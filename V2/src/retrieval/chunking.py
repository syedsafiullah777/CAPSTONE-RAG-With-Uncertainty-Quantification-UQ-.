"""Simple character chunking for KB indexing."""

from __future__ import annotations

from typing import Any


def split_text(text: str, chunk_size: int = 900, chunk_overlap: int = 150) -> list[str]:
    """Sliding-window character chunks with overlap."""
    text = " ".join(str(text).split())
    if not text:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    step = chunk_size - chunk_overlap
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += step
    return chunks


def chunk_pages(
    pages: list[dict[str, Any]],
    *,
    chunk_size: int = 900,
    chunk_overlap: int = 150,
    base_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Chunk page texts; each chunk carries provenance metadata."""
    base_metadata = base_metadata or {}
    chunks: list[dict[str, Any]] = []
    for page in pages:
        pieces = split_text(page["text"], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for idx, piece in enumerate(pieces):
            meta = {
                **base_metadata,
                "page": int(page.get("page") or 1),
                "local_path": str(page.get("local_path") or ""),
                "chunk_index": idx,
                "source_type": "pdf",
            }
            chunks.append({"text": piece, "metadata": meta})
    return chunks
