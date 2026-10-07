"""Роуты: /api/sources/*."""
import hashlib
import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db import get_session
from backend.models import Source, Document, Chunk
from backend.schemas import (
    SourceCreate,
    SourceOut,
    SourceDetailOut,
    SourceAddResponse,
    DocumentOut,
    DeleteResponse,
    ReindexResponse,
)
from backend.parsers import parse_source
from backend.chunker import chunk_text
from backend.config import UPLOADS_DIR, CHUNK_MIN_TOKENS, CHUNK_MAX_TOKENS, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sources")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source_to_out(source: Source) -> SourceOut:
    doc_count = len(source.documents) if source.documents else 0
    chunk_count = sum(len(d.chunks) for d in source.documents) if source.documents else 0
    return SourceOut(
        id=source.id,
        type=source.type,
        name=source.name,
        url=source.url,
        file_path=source.file_path,
        meta=source.meta or {},
        created_at=source.created_at,
        last_sync_at=source.last_sync_at,
        document_count=doc_count,
        chunk_count=chunk_count,
    )


@router.post("/add", response_model=SourceAddResponse)
async def add_source(
    body: SourceCreate,
    session: AsyncSession = Depends(get_session),
) -> SourceAddResponse:
    """Добавить источник: распарсить, дедуплицировать, чанкировать."""
    warnings: list[str] = []

    # 1. Парсим
    try:
        raw_docs = await parse_source(body.type, body.payload)
    except Exception as e:
        logger.error("Parse failed: %s", e)
        raise HTTPException(status_code=422, detail=f"Parse error: {e}")

    if not raw_docs:
        raise HTTPException(status_code=422, detail="No documents extracted from source")

    # 2. Определяем имя источника
    name = body.payload.get("title", "")
    if not name:
        if body.type == "file":
            name = Path(body.payload.get("path", "")).name
        elif body.type == "url":
            name = body.payload.get("url", "")
        elif body.type == "vk":
            name = f"VK: {body.payload.get('group', '')}"
        elif body.type == "raw":
            name = "Raw text"
        else:
            name = f"Source {body.type}"

    # 3. Создаём Source
    source = Source(
        type=body.type,
        name=name,
        url=body.payload.get("url"),
        file_path=body.payload.get("path"),
        meta=body.payload.get("meta", {}),
        last_sync_at=datetime.utcnow(),
    )
    session.add(source)
    await session.flush()

    # 4. Для каждого документа — дедупликация + создание
    total_chunks = 0
    docs_added = 0

    for raw_doc in raw_docs:
        text = raw_doc.get("text", "").strip()
        if not text:
            warnings.append(f"Empty text in document: {raw_doc.get('title', '?')}")
            continue

        text_hash = _sha256(text)

        # Дедупликация: проверяем, есть ли уже такой текст
        existing = (
            await session.execute(
                select(Document).where(Document.text_hash == text_hash)
            )
        ).scalar_one_or_none()

        if existing:
            logger.info("Duplicate document skipped (hash=%s)", text_hash[:12])
            warnings.append(f"Duplicate skipped: {raw_doc.get('title', '?')}")
            continue

        # Создаём документ
        doc = Document(
            source_id=source.id,
            title=raw_doc.get("title"),
            url=raw_doc.get("url"),
            date=raw_doc.get("date"),
            text=text,
            text_hash=text_hash,
            meta=raw_doc.get("meta", {}),
        )
        session.add(doc)
        await session.flush()

        # 5. Чанкируем
        chunks_data = chunk_text(
            text,
            min_tokens=CHUNK_MIN_TOKENS,
            max_tokens=CHUNK_MAX_TOKENS,
            overlap=CHUNK_OVERLAP,
        )

        for cd in chunks_data:
            chunk = Chunk(
                document_id=doc.id,
                chunk_index=cd["chunk_index"],
                text=cd["text"],
                token_count=cd["token_count"],
                char_start=cd["char_start"],
                char_end=cd["char_end"],
            )
            session.add(chunk)
            total_chunks += 1

        docs_added += 1

    await session.commit()

    logger.info(
        "Source added: id=%d, docs=%d, chunks=%d",
        source.id, docs_added, total_chunks,
    )

    return SourceAddResponse(
        source_id=source.id,
        documents=docs_added,
        chunks=total_chunks,
        warnings=warnings,
    )


