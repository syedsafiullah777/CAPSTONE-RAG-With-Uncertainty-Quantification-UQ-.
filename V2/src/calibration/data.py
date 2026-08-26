"""Phase 13: load the frozen FinQA DEV calibration set (never the frozen 140)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.config import ExperimentConfig, get_path, load_experiment_config, project_root
from src.data.select_calibration import rows_fingerprint
from src.run.subset import load_frozen_question_rows

CALIBRATION_N = 40
COVERAGE_FLOOR = 0.50
SELECTION_RULE = "max_selective_accuracy_coverage_ge_0.50"
TIE_BREAK = "lowest_threshold"


def calibration_csv(config: ExperimentConfig | None = None) -> Path:
    cfg = config or load_experiment_config()
    dataset = cfg.section("dataset")
    rel = str(dataset.get("frozen_calibration_set") or "data/calibration/calibration_questions.csv")
    path = (project_root() / rel).resolve()
    if not path.is_file():
        path = get_path(cfg, "data_calibration") / "calibration_questions.csv"
    return path


def calibration_manifest_path(config: ExperimentConfig | None = None) -> Path:
    cfg = config or load_experiment_config()
    dataset = cfg.section("dataset")
    rel = str(dataset.get("calibration_manifest") or "data/calibration/calibration_manifest.json")
    return (project_root() / rel).resolve()


def load_calibration_questions(
    *,
    n: int = CALIBRATION_N,
    config: ExperimentConfig | None = None,
    csv_path: Path | None = None,
) -> list[dict[str, str]]:
    if n < 1:
        raise ValueError("Calibration n must be >= 1")
    if n > CALIBRATION_N:
        raise ValueError(
            f"Phase 13 calibration is capped at {CALIBRATION_N} DEV questions. "
            "Do not use the frozen 140 or start the 420-case benchmark here."
        )
    path = csv_path or calibration_csv(config)
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            qid = str(row.get("id") or "").strip()
            question = str(row.get("question") or "").strip()
            split = str(row.get("split") or "dev").strip().lower()
            if not qid or not question:
                continue
            if split and split != "dev":
                raise ValueError(f"Calibration row {qid} has split={split!r}; expected dev")
            rows.append(
                {
                    "id": qid,
                    "question": question,
                    "program_answer": str(row.get("program_answer") or ""),
                    "original_answer": str(row.get("original_answer") or ""),
                    "file_name": str(row.get("file_name") or ""),
                    "split": "dev",
                }
            )
            if len(rows) >= n:
                break
    if len(rows) < n:
        raise ValueError(f"Calibration CSV has {len(rows)} rows; need {n}")
    return rows


def frozen_test_ids(config: ExperimentConfig | None = None) -> set[str]:
    return {row["id"] for row in load_frozen_question_rows()}


def assert_no_test_leakage(questions: list[dict[str, str]], *, config: ExperimentConfig | None = None) -> None:
    test_ids = frozen_test_ids(config)
    leaked = [row["id"] for row in questions if row["id"] in test_ids]
    if leaked:
        raise RuntimeError(f"Calibration set leaks frozen test IDs: {leaked[:5]}")
    bad_prefix = [row["id"] for row in questions if not str(row["id"]).startswith("finqa_dev_")]
    if bad_prefix:
        raise RuntimeError(f"Calibration IDs must be FinQA DEV, got: {bad_prefix[:5]}")


def load_calibration_manifest(path: Path | None = None) -> dict[str, Any]:
    dest = path or calibration_manifest_path()
    return json.loads(dest.read_text(encoding="utf-8"))


def verify_calibration_subset(questions: list[dict[str, str]]) -> dict[str, Any]:
    manifest = load_calibration_manifest()
    ids = [row["id"] for row in questions]
    expected = list(manifest.get("selected_ids") or [])[: len(ids)]
    if expected and ids != expected:
        raise ValueError("Calibration question IDs do not match the frozen Phase 5 manifest order")
    expected_sha = str(manifest.get("selected_ids_sha256") or "")
    if len(ids) == CALIBRATION_N and expected_sha and rows_fingerprint(questions) != expected_sha:
        raise ValueError("Calibration ID SHA-256 does not match the Phase 5 manifest")
    assert_no_test_leakage(questions)
    return manifest
