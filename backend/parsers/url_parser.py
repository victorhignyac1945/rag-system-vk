"""Парсер URL: httpx + trafilatura."""
import logging

import httpx
import trafilatura

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


async def parse_url(url: str) -> list[dict]:
    """
    Скачать URL и извлечь основной текст через trafilatura.
    Возвращает 1 документ: {title, url, text, date?, meta?}
    """
    logger.info("Parsing URL: %s", url)

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=30.0,
        headers=HEADERS,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html = response.text

    # Извлекаем текст
    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        favor_precision=True,
    )

    if not text or len(text.strip()) < 200:
        # Fallback: попробуем без favor_precision
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            favor_precision=False,
        )

    if not text or len(text.strip()) < 200:
        raise ValueError(
            f"trafilatura extracted less than 200 chars from {url}. "
            "The page may require JavaScript or be behind a paywall."
        )

    # Извлекаем title из HTML
    import re
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    page_title = title_match.group(1).strip() if title_match else url

    # Пытаемся извлечь дату
    date_match = re.search(
        r'<meta[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)',
        html,
        re.IGNORECASE,
    )
    date = date_match.group(1).strip() if date_match else None

    return [{
        "title": page_title,
        "url": url,
        "text": text.strip(),
        "date": date,
        "meta": {"format": "url", "content_length": len(text)},
    }]
