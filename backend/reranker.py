"""Reranker: BAAI/bge-reranker-v2-m3 через sentence_transformers.CrossEncoder."""
import logging
import os

import numpy as np

from backend.config import RERANKER_MODEL, USE_GPU

logger = logging.getLogger(__name__)

# Lazy-loaded model
_reranker_model = None


def _get_device() -> str:
    """Определить устройство для модели."""
    if USE_GPU:
        try:
            import torch
            if torch.cuda.is_available():
                logger.info("Using CUDA for reranker")
                return "cuda"
        except ImportError:
            pass
    logger.info("Using CPU for reranker")
    # Устанавливаем количество потоков для CPU
    try:
        import torch
        cpu_count = os.cpu_count() or 4
        torch.set_num_threads(min(cpu_count, 8))
    except ImportError:
        pass
    return "cpu"


def _load_model():
    """Lazy load модели reranker."""
    global _reranker_model
    if _reranker_model is None:
        try:
            from sentence_transformers import CrossEncoder
            device = _get_device()
            logger.info("Loading reranker model: %s on %s", RERANKER_MODEL, device)
            _reranker_model = CrossEncoder(RERANKER_MODEL, device=device)
            logger.info("Reranker model loaded successfully")
        except Exception as e:
            logger.error("Failed to load reranker model: %s", e)
            _reranker_model = None
    return _reranker_model


def rerank(
    query: str,
    texts: list[str],
    top_n: int = 5,
) -> list[tuple[int, float]]:
    """
    Реранжировать тексты по запросу.
    Возвращает: [(original_index, score), ...] отсортированные по убыванию score.
    """
    if not texts:
        return []

    model = _load_model()
    if model is None:
        # Fallback: возвращаем в исходном порядке
        logger.warning("Reranker not available, returning original order")
        return [(i, 1.0 - i * 0.01) for i in range(min(top_n, len(texts)))]

    # Формируем пары (query, text)
    pairs = [(query, text) for text in texts]

    try:
        import torch

        # Батчим по 16
        batch_size = 16
        all_scores: list[float] = []

        with torch.inference_mode():
            for i in range(0, len(pairs), batch_size):
                batch = pairs[i : i + batch_size]
                scores = model.predict(batch, batch_size=batch_size, show_progress_bar=False)
                all_scores.extend(scores.tolist() if hasattr(scores, 'tolist') else list(scores))

        # Сортируем по score
        indexed_scores = [(i, score) for i, score in enumerate(all_scores)]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        return indexed_scores[:top_n]

    except Exception as e:
        logger.error("Reranker failed: %s", e)
        return [(i, 1.0 - i * 0.01) for i in range(min(top_n, len(texts)))]
