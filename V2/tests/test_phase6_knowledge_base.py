"""Phase 6 tests: chunking and knowledge-base artefacts."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import project_root
from src.retrieval.chunking import chunk_pages, split_text


def test_split_text_overlap_and_bounds() -> None:
    text = "abcdefghij" * 50  # 500 chars
    chunks = split_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) >= 5
    assert all(len(c) <= 100 for c in chunks)
    assert chunks[0].startswith("abcd")


def test_chunk_pages_adds_provenance() -> None:
    pages = [{"text": "hello world " * 100, "page": 2, "local_path": "/tmp/x.pdf"}]
    chunks = chunk_pages(
        pages,
        chunk_size=80,
        chunk_overlap=10,
        base_metadata={"file_name": "pdf/A/1/page_1.pdf", "source_type": "pdf"},
    )
    assert chunks
    assert chunks[0]["metadata"]["page"] == 2
    assert chunks[0]["metadata"]["source_type"] == "pdf"
    assert chunks[0]["metadata"]["file_name"] == "pdf/A/1/page_1.pdf"


def test_phase6_index_manifest_and_demo() -> None:
    root = project_root()
    manifest_path = root / "knowledge_base" / "index" / "index_manifest.json"
    demo_path = root / "knowledge_base" / "index" / "retrieval_demo.json"
    assert manifest_path.is_file(), "Run: PYTHONPATH=. python scripts/build_index.py"
    assert demo_path.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["phase"] == 6
    assert manifest["embedding_model"] == "BAAI/bge-small-en-v1.5"
    assert manifest["vector_store"] == "chroma"
    assert manifest["docs_indexed"] > 0
    assert manifest["chunks"] > 0
    assert "Gold context fields are not ingested" in manifest["note"]

    demo = json.loads(demo_path.read_text(encoding="utf-8"))
    assert demo["query"]
    assert len(demo["hits"]) > 0
    hit = demo["hits"][0]
    assert hit["source_type"] == "pdf"
    assert hit["file_name"]
    assert hit["chunk_id"]
    assert "text" in hit and hit["text"]


def test_phase6_did_not_index_gold_context_files() -> None:
    """Guardrail: documents dir should contain PDFs under split folders, not gold txt dumps named by question."""
    docs = project_root() / "knowledge_base" / "documents"
    assert docs.is_dir()
    pdfs = list(docs.rglob("*.pdf"))
    txts = list(docs.rglob("*.txt"))
    assert pdfs, "Expected downloaded source PDFs"
    # Gold-context-as-.txt pattern from V1 must not appear as the KB source.
    assert not any(p.name.startswith("finqa_") and p.suffix == ".txt" for p in txts)
