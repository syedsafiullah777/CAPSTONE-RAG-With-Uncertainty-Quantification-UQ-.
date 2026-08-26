"""Write or refuse ``threshold.lock.json``. Official lock requires a real DEV run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.calibration.data import CALIBRATION_N, assert_no_test_leakage
from src.calibration.select import case_to_point, select_threshold
from src.config import get_path, load_experiment_config, project_root
from src.run.store import utc_now
from src.run.subset import ids_sha256

LOCK_FILENAME = "threshold.lock.json"
CANDIDATE_FILENAME = "threshold.candidate.json"
OFFICIAL_BACKENDS = {"llama_cpp", "transformers"}


def lock_path() -> Path:
    return get_path(load_experiment_config(), "results_config") / LOCK_FILENAME


def candidate_path() -> Path:
    return get_path(load_experiment_config(), "results_config") / CANDIDATE_FILENAME


def load_cases(jsonl_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            rows.append(json.loads(text))
    return rows


def official_lock_allowed(*, backend: str, device: str | None, n_completed: int) -> tuple[bool, str]:
    if str(backend).lower() in {"mock", "test"}:
        return False, "Mock backend cannot lock the official threshold."
    if str(backend).lower() not in OFFICIAL_BACKENDS:
        return False, f"Backend {backend!r} is not an official lock backend ({sorted(OFFICIAL_BACKENDS)})."
    if device in {None, "mps_capable_host"}:
        return False, "Official lock requires a CUDA Colab-style device, not Mac MPS."
    if n_completed < CALIBRATION_N:
        return False, f"Official lock requires {CALIBRATION_N} completed DEV cases (got {n_completed})."
    return True, "ok"


def build_lock_payload(
    cases: list[dict[str, Any]],
    *,
    run_id: str,
    backend: str,
    device: str | None,
    gpu: Any,
    git_commit: str | None,
    official: bool,
) -> dict[str, Any]:
    question_ids = [str(case.get("question_id")) for case in cases]
    fake_rows = [{"id": qid} for qid in question_ids]
    assert_no_test_leakage(fake_rows)
    points = [case_to_point(case) for case in cases]
    selection = select_threshold(points)
    curve = selection.pop("curve")
    payload = {
        "phase": 13,
        "mode": "calibration",
        "locked": bool(official and selection.get("selected")),
        "threshold": selection.get("threshold"),
        "rule": selection.get("rule"),
        "coverage_floor": selection.get("coverage_floor"),
        "tie_break": selection.get("tie_break"),
        "coverage": selection.get("coverage"),
        "selective_accuracy": selection.get("selective_accuracy"),
        "n": selection.get("n"),
        "n_answer": selection.get("n_answer"),
        "n_abstain": selection.get("n_abstain"),
        "selected": selection.get("selected"),
        "reason": selection.get("reason"),
        "source_split": "dev",
        "used_frozen_test_140": False,
        "n_cases": len(cases),
        "question_ids": question_ids,
        "question_ids_sha256": ids_sha256(question_ids),
        "run_id": run_id,
        "backend": backend,
        "device": device,
        "gpu": gpu,
        "git_commit": git_commit,
        "architecture": "multi_agent_uq",
        "recorded_at_utc": utc_now(),
        "curve": curve,
    }
    if official and payload["locked"]:
        payload["threshold_note"] = "LOCKED on FinQA DEV calibration — not tuned on the frozen 140"
    else:
        payload["threshold_note"] = "candidate only — NOT LOCKED"
        payload["locked"] = False
    return payload


def write_threshold_files(payload: dict[str, Any]) -> dict[str, str]:
    out_dir = get_path(load_experiment_config(), "results_config")
    out_dir.mkdir(parents=True, exist_ok=True)
    cand = out_dir / CANDIDATE_FILENAME
    cand.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    written = {"candidate": _rel(cand)}
    if payload.get("locked"):
        lock = out_dir / LOCK_FILENAME
        lock.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
        written["lock"] = _rel(lock)
    return written


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_root()))
    except ValueError:
        return str(path)
