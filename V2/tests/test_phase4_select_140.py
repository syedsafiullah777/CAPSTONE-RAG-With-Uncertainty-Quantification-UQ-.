"""Phase 4 tests: stratified freeze logic and frozen artefacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from src.config import project_root
from src.data.select_140 import (
    filter_and_dedupe,
    freeze_test_140,
    normalize_question,
    stratified_sample,
)


def _row(i: int, *, question: str | None = None, company: str = "A", file_i: int | None = None) -> dict:
    fi = file_i if file_i is not None else i
    return {
        "id": f"id_{i:04d}",
        "context_id": f"ctx_{fi}",
        "split": "test",
        "question": question if question is not None else f"Question number {i}?",
        "program_answer": str(i),
        "original_answer": str(i),
        "context": "evidence " * 30,
        "table": "|a|b|",
        "pre_text": "pre",
        "post_text": "post",
        "file_name": f"pdf/{company}/2010/page_{fi}.pdf",
        "company_name": f"Company {company}",
        "company_symbol": company,
        "report_year": 2010 + (i % 3),
        "page_number": fi,
        "company_sector": "Financials",
        "company_industry": "Banks",
        "company_headquarters": "US",
        "company_cik": 1000 + i,
        "company_founded": "1900",
    }


def test_filter_drops_empty_and_dedupes_questions() -> None:
    rows = [
        _row(1),
        _row(2, question="Same question?"),
        _row(3, question="Same question?"),
        {**_row(4), "program_answer": ""},
        {**_row(5), "question": ""},
    ]
    result = filter_and_dedupe(rows)
    assert result["stats"]["dropped_not_essential"] == 2
    assert result["stats"]["dropped_duplicate_question"] == 1
    assert result["stats"]["eligible_unique_questions"] == 2
    ids = [r["id"] for r in result["rows"]]
    assert ids == sorted(ids)


def test_stratified_sample_respects_caps_and_seed() -> None:
    rows = []
    for i in range(60):
        company = ["A", "B", "C", "D", "E"][i % 5]
        rows.append(_row(i, company=company, file_i=i))
    filtered = filter_and_dedupe(rows)["rows"]
    # n=15 with 5 companies × max 3 fits without relaxing caps.
    a = stratified_sample(filtered, n=15, seed=42, max_per_company=3, max_per_file=1)
    b = stratified_sample(filtered, n=15, seed=42, max_per_company=3, max_per_file=1)
    assert [r["id"] for r in a["rows"]] == [r["id"] for r in b["rows"]]
    assert a["n"] == 15
    assert a["max_questions_per_company"] <= 3
    assert a["max_questions_per_file"] <= 1
    assert a["caps_used"] == {"max_per_company": 3, "max_per_file": 1}


def test_freeze_writes_csv_and_manifest(tmp_path: Path) -> None:
    rows = [_row(i, company=["A", "B", "C", "D"][i % 4], file_i=i) for i in range(40)]
    csv_path = tmp_path / "selected_140_questions.csv"
    manifest_path = tmp_path / "sampling_manifest.json"
    # Use n=10 for unit speed.
    result = freeze_test_140(
        rows,
        output_csv=csv_path,
        output_manifest=manifest_path,
        n=10,
        seed=42,
    )
    assert result["manifest"]["n"] == 10
    assert csv_path.is_file()
    with csv_path.open(encoding="utf-8") as handle:
        loaded = list(csv.DictReader(handle))
    assert len(loaded) == 10
    assert len({r["id"] for r in loaded}) == 10
    assert len({normalize_question(r["question"]) for r in loaded}) == 10


def test_phase4_frozen_artefacts_if_present() -> None:
    """Integration check against the live freeze (created by scripts/select_140.py)."""
    root = project_root()
    csv_path = root / "data" / "final" / "selected_140_questions.csv"
    manifest_path = root / "data" / "final" / "sampling_manifest.json"
    assert csv_path.is_file(), "Run: PYTHONPATH=. python scripts/select_140.py"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["phase"] == 4
    assert manifest["frozen"] is True
    assert manifest["n"] == 140
    assert manifest["sampling_seed"] == 42
    assert len(manifest["selected_ids"]) == 140
    assert len(set(manifest["selected_ids"])) == 140

    with csv_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 140
    assert len({r["id"] for r in rows}) == 140
    assert len({normalize_question(r["question"]) for r in rows}) == 140
    assert all(r["program_answer"].strip() for r in rows)
    assert all(r["file_name"].strip() for r in rows)
    assert {r["id"] for r in rows} == set(manifest["selected_ids"])

    # Replay fingerprint stability: recompute from CSV ids.
    import hashlib

    payload = json.dumps([r["id"] for r in rows], separators=(",", ":"))
    assert hashlib.sha256(payload.encode("utf-8")).hexdigest() == manifest["selected_ids_sha256"]

    # Phase 5 calibration freeze must not exist yet.
    assert not (root / "data" / "calibration" / "calibration_questions.csv").exists()
