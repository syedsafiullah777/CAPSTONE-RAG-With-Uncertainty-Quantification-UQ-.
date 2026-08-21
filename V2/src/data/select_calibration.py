"""Phase 5: freeze FinQA DEV calibration questions (separate from the frozen test 140).

Threshold locking is NOT performed here — only the calibration sample is frozen.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from src.data.select_140 import (
    EXPORT_COLUMNS,
    filter_and_dedupe,
    normalize_question,
    stratified_sample,
    write_csv,
)


def load_frozen_test_ids_and_questions(
    test_csv: Path,
) -> tuple[set[str], set[str]]:
    if not test_csv.exists():
        raise FileNotFoundError(
            f"Frozen test set not found: {test_csv}. Run Phase 4 first."
        )
    ids: set[str] = set()
    questions: set[str] = set()
    with test_csv.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            ids.add(str(row["id"]))
            questions.add(normalize_question(str(row["question"])))
    return ids, questions


def exclude_test_overlap(
    rows: list[dict[str, Any]],
    forbidden_ids: set[str],
    forbidden_questions: set[str],
) -> dict[str, Any]:
    kept: list[dict[str, Any]] = []
    dropped_id = 0
    dropped_question = 0
    for row in rows:
        if str(row["id"]) in forbidden_ids:
            dropped_id += 1
            continue
        if normalize_question(str(row["question"])) in forbidden_questions:
            dropped_question += 1
            continue
        kept.append(row)
    return {
        "rows": kept,
        "stats": {
            "input_rows": len(rows),
            "dropped_id_overlap": dropped_id,
            "dropped_question_overlap": dropped_question,
            "remaining": len(kept),
        },
    }


def rows_fingerprint(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps([r["id"] for r in rows], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def freeze_calibration(
    dev_rows: list[dict[str, Any]],
    *,
    frozen_test_csv: Path,
    output_csv: Path,
    output_manifest: Path,
    n: int = 40,
    seed: int = 42,
    max_per_company: int = 2,
    max_per_file: int = 1,
    dataset_id: str = "G4KMU/t2-ragbench",
    subset: str = "FinQA",
) -> dict[str, Any]:
    forbidden_ids, forbidden_questions = load_frozen_test_ids_and_questions(frozen_test_csv)
    filtered = filter_and_dedupe(dev_rows, split="dev")
    cleaned = exclude_test_overlap(filtered["rows"], forbidden_ids, forbidden_questions)
    sampled = stratified_sample(
        cleaned["rows"],
        n=n,
        seed=seed,
        max_per_company=max_per_company,
        max_per_file=max_per_file,
    )
    write_csv(output_csv, sampled["rows"])

    # Hard safety checks before writing the manifest.
    selected_ids = [r["id"] for r in sampled["rows"]]
    selected_questions = {normalize_question(str(r["question"])) for r in sampled["rows"]}
    if set(selected_ids) & forbidden_ids:
        raise RuntimeError("Calibration set overlaps frozen test ids")
    if selected_questions & forbidden_questions:
        raise RuntimeError("Calibration set overlaps frozen test questions")

    manifest = {
        "phase": 5,
        "frozen": True,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "confidence_threshold_calibration_only",
        "threshold_locked": False,
        "dataset_id": dataset_id,
        "subset": subset,
        "source_split": "dev",
        "n": sampled["n"],
        "sampling_seed": seed,
        "filter_rules": {
            "require_non_empty": [
                "id",
                "question",
                "program_answer",
                "context_id",
                "file_name",
                "context",
            ],
            "dedupe": "normalize_question keep_lowest_id",
            "exclude_overlap_with": str(frozen_test_csv),
        },
        "diversity_caps_requested": {
            "max_per_company": max_per_company,
            "max_per_file": max_per_file,
        },
        "diversity_caps_used": sampled["caps_used"],
        "filter_stats": filtered["stats"],
        "overlap_exclusion_stats": cleaned["stats"],
        "unique_companies": sampled["unique_companies"],
        "unique_files": sampled["unique_files"],
        "max_questions_per_company": sampled["max_questions_per_company"],
        "max_questions_per_file": sampled["max_questions_per_file"],
        "report_year_distribution": sampled["report_year_distribution"],
        "selected_ids": selected_ids,
        "selected_ids_sha256": rows_fingerprint(sampled["rows"]),
        "frozen_test_csv": str(frozen_test_csv),
        "output_csv": str(output_csv),
        "export_columns": EXPORT_COLUMNS,
        "note": (
            "Use this set only to choose confidence method/threshold. "
            "Lock threshold before evaluating the frozen test 140. "
            "Do not tune the threshold on the test set."
        ),
    }
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    output_manifest.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    return {"rows": sampled["rows"], "manifest": manifest}
