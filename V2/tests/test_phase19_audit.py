"""Phase 19 reproducibility audit. Frozen artefacts only; no RAG/Qwen/judge/stats rerun."""

from __future__ import annotations

import ast
from pathlib import Path

from src.audit import FORBIDDEN_AUDIT_IMPORTS, verify_audit_does_not_import_generation
from src.evaluation.runner import sha256_file
from src.statistics.constants import (
    EXPECTED_JUDGE_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
)


def test_audit_modules_do_not_import_generation() -> None:
    verify_audit_does_not_import_generation()
    imported: set[str] = set()
    pkg = Path("src/audit")
    for py in pkg.glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    assert not (imported & FORBIDDEN_AUDIT_IMPORTS)
    text = "\n".join(p.read_text(encoding="utf-8") for p in pkg.glob("*.py"))
    for banned in ("run_single_agent", "run_multi_agent_uq", "create_backend", "llama_cpp", "analyse"):
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


def test_run_audit_does_not_rewrite_raw() -> None:
    from src.audit.checks import run_audit

    phase15 = Path("results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl")
    processed = Path("results/processed/phase16_cases.jsonl")
    judge = Path(
        "results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl"
    )
    tests_csv = Path("results/metrics/phase17_tests.csv")
    watched = (phase15, processed, judge, tests_csv)
    before = {p: sha256_file(p) for p in watched}
    result = run_audit()
    after = {p: sha256_file(p) for p in watched}
    assert before == after
    assert result["used_rag_rerun"] is False
    assert result["recomputed_statistics"] is False
    assert result["overall"] in {"PASS", "NEEDS VERIFICATION", "FAIL"}
    assert result["n_fail"] >= 0
