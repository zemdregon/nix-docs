#!/usr/bin/env bash
# Launch the nix-docs-rag MCP server (stdio).
# Cursor often spawns MCP with a minimal PATH; bootstrap NixOS tool locations first.
set -euo pipefail

export PATH="/run/current-system/sw/bin:/nix/var/nix/profiles/default/bin:${PATH:-/usr/bin:/bin}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Large Qwen embedding model used for ingest + query (must match Chroma index).
export EMBED_MODEL="${EMBED_MODEL:-qwen3-embedding:8b-q8_0}"
export OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"

if command -v nix-docs-rag-mcp >/dev/null 2>&1; then
  exec nix-docs-rag-mcp "$@"
fi

find_python() {
  if [[ -n "${RAG_PYTHON:-}" && -x "${RAG_PYTHON}" ]]; then
    echo "$RAG_PYTHON"
    return
  fi
  local p
  # Prefer envs that already have the RAG deps (from a prior nix-shell).
  for p in /nix/store/*-python3-*-env/bin/python3 /run/current-system/sw/bin/python3; do
    [[ -x "$p" ]] || continue
    if "$p" -c 'import mcp, chromadb, httpx' >/dev/null 2>&1; then
      echo "$p"
      return
    fi
  done
  echo ""
}

PY="$(find_python)"
if [[ -n "$PY" ]]; then
  export PYTHONPATH="$ROOT/meta/rag${PYTHONPATH:+:$PYTHONPATH}"
  exec "$PY" "$ROOT/meta/rag/mcp_server.py"
fi

# Cursor spawns MCP with a minimal env (no NIX_PATH); pin nixpkgs explicitly.
exec nix-shell "$ROOT/meta/rag/shell.nix" \
  -I nixpkgs=flake:nixpkgs \
  --option substituters 'https://cache.nixos.org' \
  --run "python $ROOT/meta/rag/mcp_server.py"
