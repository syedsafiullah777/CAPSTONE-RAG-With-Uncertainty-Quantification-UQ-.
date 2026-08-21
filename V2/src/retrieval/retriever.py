"""Query the persistent knowledge-base index."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.retrieval.embeddings import embed_texts
from src.retrieval.index import COLLECTION_NAME, load_collection


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    score: float
    doc_id: str
    file_name: str
    split: str
    page: int | str
    company_symbol: str
    report_year: str
    role: str
    context_id: str
    source_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _distance_to_similarity(distance: float | None) -> float:
    if distance is None:
        return 0.0
    # Chroma cosine space returns distance; convert to a bounded similarity-like score.
    return max(0.0, 1.0 - float(distance))


def retrieve(
    question: str,
    *,
    persist_dir: Path,
    top_k: int = 4,
    embedding_model: str = "BAAI/bge-small-en-v1.5",
    collection_name: str = COLLECTION_NAME,
) -> list[RetrievedChunk]:
    if not question or not question.strip():
        raise ValueError("question must be non-empty")

    collection = load_collection(persist_dir, collection_name=collection_name)
    query_vec = embed_texts([question], model_name=embedding_model)[0]
    result = collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]
    ids = (result.get("ids") or [[]])[0]

    chunks: list[RetrievedChunk] = []
    for i, text in enumerate(documents):
        meta = metadatas[i] if i < len(metadatas) else {}
        distance = distances[i] if i < len(distances) else None
        chunk_id = ids[i] if i < len(ids) else str(meta.get("chunk_id") or f"idx_{i}")
        chunks.append(
            RetrievedChunk(
                chunk_id=str(chunk_id),
                text=str(text or ""),
                score=_distance_to_similarity(distance),
                doc_id=str(meta.get("doc_id") or ""),
                file_name=str(meta.get("file_name") or ""),
                split=str(meta.get("split") or ""),
                page=meta.get("page", ""),
                company_symbol=str(meta.get("company_symbol") or ""),
                report_year=str(meta.get("report_year") or ""),
                role=str(meta.get("role") or ""),
                context_id=str(meta.get("context_id") or ""),
                source_type=str(meta.get("source_type") or ""),
            )
        )
    return chunks
