"""Write Phase 17 tables, figures, and interpretation. Does not touch raw JSONL."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from src.statistics.constants import JUDGE_METRIC_LABEL, LOCKED_T


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        if (abs(value) != 0 and abs(value) < 1e-4) or abs(value) >= 1e4:
            return f"{value:.6g}"
        return f"{value:.{digits}f}"
    return str(value)


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _fmt(row.get(k)) if not isinstance(row.get(k), str) else row.get(k) for k in fieldnames})


def _test_row(row: dict[str, Any]) -> dict[str, Any]:
    ci_left = row.get("ci_left") or {}
    ci_right = row.get("ci_right") or {}
    shapiro = row.get("shapiro") or {}
    return {
        "id": row.get("id"),
        "rq": row.get("rq"),
        "family": row.get("family"),
        "role": row.get("role"),
        "left": row.get("left") or row.get("label_left") or "",
        "right": row.get("right") or row.get("label_right") or "",
        "outcome": row.get("outcome"),
        "layer": row.get("layer"),
        "unit": row.get("unit"),
        "n": row.get("n") or row.get("n_left"),
        "n_right": row.get("n_right"),
        "n11_both_positive": row.get("n11_both_positive"),
        "n10_left_only": row.get("n10_left_only"),
        "n01_right_only": row.get("n01_right_only"),
        "n00_both_negative": row.get("n00_both_negative"),
        "n_discordant": row.get("n_discordant"),
        "n_nonzero_differences": row.get("n_nonzero_differences"),
        "mean_left": row.get("mean_left"),
        "mean_right": row.get("mean_right"),
        "mean_difference": row.get("mean_difference"),
        "sd_difference": row.get("sd_difference"),
        "ci95_diff_low": row.get("ci95_diff_low"),
        "ci95_diff_high": row.get("ci95_diff_high"),
        "test": row.get("test") or row.get("selected_test"),
        "statistic_name": row.get("statistic_name"),
        "statistic": row.get("statistic"),
        "df": row.get("df") or row.get("t_df"),
        "p_value": row.get("p_value"),
        "p_value_holm": row.get("p_value_holm"),
        "significant_holm_0.05": row.get("significant_holm_0.05"),
        "t_statistic": row.get("t_statistic"),
        "t_p_value": row.get("t_p_value"),
        "chi2_continuity": row.get("chi2_continuity"),
        "effect_cohens_g": row.get("effect_cohens_g"),
        "effect_odds_ratio_haldane": row.get("effect_odds_ratio_haldane"),
        "effect_cohens_dz": row.get("effect_cohens_dz"),
        "effect_rank_biserial": row.get("effect_rank_biserial") or row.get("effect_rank_biserial_approx"),
        "shapiro_p": shapiro.get("p_value"),
        "shapiro_normality_ok": shapiro.get("normality_ok"),
        "wilson_left_low": ci_left.get("ci_low"),
        "wilson_left_high": ci_left.get("ci_high"),
        "wilson_right_low": ci_right.get("ci_low"),
        "wilson_right_high": ci_right.get("ci_high"),
        "note": row.get("note") or "",
    }


TEST_FIELDS = [
    "id", "rq", "family", "role", "left", "right", "outcome", "layer", "unit",
    "n", "n_right", "n11_both_positive", "n10_left_only", "n01_right_only", "n00_both_negative",
    "n_discordant", "n_nonzero_differences", "mean_left", "mean_right", "mean_difference",
    "sd_difference", "ci95_diff_low", "ci95_diff_high", "test", "statistic_name", "statistic",
    "df", "p_value", "p_value_holm", "significant_holm_0.05", "t_statistic", "t_p_value",
    "chi2_continuity", "effect_cohens_g", "effect_odds_ratio_haldane", "effect_cohens_dz",
    "effect_rank_biserial", "shapiro_p", "shapiro_normality_ok",
    "wilson_left_low", "wilson_left_high", "wilson_right_low", "wilson_right_high", "note",
]


def _descriptive_rows(descriptive: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in descriptive:
        disp = row["displayed_correctness"]
        claim = row["claim_correctness"]
        sel = row["selective_accuracy"]
        cov = row["coverage_wilson"]
        uns = row["unsupported_emitted"]
        llm = row["llm_faithfulness_all"]
        ov = row["token_overlap"]
        out.append({
            "architecture": row["architecture"],
            "label": row["label"],
            "n": row["n"],
            "n_answer": row["n_answer"],
            "n_abstain": row["n_abstain"],
            "coverage": row["coverage"],
            "coverage_ci_low": cov["ci_low"],
            "coverage_ci_high": cov["ci_high"],
            "abstention_rate": row["abstention_rate"],
            "displayed_correct_k": row["displayed_correct_k"],
            "displayed_correctness": disp["mean"],
            "displayed_ci_low": disp["ci_low"],
            "displayed_ci_high": disp["ci_high"],
            "claim_correct_k": row["claim_correct_k"],
            "claim_correctness": claim["mean"],
            "claim_ci_low": claim["ci_low"],
            "claim_ci_high": claim["ci_high"],
            "selective_accuracy": sel["mean"],
            "selective_ci_low": sel["ci_low"],
            "selective_ci_high": sel["ci_high"],
            "unsupported_emitted": uns["mean"],
            "unsupported_ci_low": uns["ci_low"],
            "unsupported_ci_high": uns["ci_high"],
            "llm_faithfulness_mean": llm["mean"],
            "llm_faithfulness_sd": llm["sd"],
            "llm_faithfulness_ci_low": llm["ci_low"],
            "llm_faithfulness_ci_high": llm["ci_high"],
            "token_overlap_mean": ov["mean"],
            "token_overlap_sd": ov["sd"],
            "context_precision_mean": row["context_precision"]["mean"],
            "context_recall_mean": row["context_recall"]["mean"],
            "confidence_mean": row["confidence"]["mean"],
            "confidence_sd": row["confidence"]["sd"],
        })
    return out


def _md_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    header = "| " + " | ".join(title for title, _ in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, sep]
    for row in rows:
        cells = []
        for _, key in columns:
            val = row.get(key)
            cells.append(_fmt(val) if not isinstance(val, str) else val)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_markdown(result: dict[str, Any], path: Path) -> None:
    interp = result["interpretation"]
    desc_rows = _descriptive_rows(result["descriptive"])
    tests = [_test_row(t) for t in result["tests"]]
    lines = [
        "# Phase 17 statistical results",
        "",
        "CPU analysis of frozen Phase 15/16 artefacts. No RAG rerun. No Qwen generation. No new judge calls.",
        "",
        f"**Statistical unit:** {interp['statistical_unit']}",
        "",
        f"**Locked T:** {LOCKED_T} (DEV 40 only; not retuned on the frozen 140).",
        "",
        f"**RQ2 metric label:** `{JUDGE_METRIC_LABEL}` — **not official RAGAS.**",
        "",
        "## Descriptive rates (Wilson 95% CI)",
        "",
        _md_table(desc_rows, [
            ("Architecture", "label"),
            ("Displayed correct", "displayed_correct_k"),
            ("Displayed acc.", "displayed_correctness"),
            ("95% CI low", "displayed_ci_low"),
            ("95% CI high", "displayed_ci_high"),
            ("Coverage", "coverage"),
            ("Selective acc.", "selective_accuracy"),
            ("Unsupported emitted", "unsupported_emitted"),
            ("LLM faithfulness mean", "llm_faithfulness_mean"),
        ]),
        "",
        "## Hypothesis tests",
        "",
        "Holm–Bonferroni adjustment is within each family. Do not claim significance unless `significant_holm_0.05` is true.",
        "",
        _md_table(tests, [
            ("ID", "id"),
            ("RQ", "rq"),
            ("Role", "role"),
            ("Test", "test"),
            ("n", "n"),
            ("Statistic", "statistic"),
            ("p", "p_value"),
            ("p Holm", "p_value_holm"),
            ("Sig. Holm 0.05", "significant_holm_0.05"),
            ("Effect", "effect_cohens_g"),
        ]),
        "",
        "## RQ1 interpretation",
        "",
        interp["rq1"],
        "",
        "## RQ2 interpretation",
        "",
        interp["rq2"],
        "",
        "## RQ3 interpretation",
        "",
        interp["rq3"],
        "",
        "## Retrieval control",
        "",
        result["retrieval_control"]["note"],
        "",
        "## Limitations",
        "",
    ]
    for item in interp["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_plots(result: dict[str, Any], fig_dir: Path) -> list[str]:
    """Redraw dissertation figures from saved Phase 17 tables. Does not recompute tests."""
    from src.config import project_root
    from src.statistics.figures import render_from_saved

    del result, fig_dir
    written = render_from_saved(project_root())
    return [path for paths in written.values() for path in paths]


def write_outputs(result: dict[str, Any], root: Path) -> dict[str, str]:
    metrics = root / "results" / "metrics"
    config = root / "results" / "config"
    final = root / "results" / "final"
    fig_dir = metrics / "phase17_figures"
    metrics.mkdir(parents=True, exist_ok=True)
    config.mkdir(parents=True, exist_ok=True)
    final.mkdir(parents=True, exist_ok=True)

    desc_rows = _descriptive_rows(result["descriptive"])
    test_rows = [_test_row(t) for t in result["tests"]]
    desc_fields = list(desc_rows[0].keys())
    desc_csv = metrics / "phase17_descriptive.csv"
    tests_csv = metrics / "phase17_tests.csv"
    effects_csv = metrics / "phase17_effect_sizes.csv"
    assume_csv = metrics / "phase17_assumptions.csv"
    _write_csv(desc_csv, desc_rows, desc_fields)
    _write_csv(tests_csv, test_rows, TEST_FIELDS)
    effect_fields = [
        "id", "rq", "family", "left", "right", "effect_cohens_g",
        "effect_odds_ratio_haldane", "effect_cohens_dz", "effect_rank_biserial",
        "mean_difference", "p_value_holm", "significant_holm_0.05",
    ]
    _write_csv(effects_csv, test_rows, effect_fields)
    assume_rows = []
    for item in result["assumptions"]:
        sh = item["shapiro"]
        assume_rows.append({
            "name": item["name"],
            "metric": item.get("metric"),
            "n": sh.get("n"),
            "shapiro_statistic": sh.get("statistic"),
            "shapiro_p_value": sh.get("p_value"),
            "normality_ok": sh.get("normality_ok"),
            "note": sh.get("note") or (
                "Paired-difference normality acceptable; t-test may be used as sensitivity."
                if sh.get("normality_ok")
                else "Paired-difference normality not met; Wilcoxon/McNemar preferred."
            ),
        })
    _write_csv(assume_csv, assume_rows, list(assume_rows[0].keys()))

    md_path = metrics / "phase17_summary.md"
    write_markdown(result, md_path)
    interp_path = final / "phase17_interpretation.md"
    interp_path.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")

    slim = {k: v for k, v in result.items() if k != "series"}
    summary_json = config / "phase17_statistics_summary.json"
    summary_json.write_text(json.dumps(_jsonable(slim), indent=2) + "\n", encoding="utf-8")

    figures = write_plots(result, fig_dir)
    return {
        "descriptive_csv": str(desc_csv),
        "tests_csv": str(tests_csv),
        "effects_csv": str(effects_csv),
        "assumptions_csv": str(assume_csv),
        "summary_md": str(md_path),
        "interpretation_md": str(interp_path),
        "summary_json": str(summary_json),
        "figures": figures,
    }
