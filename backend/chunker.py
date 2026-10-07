"""Чанкинг текста: разбивка на фрагменты 300–800 токенов с overlap."""
import re
import logging

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> list[str]:
    """Простая токенизация: последовательности word-символов."""
    return re.findall(r'\w+', text)


def _count_tokens(text: str) -> int:
    return len(_tokenize(text))


def chunk_text(
    text: str,
    min_tokens: int = 300,
    max_tokens: int = 800,
    overlap: int = 75,
) -> list[dict]:
    """
    Разбить текст на чанки.

    Стратегия:
    1. Токенизируем весь текст.
    2. Если текст < min_tokens — один чанк целиком.
    3. Иначе: разбиваем на окна по max_tokens с overlap.
    4. Восстанавливаем текст по позициям токенов.
    """
    text = text.strip()
    if not text:
        return []

    # Находим позиции всех токенов в тексте
    token_spans: list[tuple[int, int]] = []
    for match in re.finditer(r'\w+', text):
        token_spans.append((match.start(), match.end()))

    total_tokens = len(token_spans)

    if total_tokens <= min_tokens:
        return [{
            "text": text,
            "token_count": total_tokens,
            "char_start": 0,
            "char_end": len(text),
            "chunk_index": 0,
        }]

    # Разбиваем на чанки по max_tokens с overlap
    chunks: list[dict] = []
    pos = 0

    while pos < total_tokens:
        end = min(pos + max_tokens, total_tokens)

        # Позиции символов для этого чанка
        char_start = token_spans[pos][0]
        char_end = token_spans[end - 1][1]
        chunk_text_str = text[char_start:char_end]

        chunks.append({
            "text": chunk_text_str,
            "token_count": end - pos,
            "char_start": char_start,
            "char_end": char_end,
            "chunk_index": len(chunks),
        })

        if end >= total_tokens:
            break

        # Следующий чанк начинается с overlap
        pos = end - overlap

    # Перенумеруем
    for i, c in enumerate(chunks):
        c["chunk_index"] = i

    logger.info("Chunked %d tokens into %d chunks", total_tokens, len(chunks))
    return chunks
