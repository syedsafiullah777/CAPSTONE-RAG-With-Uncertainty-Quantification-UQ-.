"""Phase 18 error analysis. Frozen artefacts only; no RAG/Qwen/judge/stats rerun."""

from __future__ import annotations

import ast
from pathlib import Path

from src.evaluation.runner import sha256_file
from src.error_analysis.constants import (
    EXPECTED_JUDGE_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
    FORBIDDEN_ERROR_ANALYSIS_IMPORTS,
    SAMPLE_SEED,
)
from src.error_analysis.taxonomy import assign_category


def test_taxonomy_false_abstention_precedes_numeric_error() -> None:
    row = assign_category({
        "answered": False,
        "displayed_correct": 0,
        "claim_correct": 1,
        "context_recall": 0.0,
        "context_recall_numeric": 0,
        "llm_faithfulness": 0.9,
        "displayed_answer": "Evidence is insufficient.",
        "confidence": 0.60,
        "verification_status": "VERIFIED",
        "context_precision": 0.5,
        "architecture": "multi_agent_uq",
    })
    assert row["primary_category"] == "incorrect_abstention"
    assert row["error_layer"] == "abstention"


def test_taxonomy_does_not_call_numeric_error_hallucination() -> None:
    row = assign_category({
        "answered": True,
        "displayed_correct": 0,
        "claim_correct": 0,
        "context_recall": 1.0,
        "context_recall_numeric": 1,
        "llm_faithfulness": 0.8,
        "displayed_answer": "The ROI is 12.5.",
        "confidence": 0.80,
        "verification_status": "VERIFIED",
        "context_precision": 0.5,
        "architecture": "multi_agent",
    })
    assert row["primary_category"] == "incorrect_numerical_reasoning"
    assert "hallucination" not in row["primary_category"]
    assert "false_confidence" in row["tags"]


def test_error_analysis_modules_do_not_import_rag() -> None:
    imported: set[str] = set()
    pkg = Path("src/error_analysis")
    for py in pkg.glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    assert not (imported & FORBIDDEN_ERROR_ANALYSIS_IMPORTS)
    text = "\n".join(p.read_text(encoding="utf-8") for p in pkg.glob("*.py"))
    for banned in ("run_single_agent", "run_multi_agent_uq", "create_backend", "llama_cpp"):
        assert banned not in text


def test_run_error_analysis_does_not_rewrite_raw() -> None:
    from src.error_analysis.pipeline import run_error_analysis

    phase15 = Path("results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl")
    processed = Path("results/processed/phase16_cases.jsonl")
    judge = Path("results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl")
    tests_csv = Path("results/metrics/phase17_tests.csv")
    watched = (phase15, processed, judge, tests_csv)
    before = {p: sha256_file(p) for p in watched}
    result = run_error_analysis()
    after = {p: sha256_file(p) for p in watched}
    assert before == after
    assert result["n_cases"] == 420
    assert result["n_sample"] >= 20
    assert result["seed"] == SAMPLE_SEED
    assert result["false_abstentions_in_sample"] == 2
    assert result["used_rag_rerun"] is False
    cases_csv = Path("results/analysis/phase18_error_cases.csv")
    summary_csv = Path("results/analysis/phase18_error_summary.csv")
    md = Path("results/final/phase18_error_analysis.md")
    assert cases_csv.is_file() and summary_csv.is_file() and md.is_file()
    text = md.read_text(encoding="utf-8")
    assert "not official RAGAS" in text
    assert "hallucination" in text.lower()
    assert sha256_file(phase15) == EXPECTED_PHASE15_SHA256
    assert sha256_file(processed) == EXPECTED_PROCESSED_SHA256
    assert sha256_file(judge) == EXPECTED_JUDGE_SHA256
