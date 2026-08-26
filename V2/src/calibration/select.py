"""Pre-registered DEV-only threshold selection. Never inspect the frozen 140."""

from __future__ import annotations

from typing import Any

from src.calibration.data import COVERAGE_FLOOR, SELECTION_RULE, TIE_BREAK
from src.evaluation.numeric import numeric_match

GRID_STEP = 0.01


def draft_text(case: dict[str, Any]) -> str:
    cfg = case.get("configuration") or {}
    draft = cfg.get("draft_answer")
    if draft:
        return str(draft)
    return str(case.get("answer") or "")


def case_to_point(case: dict[str, Any]) -> dict[str, Any]:
    confidence = case.get("confidence")
    gold = case.get("reference_answer")
    predicted = draft_text(case)
    correct = numeric_match(predicted, gold) if confidence is not None else False
    return {
        "question_id": case.get("question_id"),
        "confidence": None if confidence is None else float(confidence),
        "correct": bool(correct),
        "gold": gold,
        "draft": predicted,
        "smoke_decision": case.get("decision"),
    }


def _candidate_thresholds(confidences: list[float]) -> list[float]:
    grid = [round(i * GRID_STEP, 2) for i in range(0, 101)]
    observed = sorted({round(float(c), 4) for c in confidences})
    merged = sorted(set(grid + observed))
    return merged


def metrics_at_threshold(points: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    usable = [p for p in points if p.get("confidence") is not None]
    n = len(usable)
    answered = [p for p in usable if float(p["confidence"]) >= threshold]
    abstained = n - len(answered)
    n_answer = len(answered)
    n_correct = sum(1 for p in answered if p["correct"])
    coverage = (n_answer / n) if n else 0.0
    selective_accuracy = (n_correct / n_answer) if n_answer else 0.0
    return {
        "threshold": float(threshold),
        "n": n,
        "n_answer": n_answer,
        "n_abstain": abstained,
        "n_correct_answered": n_correct,
        "coverage": coverage,
        "selective_accuracy": selective_accuracy,
        "meets_coverage_floor": coverage >= COVERAGE_FLOOR,
    }


def sweep_thresholds(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    confidences = [float(p["confidence"]) for p in points if p.get("confidence") is not None]
    if not confidences:
        raise ValueError("No calibration confidences to sweep")
    return [metrics_at_threshold(points, t) for t in _candidate_thresholds(confidences)]


def select_threshold(points: list[dict[str, Any]]) -> dict[str, Any]:
    """Maximise selective accuracy among T with coverage >= 0.50; tie → lowest T."""
    curve = sweep_thresholds(points)
    feasible = [row for row in curve if row["meets_coverage_floor"]]
    if not feasible:
        return {
            "selected": False,
            "threshold": None,
            "rule": SELECTION_RULE,
            "coverage_floor": COVERAGE_FLOOR,
            "tie_break": TIE_BREAK,
            "reason": f"No threshold achieved coverage >= {COVERAGE_FLOOR}",
            "curve": curve,
        }
    best = max(feasible, key=lambda row: (row["selective_accuracy"], -row["threshold"]))
    return {
        "selected": True,
        "threshold": best["threshold"],
        "rule": SELECTION_RULE,
        "coverage_floor": COVERAGE_FLOOR,
        "tie_break": TIE_BREAK,
        "coverage": best["coverage"],
        "selective_accuracy": best["selective_accuracy"],
        "n_answer": best["n_answer"],
        "n_abstain": best["n_abstain"],
        "n": best["n"],
        "curve": curve,
    }
