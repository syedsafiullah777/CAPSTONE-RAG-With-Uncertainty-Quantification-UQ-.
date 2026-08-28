"""Phase 18 pipeline: taxonomy on 420 cases + stratified qualitative sample."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.config import project_root
from src.error_analysis.constants import ARCH_LABELS, EXCERPT_CHARS
from src.error_analysis.explain import _clip, explain_case
from src.error_analysis.load import load_universe
from src.error_analysis.report import CASE_FIELDS, summarise, write_markdown, _write_csv
from src.error_analysis.sample import select_sample
from src.error_analysis.taxonomy import assign_category
from src.statistics.load import sha256_file


def _row(case: dict[str, Any], assigned: dict[str, Any], strata: list[str], in_sample: bool) -> dict[str, Any]:
    return {
        "question_id": case["question_id"],
        "architecture": case["architecture"],
        "architecture_label": ARCH_LABELS[case["architecture"]],
        "case_key": case["case_key"],
        "in_qualitative_sample": "true" if in_sample else "false",
        "sample_strata": ";".join(strata),
        "displayed_correct": case["displayed_correct"],
        "claim_correct": case["claim_correct"],
        "decision": case["decision"],
        "confidence": "" if case.get("confidence") is None else f"{float(case['confidence']):.6f}",
        "threshold": "" if case.get("threshold") is None else case["threshold"],
        "llm_faithfulness": f"{float(case['llm_faithfulness']):.4f}",
        "token_overlap": f"{float(case['token_overlap']):.4f}",
        "context_precision": f"{float(case['context_precision']):.4f}",
        "context_recall": f"{float(case['context_recall']):.4f}",
        "context_recall_numeric": case["context_recall_numeric"],
        "verification_status": case.get("verification_status") or "",
        "verification_score": (
            "" if case.get("verification_score") is None else f"{float(case['verification_score']):.4f}"
        ),
        "n_evidence": case["n_evidence"],
        "gold_program_answer": case.get("gold_program_answer") or "",
        "gold_file_name": case.get("gold_file_name") or "",
        "retrieved_files": " | ".join(case.get("retrieved_files") or []),
        "primary_category": assigned["primary_category"],
        "error_layer": assigned["error_layer"],
        "tags": ";".join(assigned["tags"]),
        "explanation": explain_case(case, assigned) if in_sample else "",
        "question_excerpt": _clip(case.get("question") or "", EXCERPT_CHARS) if in_sample else "",
        "displayed_answer_excerpt": _clip(case.get("displayed_answer") or "", EXCERPT_CHARS) if in_sample else "",
        "draft_excerpt": _clip(case.get("draft_answer") or "", EXCERPT_CHARS) if in_sample else "",
    }


def run_error_analysis(root: Path | None = None) -> dict[str, Any]:
    root = root or project_root()
    watched = [
        root / "results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl",
        root / "results/processed/phase16_cases.jsonl",
        root / "results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl",
        root / "results/metrics/phase17_tests.csv",
        root / "results/config/phase17_statistics_summary.json",
    ]
    before = {str(path): sha256_file(path) for path in watched if path.is_file()}
    universe = load_universe(root)
    sample = select_sample(universe)
    assigned_by_key = {case["case_key"]: assign_category(case) for case in universe["cases"]}

    all_rows = []
    sample_rows = []
    for case in universe["cases"]:
        key = case["case_key"]
        in_sample = key in sample["strata_by_case"]
        row = _row(case, assigned_by_key[key], sample["strata_by_case"].get(key, []), in_sample)
        all_rows.append(row)
        if in_sample:
            sample_rows.append(row)

    summary_rows = summarise(all_rows)
    analysis_dir = root / "results" / "analysis"
    cases_csv = analysis_dir / "phase18_error_cases.csv"
    summary_csv = analysis_dir / "phase18_error_summary.csv"
    md_path = root / "results" / "final" / "phase18_error_analysis.md"
    _write_csv(cases_csv, all_rows, CASE_FIELDS)
    _write_csv(summary_csv, summary_rows, [
        "architecture", "architecture_label", "primary_category", "n",
        "n_architecture", "pct_of_architecture", "scope",
    ])
    write_markdown(
        md_path,
        n_sample=sample["n_cases"],
        n_sample_questions=sample["n_questions"],
        sample_method=sample["method"],
        summary_rows=summary_rows,
        sample_rows=sample_rows,
        hashes=universe["hashes"],
    )
    after = {str(path): sha256_file(path) for path in watched if path.is_file()}
    if before != after:
        raise RuntimeError("Phase 18 must not modify Phase 15/16/17 source artefacts")
    return {
        "n_cases": len(all_rows),
        "n_sample": sample["n_cases"],
        "n_sample_questions": sample["n_questions"],
        "seed": sample["seed"],
        "false_abstentions_in_sample": sum(
            1 for r in sample_rows if r["primary_category"] == "incorrect_abstention"
        ),
        "paths": {
            "cases_csv": str(cases_csv),
            "summary_csv": str(summary_csv),
            "markdown": str(md_path),
        },
        "hashes": universe["hashes"],
        "used_rag_rerun": False,
        "source_artefacts_unchanged": True,
    }
