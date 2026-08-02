"""Chroma persistent store helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from config import CHROMA_DIR, COLLECTION_NAME, EMBED_DIM


def open_client(persist_dir: Path | None = None) -> chromadb.PersistentClient:
    path = persist_dir or CHROMA_DIR
    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(path))


def get_collection(
    client: chromadb.PersistentClient | None = None,
    *,
    reset: bool = False,
) -> Collection:
    client = client or open_client()
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embed_dim": EMBED_DIM},
    )


def upsert_chunks(
    collection: Collection,
    *,
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict[str, Any]],
) -> None:
    if not ids:
        return
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def delete_by_path(collection: Collection, path: str) -> None:
    try:
        collection.delete(where={"path": path})
    except Exception:
        # Empty collection / no matches — fine.
        pass


def query_embeddings(
    collection: Collection,
    embedding: list[float],
    *,
    n_results: int = 8,
) -> dict[str, Any]:
    return collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
