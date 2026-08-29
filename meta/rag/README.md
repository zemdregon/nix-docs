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

## Cursor MCP

**Global** (all workspaces): `~/.cursor/mcp.json` registers **nix-docs-rag** (stdio). It still launches this repo’s [`mcp_run.sh`](mcp_run.sh) and reads `meta/rag/.chroma/`. On NixOS the command is absolute `/run/current-system/sw/bin/bash` so Cursor’s minimal `PATH` works. Embeddings are pinned to `qwen3-embedding:8b-q8_0` via `EMBED_MODEL` (must match the Chroma index).

| Tool | Purpose |
|------|---------|
| `search_wiki` | Semantic search over indexed chunks |
| `get_wiki_chunk` | Full chunk text by id |
| `ask_wiki` | Retrieve + local Ollama chat answer |
| `wiki_stats` | Index size, models, store path |

After changing MCP config: `agent mcp disable nix-docs-rag && agent mcp enable nix-docs-rag`, or reload MCP in the IDE (**Settings → Tools & MCP**). Requires Ollama running and an ingested index (`ingest.py` above).

Check: `agent mcp list` should show `nix-docs-rag: ready`; `agent mcp list-tools nix-docs-rag` lists the four tools.

Launcher: [`mcp_run.sh`](mcp_run.sh) → [`mcp_server.py`](mcp_server.py).

## What gets indexed

Wiki `*.md` leaves under the repo root, with exclusions in [`config.py`](config.py):

| Rule | Effect |
|------|--------|
| `SKIP_DIR_NAMES` | Skip `.git/`, `.github/`, `docs/`, `site/`, `assets/`, `.cursor/`, `.chroma/`, … |
| `SKIP_REL_PATHS` | Skip root process files (`AGENTS.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`) |
| `SKIP_PATH_PREFIXES` / `KEEP_PATH_PREFIXES` | Skip all of `meta/` except `meta/examples/` |
| `SKIP_STATUSES` | Skip frontmatter `status: draft` and `status: stub` |
| `MIN_CHUNK_CONTENT_CHARS` | Drop heading-only / empty sections (&lt; ~40 chars of body after the ATX heading) |

Chunks are heading-aware (ATX headings inside fenced code are ignored so shell `#` comments do not split chunks). Queries use a Qwen3 instruction prefix for retrieval.

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
| [`mcp_server.py`](mcp_server.py) | Cursor MCP server (stdio) |
| [`mcp_run.sh`](mcp_run.sh) | MCP launcher via `nix-shell` |
