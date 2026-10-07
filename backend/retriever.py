"""Гибридный ретривер: BM25 + FAISS + RRF."""
import logging
import pickle
from pathlib import Path

import numpy as np

from backend.models import Chunk

logger = logging.getLogger(__name__)

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None
    logger.warning("rank_bm25 not installed, BM25 disabled")

try:
    import faiss
except ImportError:
    faiss = None
    logger.warning("faiss not installed, FAISS disabled")


def _tokenize(text: str) -> list[str]:
    """Токенизация для BM25."""
    import re
    return re.findall(r'\w+', text.lower())


class HybridRetriever:
    """
    Гибридный ретривер: BM25 + FAISS + RRF.
    """

    def __init__(self):
        self.chunks: list[Chunk] = []
        self.bm25: BM25Okapi | None = None
        self.faiss_index = None
        self.chunk_ids: list[int] = []
        self.tokenized_corpus: list[list[str]] = []

    def build(self, chunks: list[Chunk], embeddings: np.ndarray | None = None) -> None:
        """
        Построить индексы из списка чанков.
        chunks: список ORM Chunk объектов
        embeddings: numpy array shape (N, dim) или None
        """
        self.chunks = chunks
        self.chunk_ids = [c.id for c in chunks]

        # BM25
        if BM25Okapi is not None and chunks:
            self.tokenized_corpus = [_tokenize(c.text) for c in chunks]
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            logger.info("BM25 built: %d documents", len(chunks))
        else:
            self.bm25 = None

        # FAISS
        if faiss is not None and embeddings is not None and len(embeddings) > 0:
            dim = embeddings.shape[1]
            # IndexFlatIP — inner product на нормализованных = cosine
            self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(embeddings.astype(np.float32))
            logger.info("FAISS built: %d vectors, dim=%d", len(embeddings), dim)
        else:
            self.faiss_index = None

    def search(
        self,
        query_vec: np.ndarray | None,
        query_text: str,
        top_k: int = 20,
    ) -> list[tuple[int, float, str]]:
        """
        Гибридный поиск: BM25 + FAISS + RRF.
        Возвращает: [(chunk_id, score, method), ...]
        """
        if not self.chunks:
            return []

        bm25_results: list[tuple[int, float]] = []
        faiss_results: list[tuple[int, float]] = []

        # BM25 поиск
        if self.bm25 is not None:
            tokenized_query = _tokenize(query_text)
            scores = self.bm25.get_scores(tokenized_query)
            # Топ-K по BM25
            top_indices = np.argsort(scores)[::-1][:top_k]
            for idx in top_indices:
                if scores[idx] > 0:
                    bm25_results.append((self.chunk_ids[idx], float(scores[idx])))

        # FAISS поиск
        if self.faiss_index is not None and query_vec is not None and len(query_vec) > 0:
            query_vec_2d = query_vec.reshape(1, -1).astype(np.float32)
            k = min(top_k, self.faiss_index.ntotal)
            if k > 0:
                scores, indices = self.faiss_index.search(query_vec_2d, k)
                for score, idx in zip(scores[0], indices[0]):
                    if idx >= 0 and idx < len(self.chunk_ids):
                        faiss_results.append((self.chunk_ids[idx], float(score)))

        # RRF (Reciprocal Rank Fusion)
        k_rrf = 60
        combined_scores: dict[int, float] = {}
        method_map: dict[int, str] = {}

        # BM25 ранги
        for rank, (chunk_id, _) in enumerate(bm25_results):
            combined_scores[chunk_id] = combined_scores.get(chunk_id, 0.0) + 1.0 / (k_rrf + rank + 1)
            method_map[chunk_id] = "bm25"

        # FAISS ранги
        for rank, (chunk_id, _) in enumerate(faiss_results):
            combined_scores[chunk_id] = combined_scores.get(chunk_id, 0.0) + 1.0 / (k_rrf + rank + 1)
            if chunk_id in method_map:
                method_map[chunk_id] = "hybrid"
            else:
                method_map[chunk_id] = "faiss"

        # Сортируем по RRF score
        sorted_chunks = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        results: list[tuple[int, float, str]] = []
        for chunk_id, score in sorted_chunks[:top_k]:
            results.append((chunk_id, score, method_map.get(chunk_id, "hybrid")))

        logger.info(
            "Hybrid search: bm25=%d, faiss=%d, combined=%d",
            len(bm25_results),
            len(faiss_results),
            len(results),
        )
        return results

    def save(self, path: Path) -> None:
        """Сохранить индексы в файл."""
        data = {
            "chunk_ids": self.chunk_ids,
            "bm25": self.bm25,
            "tokenized_corpus": self.tokenized_corpus,
        }
        with open(path / "retriever.pkl", "wb") as f:
            pickle.dump(data, f)

        # FAISS сохраняем отдельно
        if self.faiss_index is not None and faiss is not None:
            faiss.write_index(self.faiss_index, str(path / "faiss.index"))

        logger.info("Retriever saved to %s", path)

    @classmethod
    def load(cls, path: Path) -> "HybridRetriever":
        """Загрузить индексы из файла."""
        retriever = cls()

        pkl_path = path / "retriever.pkl"
        if pkl_path.exists():
            with open(pkl_path, "rb") as f:
                data = pickle.load(f)
            retriever.chunk_ids = data.get("chunk_ids", [])
            retriever.bm25 = data.get("bm25")
            retriever.tokenized_corpus = data.get("tokenized_corpus", [])
            logger.info("Retriever loaded: %d chunks", len(retriever.chunk_ids))

        faiss_path = path / "faiss.index"
        if faiss_path.exists() and faiss is not None:
            retriever.faiss_index = faiss.read_index(str(faiss_path))
            logger.info("FAISS index loaded: %d vectors", retriever.faiss_index.ntotal)

        return retriever
