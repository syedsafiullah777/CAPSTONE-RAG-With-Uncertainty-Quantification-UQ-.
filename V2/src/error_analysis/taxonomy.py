"""Deterministic error taxonomy from recorded fields. No invented causes."""

from __future__ import annotations

from typing import Any

from src.evaluation.numeric import parse_numbers
from src.error_analysis.constants import FAITHFULNESS_LOW, HIGH_CONFIDENCE, PRIMARY_CATEGORIES


def _has_number(text: str) -> bool:
    return bool(parse_numbers(text))


def assign_category(case: dict[str, Any]) -> dict[str, Any]:
    """Assign one primary category plus factual tags.

    Order is explicit so UQ abstention is not labelled as a displayed numeric error.
    Numeric incorrectness is never labelled hallucination.
    """
    answered = bool(case["answered"])
    displayed_ok = int(case["displayed_correct"]) == 1
    claim_ok = int(case["claim_correct"]) == 1
    recall = float(case["context_recall"])
    gold_in_evidence = int(case["context_recall_numeric"]) == 1
    llm = float(case["llm_faithfulness"])
    displayed = str(case.get("displayed_answer") or "")
    conf = case.get("confidence")
    verify = case.get("verification_status")

    tags: list[str] = []
    if recall == 0.0:
        tags.append("gold_file_or_context_absent_from_topk")
    if gold_in_evidence:
        tags.append("gold_number_present_in_evidence")
    else:
        tags.append("gold_number_absent_from_evidence")
    if float(case["context_precision"]) <= 0.25:
        tags.append("low_context_precision")
    if answered and conf is not None and float(conf) >= HIGH_CONFIDENCE and not displayed_ok:
        tags.append("false_confidence")
    if verify == "VERIFIED" and not claim_ok:
        tags.append("verification_false_positive")
    if verify == "VERIFIED" and claim_ok:
        tags.append("verification_true_positive")
    if verify == "WEAK_EVIDENCE" and not claim_ok:
        tags.append("verification_true_negative")
    if verify == "WEAK_EVIDENCE" and claim_ok:
        tags.append("verification_false_negative")
    if answered and not _has_number(displayed):
        tags.append("displayed_text_has_no_parsed_number")
    if llm < FAITHFULNESS_LOW:
        tags.append("low_llm_judge_faithfulness")
    else:
        tags.append("high_llm_judge_faithfulness")

    if not answered and claim_ok:
        primary = "incorrect_abstention"
    elif not answered and not claim_ok:
        primary = "appropriate_abstention"
    elif displayed_ok:
        primary = "correct_answer"
    elif recall == 0.0:
        primary = "retrieval_failure"
    elif not _has_number(displayed):
        primary = "non_numeric_answer"
    elif gold_in_evidence:
        primary = "incorrect_numerical_reasoning"
    elif llm < FAITHFULNESS_LOW:
        primary = "unsupported_claim"
    else:
        primary = "incorrect_despite_partial_evidence"

    if primary not in PRIMARY_CATEGORIES:
        raise ValueError(primary)

    layer = {
        "correct_answer": "numeric_correct",
        "appropriate_abstention": "abstention",
        "incorrect_abstention": "abstention",
        "retrieval_failure": "retrieval",
        "non_numeric_answer": "answer_format",
        "incorrect_numerical_reasoning": "numeric_error",
        "unsupported_claim": "unsupported_emission",
        "incorrect_despite_partial_evidence": "numeric_error",
    }[primary]

    return {
        "primary_category": primary,
        "error_layer": layer,
        "tags": tags,
    }