@router.post("/upload", response_model=SourceAddResponse)
async def upload_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> SourceAddResponse:
    """Загрузить файл и добавить как источник."""
    # Сохраняем файл
    ext = Path(file.filename or "file.txt").suffix
    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = UPLOADS_DIR / safe_name

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Создаём payload для file-парсера
    body = SourceCreate(
        type="file",
        payload={"path": str(file_path), "title": file.filename},
    )

    return await add_source(body, session)


@router.get("/list", response_model=list[SourceOut])
async def list_sources(
    session: AsyncSession = Depends(get_session),
) -> list[SourceOut]:
    """Список всех источников."""
    result = await session.execute(
        select(Source).options(selectinload(Source.documents)).order_by(Source.created_at.desc())
    )
    sources = result.scalars().all()
    return [_source_to_out(s) for s in sources]


@router.get("/{source_id}", response_model=SourceDetailOut)
async def get_source(
    source_id: int,
    session: AsyncSession = Depends(get_session),
) -> SourceDetailOut:
    """Детали источника с документами."""
    result = await session.execute(
        select(Source)
        .options(selectinload(Source.documents).selectinload(Document.chunks))
        .where(Source.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    return SourceDetailOut(
        id=source.id,
        type=source.type,
        name=source.name,
        url=source.url,
        file_path=source.file_path,
        meta=source.meta or {},
        created_at=source.created_at,
        last_sync_at=source.last_sync_at,
        documents=[
            DocumentOut(
                id=d.id,
                title=d.title,
                url=d.url,
                date=d.date,
                text=d.text,
                text_hash=d.text_hash,
                meta=d.meta or {},
                chunks=d.chunks or [],
            )
            for d in source.documents
        ],
    )


@router.delete("/{source_id}", response_model=DeleteResponse)
async def delete_source(
    source_id: int,
    session: AsyncSession = Depends(get_session),
) -> DeleteResponse:
    """Удалить источник каскадно (документы и чанки)."""
    result = await session.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    await session.delete(source)
    await session.commit()

    logger.info("Source deleted: id=%d", source_id)
    return DeleteResponse(deleted=True)


@router.post("/reindex", response_model=ReindexResponse)
async def reindex(
    source_id: int | None = None,
    session: AsyncSession = Depends(get_session),
) -> ReindexResponse:
    """Пересобрать чанки для источника (или всех)."""
    if source_id:
        result = await session.execute(
            select(Source)
            .options(selectinload(Source.documents))
            .where(Source.id == source_id)
        )
        sources = [result.scalar_one_or_none()]
        if not sources[0]:
            raise HTTPException(status_code=404, detail="Source not found")
    else:
        result = await session.execute(
            select(Source).options(selectinload(Source.documents))
        )
        sources = list(result.scalars().all())

    reindexed = 0

    for source in sources:
        if not source:
            continue
        for doc in source.documents:
            # Удаляем старые чанки
            await session.execute(
                delete(Chunk).where(Chunk.document_id == doc.id)
            )

            # Создаём новые
            chunks_data = chunk_text(
                doc.text,
                min_tokens=CHUNK_MIN_TOKENS,
                max_tokens=CHUNK_MAX_TOKENS,
                overlap=CHUNK_OVERLAP,
            )

            for cd in chunks_data:
                chunk = Chunk(
                    document_id=doc.id,
                    chunk_index=cd["chunk_index"],
                    text=cd["text"],
                    token_count=cd["token_count"],
                    char_start=cd["char_start"],
                    char_end=cd["char_end"],
                )
                session.add(chunk)
                reindexed += 1

        source.last_sync_at = datetime.utcnow()

    await session.commit()
    logger.info("Reindexed %d chunks", reindexed)
    return ReindexResponse(reindexed=reindexed)
