"""Defaults for the local Ollama + Chroma wiki index."""

from __future__ import annotations

import os
from pathlib import Path

# Repo root (…/nix-docs), two levels above this file (meta/rag/config.py).
REPO_ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = Path(__file__).resolve().parent
CHROMA_DIR = RAG_DIR / ".chroma"
COLLECTION_NAME = "nix-docs"

OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
# Large local embedder (4096-d). Override only if you rebuild the Chroma index to match.
EMBED_MODEL = os.environ.get("EMBED_MODEL", "qwen3-embedding:8b-q8_0")
CHAT_MODEL = os.environ.get(
    "CHAT_MODEL",
    "huihui_ai/qwen3-coder-abliterated:30b-a3b-instruct-q3_K_M",
)
EMBED_DIM = int(os.environ.get("EMBED_DIM", "4096"))

# Soft chunk targets (characters; wiki prose is dense but short).
CHUNK_TARGET_CHARS = 1200
CHUNK_OVERLAP_CHARS = 120
CHUNK_HARD_MAX_CHARS = 2400
# Drop heading-only / empty sections (content after Path/Heading + ATX line).
MIN_CHUNK_CONTENT_CHARS = 40

# Directories / path prefixes to skip when walking the tree (relative to REPO_ROOT).
SKIP_DIR_NAMES = {
    ".git",
    ".github",
    ".chroma",
    "docs",
    "site",
    "node_modules",
    ".cursor",
    "__pycache__",
    "assets",
}

# Repo-root process / contributor docs (not wiki leaves).
SKIP_REL_PATHS = frozenset(
    {
        "AGENTS.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
    }
)

# Skip process trees under these prefixes…
SKIP_PATH_PREFIXES = (
    "meta/",
)
# …except these keep-prefixes (checked before SKIP_PATH_PREFIXES).
KEEP_PATH_PREFIXES = (
    "meta/examples/",
)

# Frontmatter statuses excluded from the vector index (incomplete / WIP leaves).
SKIP_STATUSES = frozenset({"draft", "stub"})

QUERY_INSTRUCTION = (
    "Instruct: Given a Nix/NixOS documentation question, retrieve relevant "
    "wiki passages that answer it.\nQuery: {query}"
)

EMBED_BATCH_SIZE = 8
DEFAULT_TOP_K = 8
REQUEST_TIMEOUT_S = 300.0
