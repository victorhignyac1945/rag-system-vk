"""Конфигурация приложения."""
from pathlib import Path
import os

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Директория данных
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "rag.db"
INDEX_DIR = DATA_DIR / "index"

# Создаём директории при импорте
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)

# URL базы данных (SQLite async)
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# OCR
OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "false").lower() in ("true", "1", "yes")
TESSERACT_LANG: str = os.getenv("TESSERACT_LANG", "rus+eng")

# VK API
VK_SERVICE_TOKEN: str | None = os.getenv("VK_SERVICE_TOKEN")

# CORS
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Ollama
OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Модели
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "qwen3-embedding:0.6b-q8_0")
DEFAULT_LLM: str = os.getenv("DEFAULT_LLM", "qwen3.5:9b")
RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

# Retrieval
TOP_K: int = 20          # из индексов (до rerank)
TOP_N: int = 5           # после rerank
MIN_SCORE: float = 0.25
MAX_PER_SOURCE: int = 3

# GPU
USE_GPU: bool = os.getenv("USE_GPU", "true").lower() in ("true", "1", "yes")

# Чанкинг
CHUNK_MIN_TOKENS: int = 300
CHUNK_MAX_TOKENS: int = 800
CHUNK_OVERLAP: int = 75

# Эмбеддинг
EMBED_BATCH_SIZE: int = 32
EMBED_DIM: int = 1024  # qwen3-embedding:0.6b
