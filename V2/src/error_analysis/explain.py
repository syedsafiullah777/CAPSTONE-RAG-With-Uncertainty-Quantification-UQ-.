"""Evidence-based case explanations. Only recorded fields; no invented causes."""

from __future__ import annotations

from typing import Any

from src.error_analysis.constants import ARCH_LABELS, EXCERPT_CHARS, JUDGE_METRIC_LABEL, LOCKED_T


def _clip(text: str, n: int = EXCERPT_CHARS) -> str:
    text = " ".join(str(text or "").split())
    if len(text) <= n:
        return text
    return text[: n - 1] + "…"


def explain_case(case: dict[str, Any], assigned: dict[str, Any]) -> str:
    arch = ARCH_LABELS[case["architecture"]]
    primary = assigned["primary_category"]
    gold = case.get("gold_program_answer")
    rec = case["context_recall"]
    prec = case["context_precision"]
    llm = case["llm_faithfulness"]
    files = ", ".join(case.get("retrieved_files") or []) or "(none)"
    gold_file = case.get("gold_file_name") or "(missing)"
    verify = case.get("verification_status") or "not recorded (Single-Agent has no verifier)"
    conf = case.get("confidence")
    conf_s = "n/a" if conf is None else f"{float(conf):.4f}"
    parts = [
        f"{arch}; decision={case['decision']}; displayed_correct={case['displayed_correct']}; "
        f"claim_correct={case['claim_correct']}.",
        f"Gold program_answer={gold}; gold file={gold_file}.",
        f"Retrieved files ({case['n_evidence']} chunks, scores={case.get('retrieval_scores')}): {files}.",
        f"context_recall={rec:.2f} (gold file/context_id in top-k); "
        f"context_precision={prec:.2f}; gold number in evidence={bool(case['context_recall_numeric'])}.",
        f"{JUDGE_METRIC_LABEL}={llm:.4f} (not official RAGAS). "
        f"Verification status={verify}. Confidence={conf_s}; locked T={LOCKED_T:.2f}.",
    ]
    why = {
        "correct_answer": "Displayed text matches the gold number within the FinQA numeric tolerance.",
        "appropriate_abstention": (
            "UQ ABSTAIN at locked T=0.65 and the withheld draft is numerically incorrect, "
            "so abstention is appropriate on the recorded claim."
        ),
        "incorrect_abstention": (
            "UQ ABSTAIN at locked T=0.65 but the withheld draft matches the gold number. "
            "This is a false abstention (correct draft withheld)."
        ),
        "retrieval_failure": (
            "Displayed answer is numerically incorrect and context_recall=0, so the gold file/"
            "context_id was not in the retrieved top-k. Shared retrieval is identical across architectures."
        ),
        "non_numeric_answer": (
            "The system emitted ANSWER but the displayed text contains no parseable number, "
            "so it cannot match the FinQA gold. This is a format/refusal issue, not a labelled hallucination."
        ),
        "incorrect_numerical_reasoning": (
            "The gold number is present in the retrieved evidence text, but the displayed numeric "
            "answer does not match. This indicates incorrect numerical reasoning or extraction, "
            "not a retrieval miss."
        ),
        "unsupported_claim": (
            f"ANSWER is numerically incorrect, the gold number is not in the evidence text, and "
            f"LLM-as-judge faithfulness is below {0.5:.1f}. Treated as unsupported emission "
            "(not called hallucination unless independent evidence showed fabrication)."
        ),
        "incorrect_despite_partial_evidence": (
            "ANSWER is numerically incorrect. The gold file/context was retrieved (recall=1) but the "
            "gold number is not in the chunk text; judge faithfulness is not low. Residual numeric error "
            "with partial document match — not labelled hallucination."
        ),
    }[primary]
    parts.append("Category rule: " + why)
    parts.append("Question: " + _clip(case.get("question") or ""))
    parts.append("Displayed answer: " + _clip(case.get("displayed_answer") or ""))
    if case.get("draft_answer"):
        parts.append("UQ draft: " + _clip(case["draft_answer"]))
    return " ".join(parts)
