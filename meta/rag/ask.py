#!/usr/bin/env python3
"""RAG ask: retrieve wiki chunks, then answer with the local Ollama coder model."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CHAT_MODEL, DEFAULT_TOP_K
from ollama_client import chat_stream
from search import search


SYSTEM = """You are a Nix/NixOS documentation assistant for the local nix-docs wiki.
Answer using ONLY the provided wiki excerpts. Cite wiki paths in backticks.
If the excerpts are insufficient, say what is missing instead of inventing APIs or options.
Be concise and technical."""


def build_context(hits: list[dict]) -> str:
    blocks: list[str] = []
    for i, h in enumerate(hits, start=1):
        blocks.append(
            f"[{i}] path=`{h['path']}` heading={h['heading']}\n{h['excerpt']}"
        )
    return "\n\n".join(blocks)


def ask(
    question: str,
    *,
    k: int = DEFAULT_TOP_K,
    stream: bool = True,
    quiet: bool = False,
) -> str:
    hits = search(question, k=k)
    context = build_context(hits)
    user = (
        f"Question: {question}\n\n"
        f"Wiki excerpts:\n{context}\n\n"
        "Answer with citations to the paths above."
    )
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
    ]

    if not quiet:
        print(f"# model: {CHAT_MODEL}", file=sys.stderr)
        print(f"# retrieved {len(hits)} chunks", file=sys.stderr)
        for h in hits:
            score = f"{h['score']:.3f}" if h["score"] is not None else "?"
            print(f"#  - {score} {h['path']} · {h['heading']}", file=sys.stderr)
        print(file=sys.stderr)

    if not stream:
        from ollama_client import chat

        return chat(messages)

    parts: list[str] = []
    for token in chat_stream(messages):
        parts.append(token)
        sys.stdout.write(token)
        sys.stdout.flush()
    sys.stdout.write("\n")
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Question to answer from the wiki index")
    parser.add_argument("-k", type=int, default=DEFAULT_TOP_K, help="Top-k chunks")
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Buffer the full reply instead of streaming tokens",
    )
    args = parser.parse_args()
    ask(args.question, k=args.k, stream=not args.no_stream)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
