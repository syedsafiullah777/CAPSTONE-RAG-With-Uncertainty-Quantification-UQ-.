"""Phase 18 constants. Read-only frozen artefacts; no retuning."""

from __future__ import annotations

from src.statistics.constants import (
    ARCH_LABELS,
    ARCH_MA,
    ARCH_SA,
    ARCH_UQ,
    ARCHITECTURES,
    EXPECTED_JUDGE_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
    FORBIDDEN_IMPORT_MODULES,
    JUDGE_METRIC_LABEL,
    LOCKED_T,
    N_CASES,
    N_QUESTIONS,
)

PHASE = 18
SAMPLE_SEED = 18
FAITHFULNESS_LOW = 0.5  # taxonomy split only; not a calibrated operating threshold
HIGH_CONFIDENCE = LOCKED_T
EXCERPT_CHARS = 220

PRIMARY_CATEGORIES = (
    "correct_answer",
    "appropriate_abstention",
    "incorrect_abstention",
    "retrieval_failure",
    "non_numeric_answer",
    "incorrect_numerical_reasoning",
    "unsupported_claim",
    "incorrect_despite_partial_evidence",
)

FORBIDDEN_ERROR_ANALYSIS_IMPORTS = FORBIDDEN_IMPORT_MODULES | {
    "src.statistics.analysis",
    "src.evaluation.judge_runner",
}
