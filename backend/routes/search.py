"""Эндпоинт: POST /api/search."""
import logging
import time
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db import get_session
from backend.models import Chunk, Document, Source
from backend.state import get_state
from backend.embedder import embed_query
from backend.reranker import rerank
from backend.config import TOP_K, TOP_N, MIN_SCORE, MAX_PER_SOURCE

logger = logging.getLogger(__name__)

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)


class SourceInfo(BaseModel):
    name: str
    url: str | None = None
    type: str
    date: str | None = None


class SearchResult(BaseModel):
    chunk_id: int
    text: str
    score: float
    source: SourceInfo
    method: str  # "bm25" | "faiss" | "hybrid"


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    timing: dict[str, int]


@router.post("/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    session: AsyncSession = Depends(get_session),
) -> SearchResponse:
    """
    Гибридный поиск: BM25 + FAISS + rerank.
    """
    start_time = time.time()
    state = await get_state()

    if state.retriever is None or not state.chunks_cache:
        logger.warning("Index not built, returning empty results")
        return SearchResponse(
            query=body.query,
            results=[],
            timing={"retrieval_ms": 0, "rerank_ms": 0},
        )

    # 1. Получаем эмбеддинг запроса
    try:
        query_vec = await embed_query(body.query)
    except Exception as e:
        logger.error("Embed query failed: %s", e)
        query_vec = None

    # 2. Гибридный поиск
    retrieval_start = time.time()
    raw_results = state.retriever.search(
        query_vec=query_vec,
        query_text=body.query,
        top_k=TOP_K,
    )
    retrieval_ms = int((time.time() - retrieval_start) * 1000)

    if not raw_results:
        return SearchResponse(
            query=body.query,
            results=[],
            timing={"retrieval_ms": retrieval_ms, "rerank_ms": 0},
        )

    # 3. Реранкинг
    rerank_start = time.time()
    chunk_ids = [r[0] for r in raw_results]
    chunk_texts = []
    chunk_map: dict[int, Chunk] = {}

    for chunk in state.chunks_cache:
        if chunk.id in chunk_ids:
            chunk_texts.append(chunk.text)
            chunk_map[chunk.id] = chunk

    # Реранкинг через CrossEncoder
    reranked_indices = await asyncio_to_thread(
        rerank,
        body.query,
        chunk_texts,
        top_n=min(body.top_k, TOP_N),
    )
    rerank_ms = int((time.time() - rerank_start) * 1000)

    # 4. Формируем результаты
    results: list[SearchResult] = []
    source_counts: dict[int, int] = {}  # source_id -> count

    for orig_idx, score in reranked_indices:
        if orig_idx >= len(chunk_ids):
            continue

        chunk_id = chunk_ids[orig_idx]
        chunk = chunk_map.get(chunk_id)
        if not chunk:
            continue

        # Фильтр по MIN_SCORE
        if score < MIN_SCORE:
            continue

        # Фильтр MAX_PER_SOURCE
        doc = chunk.document
        if not doc:
            continue

        source_id = doc.source_id
        if source_counts.get(source_id, 0) >= MAX_PER_SOURCE:
            continue
        source_counts[source_id] = source_counts.get(source_id, 0) + 1

        # Загружаем source info
        source_result = await session.execute(
            select(Source).where(Source.id == source_id)
        )
        source = source_result.scalar_one_or_none()
        if not source:
            continue

        # Находим method из raw_results
        method = "hybrid"
        for r_id, _, r_method in raw_results:
            if r_id == chunk_id:
                method = r_method
                break

        results.append(
            SearchResult(
                chunk_id=chunk.id,
                text=chunk.text,
                score=score,
                source=SourceInfo(
                    name=source.name,
                    url=source.url,
                    type=source.type,
                    date=doc.date,
                ),
                method=method,
            )
        )

        if len(results) >= body.top_k:
            break

    total_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "Search completed: query=%s, results=%d, total_ms=%d",
        body.query[:50],
        len(results),
        total_ms,
    )

    return SearchResponse(
        query=body.query,
        results=results,
        timing={"retrieval_ms": retrieval_ms, "rerank_ms": rerank_ms},
    )


async def asyncio_to_thread(func, *args, **kwargs):
    """Обёртка для asyncio.to_thread."""
    import asyncio
    return await asyncio.to_thread(func, *args, **kwargs)
