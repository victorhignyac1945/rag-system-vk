"""Конфигурация приложения."""
from pathlib import Path
import os

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Директория данных
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "rag.db"

# Создаём директории при импорте
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

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
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Чанкинг
CHUNK_MIN_TOKENS: int = 300
CHUNK_MAX_TOKENS: int = 800
CHUNK_OVERLAP: int = 75
