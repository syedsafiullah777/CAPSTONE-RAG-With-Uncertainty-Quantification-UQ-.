"""Uncertainty quantification and abstention for Multi-Agent + UQ (Phase 10)."""

from __future__ import annotations

from typing import Any

from src.rag.text_utils import average


def compute_retrieval_score(retrieval_scores: list[float]) -> float:
    """Aggregate top-k retrieval similarities into one signal (mean)."""
    if not retrieval_scores:
        return 0.0
    return average(retrieval_scores)


def compute_combined_confidence(
    retrieval_score: float,
    verification_score: float,
    *,
    method: str = "mean_retrieval_verification",
) -> dict[str, Any]:
    """Combine retrieval and verification into a single confidence score."""
    if method != "mean_retrieval_verification":
        raise ValueError(f"Unsupported UQ method: {method}")
    confidence = average([retrieval_score, verification_score])
    return {
        "method": method,
        "retrieval_score": retrieval_score,
        "verification_score": verification_score,
        "confidence": confidence,
    }


def apply_abstention_decision(
    *,
    draft_answer: str,
    confidence: float,
    threshold: float,
    abstention_message: str,
) -> tuple[str, str]:
    """Return (final_answer, decision) where decision is ANSWER or ABSTAIN."""
    if confidence >= threshold:
        return draft_answer, "ANSWER"
    return abstention_message, "ABSTAIN"
