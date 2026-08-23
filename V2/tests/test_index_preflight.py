"""Tests for knowledge-base index preflight validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import project_root
from src.retrieval.index import COLLECTION_NAME, load_collection
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight


def test_preflight_passes_on_local_built_index() -> None:
    index_dir = project_root() / "knowledge_base" / "index"
    manifest = index_dir / "index_manifest.json"
    if not manifest.is_file():
        pytest.skip("Phase 6 index not built locally")
    collection = load_collection(index_dir, collection_name=COLLECTION_NAME)
    if collection.count() == 0:
        pytest.skip("Local Chroma index empty — rebuild with build_index.py")

    report = validate_index_preflight(index_dir)
    assert report["status"] == "PASS"
    assert report["actual_count"] >= report["expected_chunks"] > 0


def test_preflight_fails_on_empty_index_with_manifest(tmp_path: Path) -> None:
    persist_dir = tmp_path / "index"
    persist_dir.mkdir()
    manifest = {
        "chunks": 1239,
        "collection_name": COLLECTION_NAME,
        "vector_store": "chroma",
    }
    (persist_dir / "index_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(IndexPreflightError, match="index is empty"):
        validate_index_preflight(persist_dir)


def test_preflight_fails_when_manifest_missing(tmp_path: Path) -> None:
    persist_dir = tmp_path / "index"
    persist_dir.mkdir()
    with pytest.raises(IndexPreflightError, match="manifest not found"):
        validate_index_preflight(persist_dir)
