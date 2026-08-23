"""Knowledge-base index preflight checks before retrieval or RAG smoke runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.retrieval.index import COLLECTION_NAME, load_collection


class IndexPreflightError(RuntimeError):
    """Raised when the Chroma index is missing or empty despite manifest expectations."""


def read_index_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.is_file():
        raise IndexPreflightError(
            f"Index manifest not found: {manifest_path}. "
            "Rebuild the knowledge base with: "
            "PYTHONPATH=. python scripts/build_index.py --distractors 50"
        )
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IndexPreflightError(f"Invalid index manifest JSON at {manifest_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise IndexPreflightError(f"Index manifest must be a JSON object: {manifest_path}")
    return data


def validate_index_preflight(
    persist_dir: Path,
    *,
    manifest_path: Path | None = None,
    collection_name: str = COLLECTION_NAME,
) -> dict[str, Any]:
    """Ensure manifest chunk count matches the live Chroma collection.

    Fails clearly when manifest expects chunks but collection.count() is zero
    (typical GitHub-only / Colab clone before rebuild).
    """
    persist_dir = Path(persist_dir)
    manifest_file = Path(manifest_path) if manifest_path is not None else persist_dir / "index_manifest.json"
    manifest = read_index_manifest(manifest_file)
    expected = int(manifest.get("chunks") or 0)
    manifest_collection = str(manifest.get("collection_name") or collection_name)
    if manifest_collection != collection_name:
        raise IndexPreflightError(
            f"Collection name mismatch: manifest={manifest_collection!r} "
            f"configured={collection_name!r}. Check config/experiment.yaml retrieval.collection_name."
        )

    collection = load_collection(persist_dir, collection_name=collection_name)
    actual = int(collection.count())

    if expected > 0 and actual == 0:
        raise IndexPreflightError(
            "Knowledge base index is empty but index_manifest.json expects "
            f"{expected} chunks at {persist_dir}. "
            "The Chroma database is not included in GitHub. "
            "On Colab, download FinQA source PDFs and rebuild before RAG smoke:\n"
            "  PYTHONPATH=. python scripts/build_index.py --distractors 50\n"
            "Then re-run preflight or the Phase 8 smoke script."
        )

    if expected > 0 and actual < expected:
        raise IndexPreflightError(
            f"Knowledge base index is incomplete: collection.count()={actual} "
            f"but index_manifest.json expects {expected} chunks at {persist_dir}. "
            "Rebuild with: PYTHONPATH=. python scripts/build_index.py --distractors 50"
        )

    return {
        "persist_dir": str(persist_dir),
        "manifest_path": str(manifest_file),
        "collection_name": collection_name,
        "expected_chunks": expected,
        "actual_count": actual,
        "status": "PASS" if expected == 0 or actual >= expected else "FAIL",
    }
