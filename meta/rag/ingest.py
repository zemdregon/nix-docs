#!/usr/bin/env python3
"""Walk the wiki, chunk Markdown, embed with Ollama, upsert into Chroma."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Line-buffer progress when redirected to a log.
try:
    sys.stderr.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
except Exception:
    pass

# Allow `python meta/rag/ingest.py` from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chunk import chunk_file, iter_markdown_files
from config import EMBED_BATCH_SIZE, EMBED_MODEL, REPO_ROOT
from ollama_client import embed_texts
from store import delete_by_path, get_collection, open_client, upsert_chunks


def batched(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def ingest(*, reset: bool = False, root: Path | None = None) -> int:
    root = root or REPO_ROOT
    files = iter_markdown_files(root)
    client = open_client()
    collection = get_collection(client, reset=reset)

    total_chunks = 0
    print(f"Indexing {len(files)} Markdown files from {root}", file=sys.stderr)
    print(f"Embed model: {EMBED_MODEL}", file=sys.stderr)

    for fi, path in enumerate(files, start=1):
        rel = path.relative_to(root).as_posix()
        chunks = chunk_file(path, root)
        if not reset:
            delete_by_path(collection, rel)
        if not chunks:
            print(f"[{fi}/{len(files)}] {rel}: 0 chunks", file=sys.stderr)
            continue

        for batch in batched(chunks, EMBED_BATCH_SIZE):
            texts = [c.text for c in batch]
            embeddings = embed_texts(texts)
            upsert_chunks(
                collection,
                ids=[c.id for c in batch],
                documents=texts,
                embeddings=embeddings,
                metadatas=[
                    {
                        "path": c.path,
                        "title": c.title,
                        "heading": c.heading,
                        "status": c.status or "",
                        "index": c.index,
                    }
                    for c in batch
                ],
            )
            total_chunks += len(batch)

        print(
            f"[{fi}/{len(files)}] {rel}: {len(chunks)} chunks "
            f"(running total {total_chunks})",
            file=sys.stderr,
        )

    count = collection.count()
    print(f"Done. Collection count={count} (upserted this run: {total_chunks})", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the Chroma collection before indexing",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repo root to index (default: nix-docs root)",
    )
    args = parser.parse_args()
    return ingest(reset=args.reset, root=args.root)


if __name__ == "__main__":
    raise SystemExit(main())
