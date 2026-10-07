"""FastAPI application: lifespan, CORS, routes."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import ALLOWED_ORIGINS
from backend.db import init_db
from backend.state import get_state
from backend.routes.health import router as health_router
from backend.routes.sources import router as sources_router
from backend.routes.search import router as search_router
from backend.routes.ask import router as ask_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database ready.")

    # Инициализируем состояние индекса
    logger.info("Loading index state...")
    state = await get_state()
    if state.retriever:
        logger.info("Index loaded: %d chunks", len(state.chunks_cache))
    else:
        logger.info("No index found, will build on first source add")

    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="RAG Backend",
    description="RAG-платформа: парсеры, БД, чанкинг, поиск, генерация",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роуты
app.include_router(health_router, prefix="/api")
app.include_router(sources_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(ask_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "RAG Backend is running", "docs": "/docs"}
