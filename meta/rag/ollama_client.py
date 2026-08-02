"""Thin Ollama HTTP client for embeddings and chat."""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from typing import Any

import httpx

from config import (
    CHAT_MODEL,
    EMBED_MODEL,
    OLLAMA_BASE_URL,
    QUERY_INSTRUCTION,
    REQUEST_TIMEOUT_S,
)


class OllamaError(RuntimeError):
    pass


def _client() -> httpx.Client:
    return httpx.Client(base_url=OLLAMA_BASE_URL, timeout=REQUEST_TIMEOUT_S)


def embed_texts(
    texts: list[str],
    *,
    model: str = EMBED_MODEL,
    retries: int = 3,
) -> list[list[float]]:
    if not texts:
        return []
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with _client() as client:
                resp = client.post(
                    "/api/embed",
                    json={"model": model, "input": texts},
                )
                resp.raise_for_status()
                data = resp.json()
            embeddings = data.get("embeddings")
            if not embeddings or len(embeddings) != len(texts):
                raise OllamaError(
                    f"unexpected embed response: got {0 if not embeddings else len(embeddings)} "
                    f"vectors for {len(texts)} inputs"
                )
            return embeddings
        except (httpx.HTTPError, OllamaError, KeyError, TypeError) as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise OllamaError(f"embed failed after {retries} retries: {last_err}")


def embed_query(query: str, *, model: str = EMBED_MODEL) -> list[float]:
    prompted = QUERY_INSTRUCTION.format(query=query.strip())
    return embed_texts([prompted], model=model)[0]


def chat_stream(
    messages: list[dict[str, str]],
    *,
    model: str = CHAT_MODEL,
) -> Iterator[str]:
    with _client() as client:
        with client.stream(
            "POST",
            "/api/chat",
            json={"model": model, "messages": messages, "stream": True},
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    obj: dict[str, Any] = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = obj.get("message") or {}
                content = msg.get("content")
                if content:
                    yield content
                if obj.get("done"):
                    break


def chat(
    messages: list[dict[str, str]],
    *,
    model: str = CHAT_MODEL,
) -> str:
    return "".join(chat_stream(messages, model=model))
