---
status: index
---

# Local RAG / vector search

Semantic search over this wiki using a **local Ollama** embedding model and a **gitignored Chroma** store. Not a content domain — tooling only.

## Prerequisites

1. [Ollama](https://ollama.com/) running (`ollama serve` if needed).
2. Models already pulled (tags used by [`config.py`](config.py)):

   | Role | Model tag |
   |------|-----------|
   | Embeddings | `qwen3-embedding:8b-q8_0` |
   | RAG chat (`ask.py`) | `huihui_ai/qwen3-coder-abliterated:30b-a3b-instruct-q3_K_M` |

3. Nix (for the Python env — no pip).

The vector store lives at `meta/rag/.chroma/` and is **not** committed (see root `.gitignore`).

## Enter the shell

From the repo root:

```bash
nix-shell meta/rag/shell.nix
```

If a private Nix binary cache is unreachable and evaluation stalls, force cache.nixos.org:

```bash
nix-shell meta/rag/shell.nix --option substituters 'https://cache.nixos.org'
```

Or one-shot:

```bash
nix-shell meta/rag/shell.nix --option substituters 'https://cache.nixos.org' --run 'python meta/rag/ingest.py --reset'
```

## Commands

Rebuild the index (wipe + full ingest):

```bash
nix-shell meta/rag/shell.nix --run 'python meta/rag/ingest.py --reset'
```

Re-ingest without wiping (per-file delete + upsert):

```bash
nix-shell meta/rag/shell.nix --run 'python meta/rag/ingest.py'
```

Semantic search:

```bash
nix-shell meta/rag/shell.nix --run 'python meta/rag/search.py "impermanence neededForBoot" -k 8'
```

RAG ask (retrieve + local coder):

```bash
nix-shell meta/rag/shell.nix --run 'python meta/rag/ask.py "when should I use deploy-rs vs Colmena?"'
```

## What gets indexed

All `*.md` under the repo root except `docs/`, `site/`, `.git/`, `meta/rag/.chroma/`, and other skip dirs listed in [`config.py`](config.py). Chunks are heading-aware; queries use a Qwen3 instruction prefix for retrieval.

Rebuild after large content edits. The corpus is small (~hundreds of leaves); a full `--reset` is normal.

## Layout

| File | Role |
|------|------|
| [`shell.nix`](shell.nix) | `python3` + `chromadb` + `httpx` |
| [`config.py`](config.py) | Models, paths, chunk sizes |
| [`chunk.py`](chunk.py) | Markdown chunker |
| [`ollama_client.py`](ollama_client.py) | Embed + chat HTTP |
| [`store.py`](store.py) | Chroma helpers |
| [`ingest.py`](ingest.py) | Build / refresh index |
| [`search.py`](search.py) | Ranked chunk search |
| [`ask.py`](ask.py) | Thin RAG CLI |
