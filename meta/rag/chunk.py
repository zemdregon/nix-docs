"""Heading-aware Markdown chunker for wiki leaves."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from config import (
    CHUNK_HARD_MAX_CHARS,
    CHUNK_OVERLAP_CHARS,
    CHUNK_TARGET_CHARS,
    REPO_ROOT,
    SKIP_DIR_NAMES,
)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
STATUS_RE = re.compile(r"^status:\s*(\S+)", re.MULTILINE)
SLUG_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class Chunk:
    id: str
    path: str
    title: str
    heading: str
    status: str
    text: str
    index: int


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = SLUG_RE.sub("-", s).strip("-")
    return s or "section"


def parse_frontmatter(raw: str) -> tuple[str, str]:
    """Return (status, body_without_frontmatter)."""
    m = FRONTMATTER_RE.match(raw)
    if not m:
        return "", raw
    status_m = STATUS_RE.search(m.group(1))
    status = status_m.group(1) if status_m else ""
    return status, raw[m.end() :]


def document_title(body: str, relpath: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return Path(relpath).stem.replace("-", " ")


def soft_split(text: str) -> list[str]:
    """Split oversized text on paragraph boundaries with overlap."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= CHUNK_TARGET_CHARS:
        return [text]

    paras = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    buf = ""

    def flush() -> None:
        nonlocal buf
        if buf.strip():
            chunks.append(buf.strip())
        buf = ""

    for para in paras:
        para = para.strip()
        if not para:
            continue
        candidate = f"{buf}\n\n{para}".strip() if buf else para
        if len(candidate) <= CHUNK_TARGET_CHARS:
            buf = candidate
            continue
        if buf:
            flush()
            # Overlap: keep a tail of the previous chunk when continuing.
            if chunks and CHUNK_OVERLAP_CHARS > 0:
                tail = chunks[-1][-CHUNK_OVERLAP_CHARS:]
                buf = f"{tail}\n\n{para}".strip()
            else:
                buf = para
        else:
            # Single paragraph longer than target — hard-split.
            start = 0
            while start < len(para):
                end = min(start + CHUNK_HARD_MAX_CHARS, len(para))
                piece = para[start:end].strip()
                if piece:
                    chunks.append(piece)
                if end >= len(para):
                    break
                start = max(end - CHUNK_OVERLAP_CHARS, start + 1)
            buf = ""

    flush()
    return chunks


def chunk_markdown(relpath: str, raw: str) -> list[Chunk]:
    status, body = parse_frontmatter(raw)
    title = document_title(body, relpath)
    matches = list(HEADING_RE.finditer(body))

    sections: list[tuple[str, str]] = []
    if not matches:
        sections.append((title, body.strip()))
    else:
        # Prolog before first heading.
        if matches[0].start() > 0:
            prolog = body[: matches[0].start()].strip()
            if prolog:
                sections.append((title, prolog))
        for i, m in enumerate(matches):
            heading = m.group(2).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            section_body = body[start:end].strip()
            # Include the heading line in the embedded text for grounding.
            block = f"{m.group(0).strip()}\n\n{section_body}".strip()
            sections.append((heading, block))

    out: list[Chunk] = []
    global_i = 0
    for section_i, (heading, block) in enumerate(sections):
        parts = soft_split(block)
        hslug = slugify(heading)
        for part_i, part in enumerate(parts):
            grounded = f"Path: {relpath}\nHeading: {heading}\n\n{part}"
            # Include section ordinal so duplicate heading slugs cannot collide.
            cid = f"{relpath}#{section_i}-{hslug}#{part_i}"
            out.append(
                Chunk(
                    id=cid,
                    path=relpath,
                    title=title,
                    heading=heading,
                    status=status,
                    text=grounded,
                    index=global_i,
                )
            )
            global_i += 1
    return out


def iter_markdown_files(root: Path | None = None) -> list[Path]:
    root = root or REPO_ROOT
    files: list[Path] = []
    for path in root.rglob("*.md"):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIR_NAMES for part in rel_parts):
            continue
        # Skip this tooling directory's README only if under .chroma (already skipped).
        files.append(path)
    files.sort()
    return files


def chunk_file(path: Path, root: Path | None = None) -> list[Chunk]:
    root = root or REPO_ROOT
    rel = path.relative_to(root).as_posix()
    raw = path.read_text(encoding="utf-8")
    return chunk_markdown(rel, raw)
