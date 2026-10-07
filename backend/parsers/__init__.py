"""Диспетчер парсеров: parse_source(type, payload) → list[dict]."""
import asyncio
import logging
from typing import Any

from backend.parsers.file_parser import parse_file
from backend.parsers.url_parser import parse_url
from backend.parsers.vk_parser import parse_vk
from backend.parsers.raw_parser import parse_raw

logger = logging.getLogger(__name__)


async def parse_source(source_type: str, payload: dict[str, Any]) -> list[dict]:
    """
    Распарсить источник по типу.
    Все CPU-bound парсеры обёрнуты в asyncio.to_thread.
    """
    logger.info("Parsing source: type=%s", source_type)

    match source_type:
        case "file":
            path = payload.get("path")
            if not path:
                raise ValueError("Missing 'path' in payload for file source")
            return await asyncio.to_thread(parse_file, path)

        case "url":
            url = payload.get("url")
            if not url:
                raise ValueError("Missing 'url' in payload for url source")
            return await parse_url(url)

        case "vk":
            group = payload.get("group")
            if not group:
                raise ValueError("Missing 'group' in payload for vk source")
            count = payload.get("count", 100)
            token = payload.get("token")
            return await parse_vk(group, count=count, token=token)

        case "raw":
            text = payload.get("text")
            if not text:
                raise ValueError("Missing 'text' in payload for raw source")
            title = payload.get("title", "")
            return await asyncio.to_thread(parse_raw, text, title)

        case _:
            raise ValueError(f"Unknown source type: {source_type}")
