"""Парсер сырого текста."""
import logging

logger = logging.getLogger(__name__)


def parse_raw(text: str, title: str = "") -> list[dict]:
    """
    Простая вставка текста вручную.
    Возвращает 1 документ.
    """
    text = text.strip()
    if not text:
        raise ValueError("Empty text provided")

    logger.info("Parsing raw text: %d chars", len(text))

    return [{
        "title": title or "Raw text",
        "text": text,
        "date": None,
        "meta": {"format": "raw"},
    }]
