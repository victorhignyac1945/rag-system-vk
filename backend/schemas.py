"""Pydantic v2 схемы для API."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


# --- Sources ---

class SourceCreate(BaseModel):
    type: str = Field(..., pattern=r"^(file|url|vk|raw)$")
    payload: dict[str, Any]


class ChunkOut(BaseModel):
    id: int
    chunk_index: int
    text: str
    token_count: int
    char_start: int
    char_end: int

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: int
    title: str | None = None
    url: str | None = None
    date: str | None = None
    text: str
    text_hash: str
    meta: dict = {}
    chunks: list[ChunkOut] = []

    model_config = {"from_attributes": True}


class SourceOut(BaseModel):
    id: int
    type: str
    name: str
    url: str | None = None
    file_path: str | None = None
    meta: dict = {}
    created_at: datetime
    last_sync_at: datetime | None = None
    document_count: int = 0
    chunk_count: int = 0

    model_config = {"from_attributes": True}


class SourceDetailOut(BaseModel):
    id: int
    type: str
    name: str
    url: str | None = None
    file_path: str | None = None
    meta: dict = {}
    created_at: datetime
    last_sync_at: datetime | None = None
    documents: list[DocumentOut] = []

    model_config = {"from_attributes": True}


class SourceAddResponse(BaseModel):
    source_id: int
    documents: int
    chunks: int
    warnings: list[str] = []


class DeleteResponse(BaseModel):
    deleted: bool


class ReindexResponse(BaseModel):
    reindexed: int


# --- Stats / Health ---

class StatsOut(BaseModel):
    chunks: int
    sources: int
    documents: int
    updated_at: datetime | None = None
    index_version: str | None = None
    index_built_at: datetime | None = None
    ollama_ok: bool = False


class HealthOut(BaseModel):
    status: str
    ollama: bool
    db: bool
