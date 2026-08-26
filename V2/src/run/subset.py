"""Reproducible Phase 12 pilot subset from the frozen 140-question test set.

Does not modify ``selected_140_questions.csv`` or the calibration set.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from src.config import ExperimentConfig, get_path, load_experiment_config, project_root

PILOT_N_QUESTIONS = 6
PILOT_N_ARCHITECTURES = 3
PILOT_N_CASES = PILOT_N_QUESTIONS * PILOT_N_ARCHITECTURES
SELECTION_RULE = "first_n_rows_of_frozen_140_csv"
THRESHOLD_NOTE = "smoke/demo — NOT LOCKED"


def frozen_test_csv(config: ExperimentConfig | None = None) -> Path:
    cfg = config or load_experiment_config()
    dataset = cfg.section("dataset")
    rel = str(dataset.get("frozen_test_set") or "data/final/selected_140_questions.csv")
    path = (project_root() / rel).resolve()
    if not path.is_file():
        path = get_path(cfg, "data_final") / "selected_140_questions.csv"
    return path


def load_frozen_question_rows(csv_path: Path | None = None) -> list[dict[str, str]]:
    path = csv_path or frozen_test_csv()
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            qid = str(row.get("id") or "").strip()
            question = str(row.get("question") or "").strip()
            if not qid or not question:
                continue
            rows.append(
                {
                    "id": qid,
                    "question": question,
                    "program_answer": str(row.get("program_answer") or ""),
                    "original_answer": str(row.get("original_answer") or ""),
                    "file_name": str(row.get("file_name") or ""),
                    "company_symbol": str(row.get("company_symbol") or ""),
                }
            )
    return rows


def ids_sha256(question_ids: list[str]) -> str:
    payload = "\n".join(question_ids).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def select_pilot_questions(
    *,
    n: int = PILOT_N_QUESTIONS,
    config: ExperimentConfig | None = None,
    csv_path: Path | None = None,
) -> list[dict[str, str]]:
    """Return the first *n* frozen-140 rows (Phase 4 CSV order, seed 42)."""
    if n < 1:
        raise ValueError("Pilot n must be >= 1")
    if n > PILOT_N_QUESTIONS:
        raise ValueError(
            f"Phase 12 pilot is capped at {PILOT_N_QUESTIONS} questions "
            f"({PILOT_N_CASES} cases). The 140-question / 420-case benchmark is a later phase."
        )
    rows = load_frozen_question_rows(csv_path or frozen_test_csv(config))
    if len(rows) < n:
        raise ValueError(f"Frozen test CSV has {len(rows)} rows; need {n}")
    selected = rows[:n]
    frozen_ids = {row["id"] for row in rows}
    if any(row["id"] not in frozen_ids for row in selected):
        raise ValueError("Pilot subset is not a subset of the frozen 140")
    return selected


def build_pilot_manifest(
    questions: list[dict[str, str]],
    *,
    frozen_n: int = 140,
) -> dict[str, Any]:
    ids = [row["id"] for row in questions]
    return {
        "phase": 12,
        "mode": "pilot",
        "frozen": True,
        "modifies_frozen_140": False,
        "modifies_frozen_calibration": False,
        "threshold_locked": False,
        "threshold_note": THRESHOLD_NOTE,
        "selection_rule": SELECTION_RULE,
        "source_csv": "data/final/selected_140_questions.csv",
        "source_split": "test",
        "frozen_n": frozen_n,
        "n_questions": len(ids),
        "n_architectures": PILOT_N_ARCHITECTURES,
        "n_cases": len(ids) * PILOT_N_ARCHITECTURES,
        "question_ids": ids,
        "question_ids_sha256": ids_sha256(ids),
        "notes": (
            "Subset is the first N rows of the Phase 4 frozen CSV (already ordered "
            "by sampling seed 42). This file documents the subset; it does not replace "
            "selected_140_questions.csv."
        ),
    }


def pilot_manifest_path() -> Path:
    return project_root() / "data" / "final" / "pilot_subset_manifest.json"


def write_pilot_manifest(questions: list[dict[str, str]], path: Path | None = None) -> Path:
    dest = path or pilot_manifest_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = build_pilot_manifest(questions)
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return dest


def load_pilot_manifest(path: Path | None = None) -> dict[str, Any]:
    dest = path or pilot_manifest_path()
    return json.loads(dest.read_text(encoding="utf-8"))


def verify_pilot_subset(questions: list[dict[str, str]], manifest: dict[str, Any] | None = None) -> None:
    ids = [row["id"] for row in questions]
    man = manifest or load_pilot_manifest()
    if man.get("modifies_frozen_140") is True:
        raise ValueError("Pilot manifest must not modify the frozen 140")
    if man.get("threshold_locked") is True:
        raise ValueError("Pilot must not lock the confidence threshold")
    if man.get("question_ids") != ids:
        raise ValueError("Pilot question IDs do not match the committed manifest")
    if man.get("question_ids_sha256") != ids_sha256(ids):
        raise ValueError("Pilot ID SHA-256 does not match the committed manifest")
