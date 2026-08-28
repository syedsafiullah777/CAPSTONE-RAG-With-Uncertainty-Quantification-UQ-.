"""Phase 17 constants. Frozen artefact hashes only — do not retune T or freeze files."""

from __future__ import annotations

PHASE = 17
N_QUESTIONS = 140
N_CASES = 420
ALPHA = 0.05
BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 42

ARCH_SA = "single_agent"
ARCH_MA = "multi_agent"
ARCH_UQ = "multi_agent_uq"
ARCHITECTURES = (ARCH_SA, ARCH_MA, ARCH_UQ)
ARCH_LABELS = {
    ARCH_SA: "Single-Agent",
    ARCH_MA: "Multi-Agent",
    ARCH_UQ: "Multi-Agent + UQ",
}

JUDGE_METRIC_LABEL = "LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)"
LOCKED_T = 0.65

PROCESSED_REL = "results/processed/phase16_cases.jsonl"
JUDGE_REL = (
    "results/raw/phase16_judge/"
    "phase16_judge_20260828T152623Z_06661255/judge.jsonl"
)
PHASE15_REL = "results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl"
FROZEN_140_REL = "data/final/selected_140_questions.csv"
CAL_40_REL = "data/calibration/calibration_questions.csv"
LOCK_REL = "results/config/threshold.lock.json"

EXPECTED_PHASE15_SHA256 = "f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa"
EXPECTED_PROCESSED_SHA256 = "e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91"
EXPECTED_JUDGE_SHA256 = "093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3"
EXPECTED_FROZEN140_SHA256 = "88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087"
EXPECTED_CAL40_SHA256 = "1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845"
EXPECTED_LOCK_SHA256 = "8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88"

FORBIDDEN_IMPORT_MODULES = {
    "llama_cpp",
    "src.run.benchmark",
    "src.rag.single_agent",
    "src.rag.multi_agent",
    "src.rag.multi_agent_uq",
    "src.models.factory",
    "src.evaluation.judge_runner",
}
