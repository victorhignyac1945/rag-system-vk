"""Эндпоинт: POST /api/ask (SSE streaming)."""
import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from backend.db import get_session
from backend.models import Chunk, Document, Source
from backend.state import get_state
from backend.embedder import embed_query
from backend.reranker import rerank
from backend.generator import generate_stream, check_ollama_available
from backend.prompts import build_extractive_prompt
from backend.config import TOP_K, TOP_N, MIN_SCORE, MAX_PER_SOURCE, DEFAULT_LLM

logger = logging.getLogger(__name__)

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=50)
    model: str | None = None


async def _retrieve_chunks(
    question: str,
    top_k: int,
    session: AsyncSession,
) -> tuple[list[dict], list[dict], dict]:
    """
    Получить релевантные чанки для вопроса.
    Возвращает: (context_chunks, source_infos, timing)
    """
    state = await get_state()
    timing: dict[str, int] = {}

    if state.retriever is None or not state.chunks_cache:
        return [], [], timing

    # 1. Эмбеддинг запроса
    try:
        query_vec = await embed_query(question)
    except Exception as e:
        logger.error("Embed query failed: %s", e)
        query_vec = None

    # 2. Гибридный поиск
    retrieval_start = time.time()
    raw_results = state.retriever.search(
        query_vec=query_vec,
        query_text=question,
        top_k=TOP_K,
    )
    timing["retrieval_ms"] = int((time.time() - retrieval_start) * 1000)

    if not raw_results:
        return [], [], timing

    # 3. Реранкинг
    rerank_start = time.time()
    chunk_ids = [r[0] for r in raw_results]
    chunk_texts = []
    chunk_map: dict[int, Chunk] = {}

    for chunk in state.chunks_cache:
        if chunk.id in chunk_ids:
            chunk_texts.append(chunk.text)
            chunk_map[chunk.id] = chunk

    reranked_indices = await asyncio.to_thread(
        rerank,
        question,
        chunk_texts,
        top_n=min(top_k, TOP_N),
    )
    timing["rerank_ms"] = int((time.time() - rerank_start) * 1000)

    # 4. Формируем контекст и источники
    context_chunks: list[dict] = []
    source_infos: list[dict] = []
    source_counts: dict[int, int] = {}

    for orig_idx, score in reranked_indices:
        if orig_idx >= len(chunk_ids):
            continue

        chunk_id = chunk_ids[orig_idx]
        chunk = chunk_map.get(chunk_id)
        if not chunk:
            continue

        if score < MIN_SCORE:
            continue

        doc = chunk.document
        if not doc:
            continue

        source_id = doc.source_id
        if source_counts.get(source_id, 0) >= MAX_PER_SOURCE:
            continue
        source_counts[source_id] = source_counts.get(source_id, 0) + 1

        # Загружаем source
        source_result = await session.execute(
            select(Source).where(Source.id == source_id)
        )
        source = source_result.scalar_one_or_none()
        if not source:
            continue

        context_chunks.append({
            "text": chunk.text,
            "chunk_id": chunk.id,
            "score": score,
        })

        source_infos.append({
            "chunk_id": chunk.id,
            "text": chunk.text[:200],  # Краткая версия
            "score": score,
            "source": {
                "name": source.name,
                "url": source.url,
                "type": source.type,
                "date": doc.date,
            },
        })

        if len(context_chunks) >= top_k:
            break

    return context_chunks, source_infos, timing


async def _event_generator(
    question: str,
    top_k: int,
    model: str | None,
    session: AsyncSession,
) -> AsyncIterator[str]:
    """Генератор SSE событий."""
    start_time = time.time()

    # 1. Retrieval + rerank
    context_chunks, source_infos, timing = await _retrieve_chunks(
        question, top_k, session
    )

    # Отправляем источники
    yield json.dumps({
        "type": "sources",
        "data": source_infos,
    })

    if not context_chunks:
        # Нет релевантных чанков
        yield json.dumps({
            "type": "token",
            "data": "В предоставленных источниках нет информации.",
        })
        yield json.dumps({
            "type": "done",
            "data": {
                "timing": timing,
                "model": model or DEFAULT_LLM,
            },
        })
        return

    # 2. Проверяем доступность Ollama
    ollama_ok = await check_ollama_available()

    if not ollama_ok:
        # Fallback: extractive ответ
        logger.warning("Ollama unavailable, using extractive fallback")
        extractive_text = _build_extractive_answer(question, context_chunks)
        for char in extractive_text:
            yield json.dumps({
                "type": "token",
                "data": char,
            })
            await asyncio.sleep(0.01)  # Имитация стриминга
    else:
        # Стримим от Ollama
        generation_start = time.time()
        try:
            async for token in generate_stream(question, context_chunks, model):
                yield json.dumps({
                    "type": "token",
                    "data": token,
                })
        except Exception as e:
            logger.error("Generation stream failed: %s", e)
            yield json.dumps({
                "type": "token",
                "data": f"[Ошибка генерации: {e}]",
            })
        timing["generation_ms"] = int((time.time() - generation_start) * 1000)

    # 3. Done
    timing["total_ms"] = int((time.time() - start_time) * 1000)
    yield json.dumps({
        "type": "done",
        "data": {
            "timing": timing,
            "model": model or DEFAULT_LLM,
        },
    })


def _build_extractive_answer(question: str, chunks: list[dict]) -> str:
    """Построить extractive ответ из чанков."""
    if not chunks:
        return "В предоставленных источниках нет информации."

    # Берём первые 200 символов из каждого чанка
    parts = []
    for i, chunk in enumerate(chunks[:5], 1):
        text = chunk.get("text", "")[:200].strip()
        if text:
            parts.append(f"[{i}] {text}")

    if not parts:
        return "В предоставленных источниках нет информации."

    return "На основе предоставленных источников:\n\n" + "\n\n".join(parts)


@router.post("/ask")
async def ask(
    body: AskRequest,
    session: AsyncSession = Depends(get_session),
) -> EventSourceResponse:
    """
    RAG-ответ со стримингом (SSE).
    Сначала sources, потом токены, в конце done.
    """
    logger.info("Ask request: question=%s, top_k=%d", body.question[:50], body.top_k)

    return EventSourceResponse(
        _event_generator(body.question, body.top_k, body.model, session)
    )
