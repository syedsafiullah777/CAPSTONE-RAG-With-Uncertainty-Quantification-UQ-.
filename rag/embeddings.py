from __future__ import annotations

from config import EMBEDDING_MODEL


def get_embedding_model():
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )
