"""Singleton AppState: управление состоянием индекса."""
import asyncio
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.config import INDEX_DIR
from backend.db import async_session_factory
from backend.models import Source, Document, Chunk
from backend.retriever import HybridRetriever
from backend.embedder import embed_texts

logger = logging.getLogger(__name__)


class AppState:
    """Глобальное состояние приложения."""

    def __init__(self):
        self.retriever: HybridRetriever | None = None
        self.chunks_cache: list[Chunk] = []
        self.index_version: str | None = None
        self.index_built_at: datetime | None = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Инициализация при старте: загрузить индекс, если есть."""
        async with self._lock:
            # Пытаемся загрузить существующий индекс
            if (INDEX_DIR / "faiss.index").exists() or (INDEX_DIR / "retriever.pkl").exists():
                try:
                    self.retriever = HybridRetriever.load(INDEX_DIR)
                    self.index_version = datetime.utcnow().isoformat()
                    self.index_built_at = datetime.utcnow()
                    logger.info("Index loaded from disk")
                except Exception as e:
                    logger.error("Failed to load index: %s", e)
                    self.retriever = None
            else:
                logger.info("No index found, will build on first source add")


# Singleton
_state: AppState | None = None


async def get_state() -> AppState:
    """Получить singleton AppState."""
    global _state
    if _state is None:
        _state = AppState()
        await _state.initialize()
    return _state


async def rebuild_index(force: bool = False) -> int:
    """
    Перестроить индекс из всех чанков в БД.
    Возвращает количество чанков в индексе.
    """
    state = await get_state()

    async with state._lock:
        # Загружаем все чанки с документами
        async with async_session_factory() as session:
            result = await session.execute(
                select(Chunk)
                .options(selectinload(Chunk.document))
                .order_by(Chunk.id)
            )
            chunks = list(result.scalars().all())

        if not chunks:
            logger.info("No chunks to index")
            state.retriever = None
            state.chunks_cache = []
            return 0

        logger.info("Building index for %d chunks...", len(chunks))

        # Получаем эмбеддинги
        texts = [c.text for c in chunks]
        try:
            embeddings = await embed_texts(texts)
        except Exception as e:
            logger.error("Embedding failed: %s", e)
            embeddings = None

        # Строим гибридный индекс
        retriever = HybridRetriever()
        retriever.build(chunks, embeddings)

        # Сохраняем
        retriever.save(INDEX_DIR)

        # Обновляем state
        state.retriever = retriever
        state.chunks_cache = chunks
        state.index_version = datetime.utcnow().isoformat()
        state.index_built_at = datetime.utcnow()

        logger.info("Index built: %d chunks", len(chunks))
        return len(chunks)
