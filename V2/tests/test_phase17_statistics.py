"""Phase 17 statistics. Frozen Phase 15/16 only; no RAG/Qwen/judge rerun."""

from __future__ import annotations

import ast
from pathlib import Path

from src.evaluation.runner import sha256_file
from src.statistics.constants import (
    EXPECTED_JUDGE_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
    FORBIDDEN_IMPORT_MODULES,
    N_CASES,
    N_QUESTIONS,
)
from src.statistics.tests import holm_adjust, mcnemar_exact, significant, wilson_ci


def test_wilson_known_value() -> None:
    ci = wilson_ci(32, 140)
    assert ci["mean"] == 32 / 140
    assert 0 < ci["ci_low"] < ci["mean"] < ci["ci_high"] < 1


def test_mcnemar_symmetric_is_not_significant() -> None:
    left = [1, 1, 0, 0, 1, 0]
    right = [1, 0, 1, 0, 1, 0]
    result = mcnemar_exact(left, right)
    assert result["n"] == 6
    assert result["n10_left_only"] == 1
    assert result["n01_right_only"] == 1
    assert result["p_value"] == 1.0
    n_sum = (
        result["n11_both_positive"]
        + result["n10_left_only"]
        + result["n01_right_only"]
        + result["n00_both_negative"]
    )
    assert n_sum == 6


def test_holm_adjusts_and_is_monotone() -> None:
    raw = [0.01, 0.04, 0.03]
    adj = holm_adjust(raw)
    assert adj[0] == 0.03
    assert all(a + 1e-12 >= r for a, r in zip(adj, raw))
    assert significant(0.049)
    assert not significant(0.05)


def test_statistics_modules_do_not_import_rag() -> None:
    imported: set[str] = set()
    stats_dir = Path("src/statistics")
    for py in stats_dir.glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    assert not (imported & FORBIDDEN_IMPORT_MODULES)
    text = "\n".join(p.read_text(encoding="utf-8") for p in stats_dir.glob("*.py"))
    for banned in ("run_single_agent", "run_multi_agent_uq", "create_backend"):
        assert banned not in text


def test_frozen_hashes_unchanged() -> None:
    phase15 = Path("results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl")
    processed = Path("results/processed/phase16_cases.jsonl")
    judge = Path(
        "results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl"
    )
    assert sha256_file(phase15) == EXPECTED_PHASE15_SHA256
    assert sha256_file(processed) == EXPECTED_PROCESSED_SHA256
    assert sha256_file(judge) == EXPECTED_JUDGE_SHA256


def test_analyse_paired_140_and_does_not_rewrite_raw() -> None:
    from src.statistics.analysis import analyse

    phase15 = Path("results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl")
    judge = Path(
        "results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl"
    )
    processed = Path("results/processed/phase16_cases.jsonl")
    before = {p: sha256_file(p) for p in (phase15, judge, processed)}
    result = analyse()
    after = {p: sha256_file(p) for p in (phase15, judge, processed)}
    assert before == after
    assert result["n_questions"] == N_QUESTIONS
    assert result["n_cases"] == N_CASES
    assert result["threshold"] == 0.65
    assert result["source"]["used_rag_rerun"] is False
    rq1 = result["rq1_confirmatory"][0]
    assert rq1["n"] == 140
    n_sum = (
        rq1["n11_both_positive"]
        + rq1["n10_left_only"]
        + rq1["n01_right_only"]
        + rq1["n00_both_negative"]
    )
    assert n_sum == 140
    desc = {row["architecture"]: row for row in result["descriptive"]}
    assert desc["single_agent"]["displayed_correct_k"] == 32
    assert desc["multi_agent"]["displayed_correct_k"] == 29
    assert desc["multi_agent_uq"]["n_answer"] == 78
    assert desc["multi_agent_uq"]["n_abstain"] == 62
    assert result["retrieval_control"]["context_precision_identical"] is True
    assert "official RAGAS" not in result["judge_metric_label"]
    assert result["judge_metric_label"].startswith("LLM-as-judge faithfulness")


PHASE17_RESULT_FILES = (
    Path("results/metrics/phase17_descriptive.csv"),
    Path("results/metrics/phase17_tests.csv"),
    Path("results/metrics/phase17_effect_sizes.csv"),
    Path("results/metrics/phase17_assumptions.csv"),
    Path("results/metrics/phase17_summary.md"),
    Path("results/config/phase17_statistics_summary.json"),
    Path("results/final/phase17_interpretation.md"),
)


def test_render_figures_does_not_change_results() -> None:
    from src.statistics.figures import APPENDIX, PRIMARY, render_from_saved

    frozen = [
        Path("results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl"),
        Path("results/processed/phase16_cases.jsonl"),
        Path("results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl"),
    ]
    watched = PHASE17_RESULT_FILES + tuple(frozen)
    before = {path: sha256_file(path) for path in watched}
    written = render_from_saved()
    after = {path: sha256_file(path) for path in watched}
    assert before == after
    fig_dir = Path("results/metrics/phase17_figures")
    for stem in PRIMARY + APPENDIX:
        for ext in (".png", ".pdf", ".svg"):
            path = fig_dir / f"{stem}{ext}"
            assert path.is_file(), path
            assert path.stat().st_size > 0
    assert set(written) == set(PRIMARY + APPENDIX)
