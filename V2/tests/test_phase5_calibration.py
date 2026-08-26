"""Phase 5 tests: calibration freeze logic and artefacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from src.config import project_root
from src.data.select_140 import normalize_question
from src.data.select_calibration import exclude_test_overlap, freeze_calibration


def _row(i: int, *, split: str = "dev", company: str = "A", question: str | None = None) -> dict:
    return {
        "id": f"{split}_{i:04d}",
        "context_id": f"ctx_{i}",
        "split": split,
        "question": question if question is not None else f"Dev question {i}?",
        "program_answer": str(i),
        "original_answer": str(i),
        "context": "evidence " * 20,
        "table": "|a|b|",
        "pre_text": "pre",
        "post_text": "post",
        "file_name": f"pdf/{company}/2011/page_{i}.pdf",
        "company_name": f"Company {company}",
        "company_symbol": company,
        "report_year": 2011,
        "page_number": i,
        "company_sector": "Financials",
        "company_industry": "Banks",
        "company_headquarters": "US",
        "company_cik": 2000 + i,
        "company_founded": "1900",
    }


def test_exclude_test_overlap_by_id_and_question() -> None:
    rows = [
        _row(1, question="Unique one?"),
        _row(2, question="Overlap question?"),
        {**_row(3), "id": "test_0001"},
    ]
    cleaned = exclude_test_overlap(
        rows,
        forbidden_ids={"test_0001"},
        forbidden_questions={normalize_question("Overlap question?")},
    )
    assert cleaned["stats"]["dropped_id_overlap"] == 1
    assert cleaned["stats"]["dropped_question_overlap"] == 1
    assert cleaned["stats"]["remaining"] == 1
    assert cleaned["rows"][0]["id"] == "dev_0001"


def test_freeze_calibration_no_overlap(tmp_path: Path) -> None:
    test_csv = tmp_path / "selected_140_questions.csv"
    with test_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "question", "program_answer", "file_name", "company_symbol"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "test_0099",
                "question": "Shared wording?",
                "program_answer": "1",
                "file_name": "pdf/X/2010/page_1.pdf",
                "company_symbol": "X",
            }
        )

    dev_rows = []
    for i in range(30):
        company = ["A", "B", "C", "D", "E", "F"][i % 6]
        q = "Shared wording?" if i == 7 else f"Calibration item {i}?"
        row_id = "test_0099" if i == 8 else f"dev_{i:04d}"
        row = _row(i, company=company, question=q)
        row["id"] = row_id
        row["file_name"] = f"pdf/{company}/2011/page_{i}.pdf"
        dev_rows.append(row)

    out_csv = tmp_path / "calibration_questions.csv"
    out_manifest = tmp_path / "calibration_manifest.json"
    result = freeze_calibration(
        dev_rows,
        frozen_test_csv=test_csv,
        output_csv=out_csv,
        output_manifest=out_manifest,
        n=10,
        seed=42,
        max_per_company=2,
        max_per_file=1,
    )
    assert result["manifest"]["n"] == 10
    assert result["manifest"]["threshold_locked"] is False
    assert "test_0099" not in result["manifest"]["selected_ids"]
    assert normalize_question("Shared wording?") not in {
        normalize_question(r["question"]) for r in result["rows"]
    }


def test_phase5_frozen_artefacts() -> None:
    root = project_root()
    csv_path = root / "data" / "calibration" / "calibration_questions.csv"
    manifest_path = root / "data" / "calibration" / "calibration_manifest.json"
    test_csv = root / "data" / "final" / "selected_140_questions.csv"
    assert csv_path.is_file(), "Run: PYTHONPATH=. python scripts/select_calibration.py"
    assert manifest_path.is_file()
    assert test_csv.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["phase"] == 5
    assert manifest["frozen"] is True
    assert manifest["threshold_locked"] is False
    assert manifest["source_split"] == "dev"
    assert manifest["n"] == 40
    assert manifest["sampling_seed"] == 42

    with csv_path.open(encoding="utf-8") as handle:
        cal_rows = list(csv.DictReader(handle))
    with test_csv.open(encoding="utf-8") as handle:
        test_rows = list(csv.DictReader(handle))

    assert len(cal_rows) == 40
    cal_ids = {r["id"] for r in cal_rows}
    test_ids = {r["id"] for r in test_rows}
    assert not (cal_ids & test_ids)

    cal_q = {normalize_question(r["question"]) for r in cal_rows}
    test_q = {normalize_question(r["question"]) for r in test_rows}
    assert not (cal_q & test_q)
    assert len(cal_q) == 40

    lock_path = root / "results" / "config" / "threshold.lock.json"
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        assert lock.get("used_frozen_test_140") is False
        assert lock.get("source_split") == "dev"
        assert int(lock.get("phase") or 0) >= 13
