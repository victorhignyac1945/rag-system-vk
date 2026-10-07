"""Эмбеддинг текстов через Ollama /api/embed."""
import logging
import numpy as np
import httpx

from backend.config import OLLAMA_URL, EMBED_MODEL, EMBED_BATCH_SIZE

logger = logging.getLogger(__name__)


async def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Получить эмбеддинги для списка текстов.
    Батчами по EMBED_BATCH_SIZE, через Ollama /api/embed.
    L2-нормализация, np.float32.
    """
    if not texts:
        return np.array([], dtype=np.float32)

    all_embeddings: list[list[float]] = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[i : i + EMBED_BATCH_SIZE]
            try:
                response = await client.post(
                    f"{OLLAMA_URL}/api/embed",
                    json={
                        "model": EMBED_MODEL,
                        "input": batch,
                    },
                )
                response.raise_for_status()
                data = response.json()
                embeddings = data.get("embeddings", [])
                all_embeddings.extend(embeddings)
            except Exception as e:
                logger.error("Embedding batch failed: %s", e)
                # Fallback: нулевые векторы
                all_embeddings.extend([[0.0] * 1024 for _ in batch])

    if not all_embeddings:
        return np.array([], dtype=np.float32)

    # Преобразуем в numpy
    embeddings_array = np.array(all_embeddings, dtype=np.float32)

    # L2-нормализация для cosine similarity через inner product
    norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)  # избегаем деления на ноль
    embeddings_array = embeddings_array / norms

    logger.info("Embedded %d texts, shape=%s", len(texts), embeddings_array.shape)
    return embeddings_array


async def embed_query(text: str) -> np.ndarray:
    """Получить эмбеддинг для одного запроса."""
    embeddings = await embed_texts([text])
    return embeddings[0] if len(embeddings) > 0 else np.array([], dtype=np.float32)
