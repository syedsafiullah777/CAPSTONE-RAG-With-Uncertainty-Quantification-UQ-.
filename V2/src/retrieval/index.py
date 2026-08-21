"""Build and load the persistent Chroma knowledge-base index."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from src.retrieval.chunking import chunk_pages
from src.retrieval.embeddings import embed_texts
from src.retrieval.extract import extract_pdf_pages
from src.retrieval.pdf_fetch import CorpusDoc


COLLECTION_NAME = "finqa_source_pdfs"


def _chroma_client(persist_dir: Path):
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError("Install chromadb: pip install chromadb") from exc
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def load_collection(persist_dir: Path, collection_name: str = COLLECTION_NAME):
    client = _chroma_client(persist_dir)
    return client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})


def _sanitize_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in meta.items():
        if value is None:
            clean[key] = ""
        elif isinstance(value, (str, int, float, bool)):
            clean[key] = value
        else:
            clean[key] = str(value)
    return clean


def build_knowledge_base(
    docs: list[CorpusDoc],
    local_paths: dict[str, str],
    *,
    persist_dir: Path,
    documents_dir: Path,
    chunk_size: int = 900,
    chunk_overlap: int = 150,
    embedding_model: str = "BAAI/bge-small-en-v1.5",
    collection_name: str = COLLECTION_NAME,
    reset: bool = True,
) -> dict[str, Any]:
    """Extract, chunk, embed, and persist Chroma index from downloaded PDFs."""
    client = _chroma_client(persist_dir)
    if reset:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    all_texts: list[str] = []
    all_ids: list[str] = []
    all_metas: list[dict[str, Any]] = []
    docs_indexed = 0
    docs_empty = 0
    extract_failures: list[dict[str, str]] = []

    for doc in docs:
        local = local_paths.get(doc.doc_key)
        if not local:
            extract_failures.append({"doc_key": doc.doc_key, "error": "missing_local_pdf"})
            continue
        pdf_path = Path(local)
        try:
            pages = extract_pdf_pages(pdf_path)
        except Exception as exc:  # noqa: BLE001
            extract_failures.append({"doc_key": doc.doc_key, "error": str(exc)})
            continue
        if not pages:
            docs_empty += 1
            continue

        base_meta = {
            "doc_id": doc.doc_key,
            "split": doc.split,
            "file_name": doc.file_name,
            "repo_pdf_path": doc.repo_path,
            "role": doc.role,
            "company_symbol": doc.company_symbol,
            "company_name": doc.company_name,
            "report_year": doc.report_year,
            "context_id": doc.context_id,
            "question_id": doc.question_id,
            "source_type": "pdf",
        }
        chunks = chunk_pages(
            pages,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            base_metadata=base_meta,
        )
        if not chunks:
            docs_empty += 1
            continue

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc.doc_key}::chunk_{i:04d}"
            meta = _sanitize_metadata({**chunk["metadata"], "chunk_id": chunk_id})
            all_ids.append(chunk_id)
            all_texts.append(chunk["text"])
            all_metas.append(meta)
        docs_indexed += 1

    if not all_texts:
        raise RuntimeError("No chunks produced — cannot build knowledge base")

    embeddings = embed_texts(all_texts, model_name=embedding_model)

    # Add in batches to avoid oversized requests.
    batch_size = 100
    for start in range(0, len(all_ids), batch_size):
        end = start + batch_size
        collection.add(
            ids=all_ids[start:end],
            documents=all_texts[start:end],
            embeddings=embeddings[start:end],
            metadatas=all_metas[start:end],
        )

    manifest = {
        "phase": 6,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "collection_name": collection_name,
        "persist_dir": str(persist_dir),
        "documents_dir": str(documents_dir),
        "embedding_model": embedding_model,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "vector_store": "chroma",
        "docs_requested": len(docs),
        "docs_indexed": docs_indexed,
        "docs_empty_text": docs_empty,
        "chunks": len(all_ids),
        "roles": {
            "test": sum(1 for d in docs if d.role == "test"),
            "calibration": sum(1 for d in docs if d.role == "calibration"),
            "distractor": sum(1 for d in docs if d.role == "distractor"),
        },
        "extract_failures": extract_failures,
        "note": (
            "Index is built from FinQA source page PDFs only. "
            "Gold context fields are not ingested as retrieval documents."
        ),
    }
    manifest_path = persist_dir / "index_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
