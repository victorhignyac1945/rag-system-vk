"""Роуты: /api/health, /api/stats."""
import logging

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_session
from backend.models import Source, Document, Chunk
from backend.schemas import HealthOut, StatsOut
from backend.config import OLLAMA_URL
from backend.state import get_state

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthOut)
async def health(session: AsyncSession = Depends(get_session)) -> HealthOut:
    """Проверка здоровья сервиса."""
    # Проверяем БД
    db_ok = True
    try:
        await session.execute(select(func.count()).select_from(Source))
    except Exception as e:
        logger.error("DB health check failed: %s", e)
        db_ok = False

    # Проверяем Ollama
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception as e:
        logger.warning("Ollama health check failed: %s", e)

    return HealthOut(
        status="ok" if (db_ok and ollama_ok) else "degraded",
        ollama=ollama_ok,
        db=db_ok,
    )


@router.get("/stats", response_model=StatsOut)
async def stats(session: AsyncSession = Depends(get_session)) -> StatsOut:
    """Статистика индекса."""
    chunks_count = (await session.execute(select(func.count()).select_from(Chunk))).scalar() or 0
    sources_count = (await session.execute(select(func.count()).select_from(Source))).scalar() or 0
    documents_count = (await session.execute(select(func.count()).select_from(Document))).scalar() or 0

    # Последнее обновление
    last_source = (
        await session.execute(
            select(Source).order_by(Source.created_at.desc()).limit(1)
        )
    ).scalar_one_or_none()

    updated_at = last_source.created_at if last_source else None

    # Получаем состояние индекса
    state = await get_state()
    index_version = state.index_version
    index_built_at = state.index_built_at

    # Проверяем Ollama
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception as e:
        logger.warning("Ollama stats check failed: %s", e)

    return StatsOut(
        chunks=chunks_count,
        sources=sources_count,
        documents=documents_count,
        updated_at=updated_at,
        index_version=index_version,
        index_built_at=index_built_at,
        ollama_ok=ollama_ok,
    )
