"""Phase 16 CPU metrics from saved RAG cases. No LLM / GPU / new generation."""

from __future__ import annotations

from typing import Any

from src.evaluation.numeric import numeric_match
from src.rag.text_utils import token_overlap

ARCHITECTURE_UQ = "multi_agent_uq"


def _norm_path(value: str | None) -> str:
    return str(value or "").replace("\\", "/").strip().lower()


def files_match(left: str | None, right: str | None) -> bool:
    a, b = _norm_path(left), _norm_path(right)
    if not a or not b:
        return False
    return a == b or a.endswith("/" + b) or b.endswith("/" + a) or a.endswith(b) or b.endswith(a)


def chunk_is_relevant(chunk: dict[str, Any], gold: dict[str, str]) -> bool:
    gold_file = gold.get("file_name") or ""
    gold_ctx = str(gold.get("context_id") or "").strip()
    chunk_file = str(chunk.get("file_name") or "")
    chunk_ctx = str(chunk.get("context_id") or "").strip()
    if gold_ctx and chunk_ctx and gold_ctx == chunk_ctx:
        return True
    return files_match(chunk_file, gold_file)


def evidence_text(chunks: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for chunk in chunks:
        text = chunk.get("text") or chunk.get("content") or ""
        if text:
            parts.append(str(text))
    return "\n".join(parts)


def scored_claim_text(case: dict[str, Any]) -> str:
    """Text used for correctness/faithfulness of the model's claim.

    UQ ABSTAIN replaces the displayed answer with the abstention template;
    the draft is the claim that would have been emitted.
    """
    cfg = case.get("configuration") or {}
    draft = cfg.get("draft_answer")
    if case.get("architecture") == ARCHITECTURE_UQ and draft:
        return str(draft)
    return str(case.get("answer") or "")


def displayed_text(case: dict[str, Any]) -> str:
    return str(case.get("answer") or "")


def context_precision(chunks: list[dict[str, Any]], gold: dict[str, str]) -> float:
    if not chunks:
        return 0.0
    relevant = sum(1 for chunk in chunks if chunk_is_relevant(chunk, gold))
    return relevant / len(chunks)


def context_recall(chunks: list[dict[str, Any]], gold: dict[str, str]) -> float:
    if not chunks:
        return 0.0
    return 1.0 if any(chunk_is_relevant(chunk, gold) for chunk in chunks) else 0.0


def score_case(case: dict[str, Any], gold: dict[str, str]) -> dict[str, Any]:
    """Score one saved architecture–question case. CPU only."""
    chunks = list(case.get("retrieved_evidence") or [])
    gold_program = gold.get("program_answer") or case.get("reference_answer")
    gold_original = gold.get("original_answer") or ""
    claim = scored_claim_text(case)
    displayed = displayed_text(case)
    evidence = evidence_text(chunks)
    decision = str(case.get("decision") or "ANSWER")
    answered = decision == "ANSWER"

    correct_claim = numeric_match(claim, gold_program)
    correct_displayed = numeric_match(displayed, gold_program)
    correct_original = numeric_match(claim, gold_original) if gold_original else False

    faithfulness = token_overlap(claim, evidence)
    stored_verify = case.get("verification_result") if isinstance(case.get("verification_result"), dict) else {}
    precision = context_precision(chunks, gold)
    recall = context_recall(chunks, gold)
    recall_numeric = numeric_match(evidence, gold_program)

    unsupported_emitted = bool(answered and not correct_displayed)

    return {
        "case_key": case.get("case_key") or f"{case.get('architecture')}:{case.get('question_id')}",
        "run_id": case.get("run_id"),
        "question_id": case.get("question_id"),
        "architecture": case.get("architecture"),
        "decision": decision,
        "answered": answered,
        "confidence": case.get("confidence"),
        "threshold": case.get("threshold"),
        "n_evidence": len(chunks),
        "gold_program_answer": gold_program,
        "gold_file_name": gold.get("file_name"),
        "gold_context_id": gold.get("context_id"),
        "answer_correctness": int(correct_displayed),
        "answer_correctness_claim": int(correct_claim),
        "answer_correctness_original_answer": int(correct_original),
        "faithfulness": faithfulness,
        "faithfulness_stored_verification_score": stored_verify.get("verification_score"),
        "faithfulness_stored_lexical_score": stored_verify.get("lexical_score"),
        "context_precision": precision,
        "context_recall": recall,
        "context_recall_numeric": int(recall_numeric),
        "unsupported_emitted": int(unsupported_emitted),
        "latency_seconds": case.get("latency_seconds"),
        "backend": case.get("backend"),
        "device": case.get("device"),
        "gpu": case.get("gpu"),
        "model": case.get("model"),
        "quantisation": case.get("quantisation"),
        "error": case.get("error"),
        "used_llm_inference": False,
        "used_gpu": False,
    }


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def aggregate_architecture(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    answered = [r for r in rows if r.get("answered")]
    abstained = [r for r in rows if not r.get("answered")]
    n_answer = len(answered)
    n_abstain = len(abstained)
    n_correct_displayed = sum(int(r.get("answer_correctness") or 0) for r in rows)
    n_correct_claim = sum(int(r.get("answer_correctness_claim") or 0) for r in rows)
    n_correct_answered = sum(int(r.get("answer_correctness") or 0) for r in answered)
    n_unsupported = sum(int(r.get("unsupported_emitted") or 0) for r in rows)
    confidences = [float(r["confidence"]) for r in rows if r.get("confidence") is not None]
    stored_v = [
        float(r["faithfulness_stored_verification_score"])
        for r in rows
        if r.get("faithfulness_stored_verification_score") is not None
    ]
    return {
        "n": n,
        "n_answer": n_answer,
        "n_abstain": n_abstain,
        "coverage": (n_answer / n) if n else 0.0,
        "abstention_rate": (n_abstain / n) if n else 0.0,
        "answer_correctness": (n_correct_displayed / n) if n else 0.0,
        "answer_correctness_claim": (n_correct_claim / n) if n else 0.0,
        "selective_accuracy": (n_correct_answered / n_answer) if n_answer else None,
        "n_correct_displayed": n_correct_displayed,
        "n_correct_claim": n_correct_claim,
        "n_correct_answered": n_correct_answered,
        "unsupported_emitted_rate": (n_unsupported / n) if n else 0.0,
        "faithfulness": mean([float(r["faithfulness"]) for r in rows]),
        "faithfulness_stored_verification_score": mean(stored_v),
        "context_precision": mean([float(r["context_precision"]) for r in rows]),
        "context_recall": mean([float(r["context_recall"]) for r in rows]),
        "context_recall_numeric": mean([float(r["context_recall_numeric"]) for r in rows]),
        "mean_confidence": mean(confidences),
        "mean_latency_seconds": mean(
            [float(r["latency_seconds"]) for r in rows if r.get("latency_seconds") is not None]
        ),
    }
