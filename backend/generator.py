"""Генерация ответов через Ollama /api/chat (streaming)."""
import logging
from collections.abc import AsyncIterator

import httpx

from backend.config import OLLAMA_URL, DEFAULT_LLM
from backend.prompts import SYSTEM_RAG, build_context, build_user_prompt

logger = logging.getLogger(__name__)


async def generate_stream(
    question: str,
    context_chunks: list[dict],
    model: str | None = None,
) -> AsyncIterator[str]:
    """
    Стримить ответ от Ollama токен за токеном.
    Yield строки (токены).
    """
    model = model or DEFAULT_LLM
    context = build_context(context_chunks)
    user_prompt = build_user_prompt(question, context)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_RAG},
            {"role": "user", "content": user_prompt},
        ],
        "stream": True,
        "think": False,  # Отключаем thinking для qwen3
        "keep_alive": -1,  # Модель не выгружается
        "options": {
            "num_ctx": 4096,
            "temperature": 0.2,
        },
    }

    logger.info("Generating with model=%s, chunks=%d", model, len(context_chunks))

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            async with client.stream(
                "POST",
                f"{OLLAMA_URL}/api/chat",
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    # Парсим JSONL
                    import json
                    try:
                        chunk = json.loads(line)
                        message = chunk.get("message", {})
                        content = message.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse JSON line: %s", line[:100])
                        continue

        except httpx.HTTPStatusError as e:
            logger.error("Ollama HTTP error: %s", e)
            yield f"[Ошибка генерации: {e.response.status_code}]"
        except Exception as e:
            logger.error("Generation failed: %s", e)
            yield f"[Ошибка генерации: {e}]"


async def check_ollama_available() -> bool:
    """Проверить доступность Ollama."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            return response.status_code == 200
    except Exception:
        return False
