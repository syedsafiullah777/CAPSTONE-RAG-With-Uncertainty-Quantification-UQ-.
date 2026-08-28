"""Load frozen Phase 16 scored cases + official judge JSONL. Read-only SHA gates."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD, load_official_lock
from src.config import project_root
from src.statistics.constants import (
    ARCHITECTURES,
    CAL_40_REL,
    EXPECTED_CAL40_SHA256,
    EXPECTED_FROZEN140_SHA256,
    EXPECTED_JUDGE_SHA256,
    EXPECTED_LOCK_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
    FORBIDDEN_IMPORT_MODULES,
    FROZEN_140_REL,
    JUDGE_REL,
    LOCKED_T,
    LOCK_REL,
    N_CASES,
    N_QUESTIONS,
    PHASE15_REL,
    PROCESSED_REL,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def verify_no_generation_stack() -> None:
    stats_dir = Path(__file__).resolve().parent
    imported: set[str] = set()
    for py in stats_dir.glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    banned = imported & FORBIDDEN_IMPORT_MODULES
    if banned:
        raise RuntimeError(f"Phase 17 statistics must not import generation stack: {sorted(banned)}")


def verify_frozen_hashes(root: Path | None = None) -> dict[str, str]:
    root = root or project_root()
    lock = load_official_lock()
    if abs(float(lock["threshold"]) - EXPECTED_LOCKED_THRESHOLD) > 1e-9:
        raise RuntimeError("Locked T is not 0.65. Phase 17 must not recalibrate.")
    if abs(float(lock["threshold"]) - LOCKED_T) > 1e-9:
        raise RuntimeError("Unexpected lock threshold.")
    paths = {
        "phase15": root / PHASE15_REL,
        "processed": root / PROCESSED_REL,
        "judge": root / JUDGE_REL,
        "frozen140": root / FROZEN_140_REL,
        "cal40": root / CAL_40_REL,
        "lock": root / LOCK_REL,
    }
    expected = {
        "phase15": EXPECTED_PHASE15_SHA256,
        "processed": EXPECTED_PROCESSED_SHA256,
        "judge": EXPECTED_JUDGE_SHA256,
        "frozen140": EXPECTED_FROZEN140_SHA256,
        "cal40": EXPECTED_CAL40_SHA256,
        "lock": EXPECTED_LOCK_SHA256,
    }
    observed: dict[str, str] = {}
    for key, path in paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Required Phase 17 input missing: {path}")
        digest = sha256_file(path)
        observed[key] = digest
        if digest != expected[key]:
            raise RuntimeError(
                f"SHA-256 mismatch for {key}: {digest} != {expected[key]}. "
                "Phase 17 refuses to proceed if frozen artefacts changed."
            )
    return observed


def load_joined(root: Path | None = None) -> dict[str, Any]:
    """Join Phase 16 CPU rows with official judge scores. Does not rewrite inputs."""
    verify_no_generation_stack()
    root = root or project_root()
    hashes = verify_frozen_hashes(root)
    processed = _jsonl(root / PROCESSED_REL)
    judge = _jsonl(root / JUDGE_REL)
    if len(processed) != N_CASES or len(judge) != N_CASES:
        raise ValueError(f"Expected {N_CASES} processed and judge rows")

    judge_by_key = {str(row["case_key"]): row for row in judge}
    if len(judge_by_key) != N_CASES:
        raise ValueError("Duplicate or missing judge case_key")

    by_q: dict[str, dict[str, dict[str, Any]]] = {}
    for row in processed:
        key = str(row["case_key"])
        qid = str(row["question_id"])
        arch = str(row["architecture"])
        if key not in judge_by_key:
            raise KeyError(f"Judge missing {key}")
        jrow = judge_by_key[key]
        merged = dict(row)
        merged["llm_faithfulness"] = float(jrow["parsed_faithfulness_score"])
        merged["llm_parse_failure"] = bool(jrow.get("parse_failure"))
        merged["judge_claim_source"] = jrow.get("claim_source")
        merged["judge_used_rag_rerun"] = bool(jrow.get("used_rag_rerun"))
        merged["judge_used_gold_context"] = bool(jrow.get("used_gold_context"))
        merged["judge_used_gold_answer"] = bool(jrow.get("used_gold_answer"))
        by_q.setdefault(qid, {})[arch] = merged

    if len(by_q) != N_QUESTIONS:
        raise ValueError(f"Expected {N_QUESTIONS} questions, found {len(by_q)}")
    for qid, arches in by_q.items():
        missing = [a for a in ARCHITECTURES if a not in arches]
        if missing:
            raise ValueError(f"{qid} missing {missing}")

    question_ids = sorted(by_q)
    return {
        "question_ids": question_ids,
        "by_question": by_q,
        "hashes": hashes,
        "n_questions": N_QUESTIONS,
        "n_cases": N_CASES,
        "used_rag_rerun": False,
        "used_llm_inference": False,
        "modifies_phase15_raw": False,
        "modifies_phase16_cpu": False,
        "modifies_phase16_judge": False,
        "threshold": LOCKED_T,
    }


def series(joined: dict[str, Any], architecture: str, field: str) -> list[Any]:
    out: list[Any] = []
    for qid in joined["question_ids"]:
        out.append(joined["by_question"][qid][architecture][field])
    return out
