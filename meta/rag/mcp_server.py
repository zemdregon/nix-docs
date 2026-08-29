#!/usr/bin/env python3
"""MCP server exposing nix-docs wiki semantic search and RAG over Chroma + Ollama."""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mcp.server.fastmcp import FastMCP

from ask import ask
from config import CHAT_MODEL, CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL, REPO_ROOT
from search import search
from store import get_collection, open_client

mcp = FastMCP(
    "nix-docs-rag",
    instructions=(
        "Semantic search over the local nix-docs wiki (Nix, NixOS, nixpkgs, flakes, "
        "Home Manager, deployment tools). Use search_wiki before inventing options, "
        "flags, or module APIs. Prefer search_wiki for factual lookups; use ask_wiki "
        "only when you need a synthesized answer with citations."
    ),
)


def _chroma_dir() -> Path:
    override = os.environ.get("NIX_DOCS_CHROMA_DIR")
    return Path(override) if override else CHROMA_DIR


@mcp.tool()
def search_wiki(
    query: str,
    top_k: int = 8,
    path_prefix: str | None = None,
    max_excerpt_chars: int = 800,
) -> str:
    """Semantic search over the nix-docs wiki vector index.

    Args:
        query: Natural-language question (e.g. "impermanence neededForBoot").
        top_k: Number of chunks to return (1–20).
        path_prefix: Optional wiki path prefix filter (e.g. "09-nixos/", "07-flakes/").
        max_excerpt_chars: Truncate each excerpt to this many characters (0 = full).
    """
    top_k = max(1, min(int(top_k), 20))
    try:
        collection = get_collection(open_client(_chroma_dir()))
        if collection.count() == 0:
            return json.dumps(
                {
                    "error": "Index is empty. Run: nix-shell meta/rag/shell.nix --run 'python meta/rag/ingest.py --reset'",
                }
            )
        hits = search(query, k=top_k)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})

    if path_prefix:
        prefix = path_prefix.strip().lstrip("/")
        hits = [h for h in hits if h.get("path", "").startswith(prefix)]

    if max_excerpt_chars and max_excerpt_chars > 0:
        for h in hits:
            excerpt = h.get("excerpt") or ""
            if len(excerpt) > max_excerpt_chars:
                h["excerpt"] = excerpt[: max_excerpt_chars - 1] + "…"

    return json.dumps(
        {
            "query": query,
            "embed_model": EMBED_MODEL,
            "count": len(hits),
            "hits": hits,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def get_wiki_chunk(chunk_id: str) -> str:
    """Fetch one wiki chunk by stable id (full text + metadata)."""
    try:
        collection = get_collection(open_client(_chroma_dir()))
        result = collection.get(
            ids=[chunk_id],
            include=["documents", "metadatas"],
        )
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})

    ids = result.get("ids") or []
    if not ids:
        return json.dumps({"error": f"Chunk not found: {chunk_id}"})

    doc = (result.get("documents") or [""])[0]
    meta = (result.get("metadatas") or [{}])[0]
    return json.dumps(
        {
            "id": chunk_id,
            "path": meta.get("path", ""),
            "title": meta.get("title", ""),
            "heading": meta.get("heading", ""),
            "status": meta.get("status", ""),
            "text": doc,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def ask_wiki(question: str, top_k: int = 8) -> str:
    """Retrieve wiki chunks and answer with the local Ollama chat model.

    Slower than search_wiki; use when you need a synthesized answer with citations.
    """
    top_k = max(1, min(int(top_k), 20))
    try:
        answer = ask(question, k=top_k, stream=False, quiet=True)
    except SystemExit as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})

    return json.dumps(
        {
            "question": question,
            "chat_model": CHAT_MODEL,
            "answer": answer,
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def wiki_stats() -> str:
    """Return index stats: chunk count, models, and Chroma store path."""
    try:
        collection = get_collection(open_client(_chroma_dir()))
        count = collection.count()
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})

    return json.dumps(
        {
            "repo_root": str(REPO_ROOT),
            "chroma_dir": str(_chroma_dir()),
            "collection": COLLECTION_NAME,
            "total_chunks": count,
            "embed_model": EMBED_MODEL,
            "chat_model": CHAT_MODEL,
        },
        indent=2,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
