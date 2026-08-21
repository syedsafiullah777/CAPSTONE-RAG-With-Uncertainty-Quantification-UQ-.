"""Embedding model loader for the knowledge base."""

from __future__ import annotations

from functools import lru_cache
from typing import Any


@lru_cache(maxsize=2)
def get_embedding_model(model_name: str = "BAAI/bge-small-en-v1.5") -> Any:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Install sentence-transformers: pip install sentence-transformers"
        ) from exc
    return SentenceTransformer(model_name)


def embed_texts(
    texts: list[str],
    *,
    model_name: str = "BAAI/bge-small-en-v1.5",
    batch_size: int = 32,
) -> list[list[float]]:
    model = get_embedding_model(model_name)
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=len(texts) > 64,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return [vector.tolist() for vector in vectors]
