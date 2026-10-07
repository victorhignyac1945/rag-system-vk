"""Парсер VK: wall.get через VK API."""
import asyncio
import logging
from datetime import datetime, timezone

import httpx

from backend.config import VK_SERVICE_TOKEN

logger = logging.getLogger(__name__)

VK_API_URL = "https://api.vk.com/method/wall.get"
RATE_LIMIT_DELAY = 0.34  # ~3 req/sec


def _normalize_group(group: str) -> str:
    """
    Нормализовать идентификатор группы/сообщества.
    Принимает: 'lua_dev', '-1234567', 'https://vk.com/lua_dev'
    """
    group = group.strip()

    # URL
    if group.startswith("http"):
        # Извлекаем имя из URL
        parts = group.rstrip("/").split("/")
        group = parts[-1]

    # Если уже число с минусом — возвращаем
    if group.startswith("-") and group[1:].isdigit():
        return group

    # Если число без минуса — добавляем минус (community)
    if group.isdigit():
        return f"-{group}"

    # Имя сообщества — возвращаем как есть
    return group


async def parse_vk(
    group: str,
    count: int = 100,
    token: str | None = None,
) -> list[dict]:
    """
    Получить посты со стены VK.
    Возвращает список документов: {title, url, date, text, meta}
    """
    api_token = token or VK_SERVICE_TOKEN
    if not api_token:
        raise ValueError(
            "VK service token not provided. "
            "Set VK_SERVICE_TOKEN env variable or pass token parameter."
        )

    owner_id = _normalize_group(group)
    logger.info("Parsing VK wall: %s (count=%d)", owner_id, count)

    docs: list[dict] = []
    offset = 0
    per_request = min(count, 100)

    async with httpx.AsyncClient(timeout=15.0) as client:
        while offset < count:
            params = {
                "access_token": api_token,
                "v": "5.199",
                "owner_id": owner_id,
                "count": per_request,
                "offset": offset,
            }

            response = await client.get(VK_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error = data["error"]
                raise RuntimeError(
                    f"VK API error: {error.get('error_code')} — {error.get('error_msg')}"
                )

            items = data.get("response", {}).get("items", [])
            if not items:
                break

            for post in items:
                text = post.get("text", "").strip()
                if not text:
                    continue  # Пропускаем посты без текста

                post_id = post["id"]
                from_id = post.get("from_id", owner_id)
                ts = post.get("date", 0)
                date_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else None

                url = f"https://vk.com/wall{from_id}_{post_id}"

                meta = {
                    "likes": post.get("likes", {}).get("count", 0),
                    "views": post.get("views", {}).get("count", 0),
                    "comments": post.get("comments", {}).get("count", 0),
                    "reposts": post.get("reposts", {}).get("count", 0),
                }

                docs.append({
                    "title": f"Пост #{post_id}",
                    "url": url,
                    "date": date_iso,
                    "text": text,
                    "meta": meta,
                })

            offset += per_request

            if offset < count:
                await asyncio.sleep(RATE_LIMIT_DELAY)

    logger.info("Parsed %d posts from VK wall %s", len(docs), owner_id)
    return docs
