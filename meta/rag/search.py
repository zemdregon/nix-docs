#!/usr/bin/env python3
"""Semantic search over the local Chroma wiki index."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DEFAULT_TOP_K
from ollama_client import embed_query
from store import get_collection, open_client, query_embeddings


def search(query: str, *, k: int = DEFAULT_TOP_K) -> list[dict]:
    collection = get_collection(open_client())
    if collection.count() == 0:
        raise SystemExit("Index is empty. Run: python meta/rag/ingest.py --reset")

    embedding = embed_query(query)
    result = query_embeddings(collection, embedding, n_results=k)

    hits: list[dict] = []
    ids = (result.get("ids") or [[]])[0]
    docs = (result.get("documents") or [[]])[0]
    metas = (result.get("metadatas") or [[]])[0]
    dists = (result.get("distances") or [[]])[0]

    for i, doc_id in enumerate(ids):
        dist = dists[i] if i < len(dists) else None
        # Cosine distance in Chroma: lower is better. Convert to a rough score.
        score = (1.0 - float(dist)) if dist is not None else None
        meta = metas[i] if i < len(metas) else {}
        doc = docs[i] if i < len(docs) else ""
        hits.append(
            {
                "id": doc_id,
                "score": score,
                "distance": dist,
                "path": meta.get("path", ""),
                "title": meta.get("title", ""),
                "heading": meta.get("heading", ""),
                "status": meta.get("status", ""),
                "excerpt": _excerpt(doc),
            }
        )
    return hits


def _excerpt(doc: str, limit: int = 360) -> str:
    # Drop the Path/Heading grounding prefix for display when present.
    body = doc
    marker = "\n\n"
    if doc.startswith("Path:") and marker in doc:
        body = doc.split(marker, 1)[1]
    body = " ".join(body.split())
    if len(body) <= limit:
        return body
    return body[: limit - 1] + "…"


def format_hits(hits: list[dict]) -> str:
    lines: list[str] = []
    for i, h in enumerate(hits, start=1):
        score = f"{h['score']:.3f}" if h["score"] is not None else "?"
        lines.append(
            f"{i}. score={score}  {h['path']}  ·  {h['heading']}"
        )
        if h.get("title") and h["title"] != h["heading"]:
            lines.append(f"   title: {h['title']}")
        lines.append(f"   {h['excerpt']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Natural-language search query")
    parser.add_argument("-k", type=int, default=DEFAULT_TOP_K, help="Top-k results")
    args = parser.parse_args()
    hits = search(args.query, k=args.k)
    if not hits:
        print("No hits.", file=sys.stderr)
        return 1
    sys.stdout.write(format_hits(hits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
