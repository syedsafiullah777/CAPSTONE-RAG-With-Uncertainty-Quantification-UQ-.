"""Dissertation figures from saved Phase 17 tables. Does not recompute tests."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.config import project_root
from src.statistics.constants import (
    ARCH_LABELS,
    ARCH_MA,
    ARCH_SA,
    ARCH_UQ,
    ARCHITECTURES,
    JUDGE_METRIC_LABEL,
    LOCKED_T,
    N_QUESTIONS,
)
from src.statistics.load import load_joined, series

COLOR_SA = "#4C72B0"
COLOR_MA = "#DD8452"
COLOR_UQ = "#55A868"
COLOR_ABSTAIN = "#C44E52"
ARCH_COLORS = {ARCH_SA: COLOR_SA, ARCH_MA: COLOR_MA, ARCH_UQ: COLOR_UQ}
DPI = 300

PRIMARY = (
    "rq1_accuracy_wilson_ci",
    "rq2_confidence_vs_faithfulness",
    "rq3_coverage_selective",
)
APPENDIX = (
    "rq1_mcnemar_counts",
    "rq2_llm_faithfulness_box",
    "rq3_uq_outcomes",
)

YLABEL_FAITHFULNESS = (
    "LLM-as-judge faithfulness\n(Qwen3-8B, custom/RAGAS-inspired)"
)


def _style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "normal",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


def _save(fig: plt.Figure, fig_dir: Path, stem: str) -> list[str]:
    fig_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for ext in (".png", ".pdf", ".svg"):
        path = fig_dir / f"{stem}{ext}"
        fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.18)
        written.append(str(path))
    plt.close(fig)
    return written


def _caption(fig: plt.Figure, text: str) -> None:
    fig.text(0.02, 0.01, text, ha="left", va="bottom", fontsize=8.2, wrap=False)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def _fmt_sci(value: float, digits: int = 3) -> str:
    mantissa, exp = f"{value:.{digits}e}".split("e")
    return rf"{mantissa} \times 10^{{{int(exp)}}}"


def _load_saved(root: Path) -> dict:
    desc_rows = _read_csv(root / "results" / "metrics" / "phase17_descriptive.csv")
    desc = {row["architecture"]: row for row in desc_rows}
    tests = {row["id"]: row for row in _read_csv(root / "results" / "metrics" / "phase17_tests.csv")}
    summary = json.loads(
        (root / "results" / "config" / "phase17_statistics_summary.json").read_text(encoding="utf-8")
    )
    joined = load_joined(root)
    llm_by_arch = {
        arch: [float(v) for v in series(joined, arch, "llm_faithfulness")]
        for arch in ARCHITECTURES
    }
    uq_answered = np.array(
        [1 if v else 0 for v in series(joined, ARCH_UQ, "answered")],
        dtype=int,
    )
    uq_conf = np.asarray(series(joined, ARCH_UQ, "confidence"), dtype=float)
    uq_llm = np.asarray(series(joined, ARCH_UQ, "llm_faithfulness"), dtype=float)
    if uq_conf.size != N_QUESTIONS:
        raise ValueError(f"Expected {N_QUESTIONS} UQ cases, found {uq_conf.size}")
    return {
        "desc": desc,
        "tests": tests,
        "summary": summary,
        "llm_by_arch": llm_by_arch,
        "uq_conf": uq_conf,
        "uq_llm": uq_llm,
        "uq_answered": uq_answered,
    }


def _fig1(data: dict, fig_dir: Path) -> list[str]:
    desc = data["desc"]
    labels = [ARCH_LABELS[a] for a in ARCHITECTURES]
    colors = [ARCH_COLORS[a] for a in ARCHITECTURES]
    means = np.array([_f(desc[a], "displayed_correctness") * 100 for a in ARCHITECTURES])
    lows = np.array([_f(desc[a], "displayed_ci_low") * 100 for a in ARCHITECTURES])
    highs = np.array([_f(desc[a], "displayed_ci_high") * 100 for a in ARCHITECTURES])
    ks = [int(float(desc[a]["displayed_correct_k"])) for a in ARCHITECTURES]
    if ks != [32, 29, 32]:
        raise ValueError(f"Unexpected displayed_correct_k {ks}; refusing to draw Figure 1")
    yerr = np.vstack([means - lows, highs - means])
    captions = [
        "32/140 = 22.86%",
        "29/140 = 20.71%",
        "32/140 = 22.86%",
    ]

    fig, ax = plt.subplots(figsize=(7.6, 5.6))
    x = np.arange(3)
    ax.bar(x, means, color=colors, width=0.62, edgecolor="white", linewidth=0.6, zorder=2)
    ax.errorbar(
        x, means, yerr=yerr, fmt="none", ecolor="black",
        elinewidth=1.15, capsize=5, capthick=1.15, zorder=3,
    )
    for i, hi in enumerate(highs):
        ax.text(i, hi + 2.4, captions[i], ha="center", va="bottom", fontsize=9.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Displayed numeric correctness (%)")
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.set_title("RQ1: Answer Correctness by Architecture (95% CI)")
    ax.text(
        0.5, 1.01,
        "n = 140 frozen FinQA test questions per architecture",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=9.5,
    )
    fig.tight_layout(rect=[0, 0.14, 1, 0.96])
    _caption(
        fig,
        "Error bars: Wilson 95% CI on the displayed numeric correctness proportion.\n"
        "Intervals overlap. This figure does not indicate a statistically significant difference.\n"
        "Source: results/metrics/phase17_descriptive.csv (Wilson CIs from Phase 17; T = 0.65 unused for RQ1).",
    )
    return _save(fig, fig_dir, "rq1_accuracy_wilson_ci")


def _fig2(data: dict, fig_dir: Path) -> list[str]:
    conf = data["uq_conf"]
    llm = data["uq_llm"]
    ans = data["uq_answered"]
    if conf.size != N_QUESTIONS:
        raise ValueError(f"Expected {N_QUESTIONS} UQ cases for Figure 2, found {conf.size}")
    rho = float(data["tests"]["rq2_spearman_uq_confidence_vs_llm_faithfulness"]["statistic"])
    p_holm = float(data["tests"]["rq2_spearman_uq_confidence_vs_llm_faithfulness"]["p_value_holm"])
    if abs(rho - 0.6988) > 5e-5:
        raise ValueError(f"Unexpected Spearman rho {rho}; refusing to draw Figure 2")
    n_ans = int(ans.sum())
    n_abs = int(N_QUESTIONS - n_ans)

    fig, ax = plt.subplots(figsize=(7.8, 5.8))
    ax.scatter(
        conf[ans == 1], llm[ans == 1],
        c=COLOR_UQ, marker="o", label=f"ANSWER (n = {n_ans})",
        alpha=0.78, s=38, edgecolors="none", zorder=3,
    )
    ax.scatter(
        conf[ans == 0], llm[ans == 0],
        c=COLOR_ABSTAIN, marker="^", label=f"ABSTAIN (n = {n_abs})",
        alpha=0.78, s=38, edgecolors="none", zorder=3,
    )
    ax.axvline(
        LOCKED_T, color="black", linestyle="--", linewidth=1.2,
        label=f"Locked T = {LOCKED_T:.2f} (DEV 40)", zorder=2,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("UQ confidence")
    ax.set_ylabel(YLABEL_FAITHFULNESS)
    ax.set_title("RQ2: UQ Confidence vs LLM-as-Judge Faithfulness")
    ax.legend(frameon=False, loc="upper left")
    ax.text(
        0.98, 0.04,
        f"Spearman $\\rho$ = {rho:.4f}\n"
        f"Holm-adjusted $p$ = ${_fmt_sci(p_holm)}$\n"
        f"n = {N_QUESTIONS} UQ cases",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9.5,
        bbox={"facecolor": "white", "edgecolor": "#cccccc", "boxstyle": "round,pad=0.35"},
    )
    fig.tight_layout(rect=[0, 0.14, 1, 0.98])
    _caption(
        fig,
        f"Y-axis: {JUDGE_METRIC_LABEL} — not official RAGAS.\n"
        "Vertical line: T = 0.65 locked on a separate 40-question FinQA DEV calibration set (not the frozen 140).\n"
        "Sources: phase17_tests.csv (ρ, Holm p); phase16_cases.jsonl + official judge JSONL (points).",
    )
    return _save(fig, fig_dir, "rq2_confidence_vs_faithfulness")


def _fig3(data: dict, fig_dir: Path) -> list[str]:
    desc = data["desc"]
    labels = [ARCH_LABELS[a] for a in ARCHITECTURES]
    coverage = np.array([_f(desc[a], "coverage") * 100 for a in ARCHITECTURES])
    selective = np.array([_f(desc[a], "selective_accuracy") * 100 for a in ARCHITECTURES])
    cov_lo = np.array([_f(desc[a], "coverage_ci_low") * 100 for a in ARCHITECTURES])
    cov_hi = np.array([_f(desc[a], "coverage_ci_high") * 100 for a in ARCHITECTURES])
    sel_lo = np.array([_f(desc[a], "selective_ci_low") * 100 for a in ARCHITECTURES])
    sel_hi = np.array([_f(desc[a], "selective_ci_high") * 100 for a in ARCHITECTURES])
    n_answer = int(float(desc[ARCH_UQ]["n_answer"]))
    n_correct = int(float(desc[ARCH_UQ]["displayed_correct_k"]))
    if n_answer != 78 or n_correct != 32:
        raise ValueError("Unexpected UQ coverage/selective counts; refusing to draw Figure 3")

    fig, ax = plt.subplots(figsize=(8.2, 5.9))
    x = np.arange(3)
    width = 0.36
    ax.bar(
        x - width / 2, coverage, width,
        label="Coverage (answered / 140)",
        color=COLOR_SA, edgecolor="white", zorder=2,
    )
    ax.bar(
        x + width / 2, selective, width,
        label="Selective accuracy (correct | answered)",
        color=COLOR_UQ, edgecolor="white", zorder=2,
    )
    ax.errorbar(
        x - width / 2, coverage,
        yerr=np.vstack([coverage - cov_lo, cov_hi - coverage]),
        fmt="none", ecolor="black", elinewidth=1.0, capsize=4, zorder=3,
    )
    ax.errorbar(
        x + width / 2, selective,
        yerr=np.vstack([selective - sel_lo, sel_hi - selective]),
        fmt="none", ecolor="black", elinewidth=1.0, capsize=4, zorder=3,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Percentage (%)")
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.set_title("RQ3: Coverage and Selective Accuracy at Locked T=0.65")
    for i in (0, 1):
        ax.text(
            i - width / 2, 50, "100%\nalways\nanswer",
            ha="center", va="center", fontsize=8, color="white",
        )
    ax.text(0 + width / 2, sel_hi[0] + 2.4, "32/140\n= 22.86%", ha="center", va="bottom", fontsize=8)
    ax.text(1 + width / 2, sel_hi[1] + 2.4, "29/140\n= 20.71%", ha="center", va="bottom", fontsize=8)
    ax.text(2 - width / 2, coverage[2] + 2.8, "78/140\n= 55.71%", ha="center", va="bottom", fontsize=8.5)
    ax.text(2 + width / 2, sel_hi[2] + 2.8, "32/78\n= 41.03%", ha="center", va="bottom", fontsize=8.5)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    fig.tight_layout(rect=[0, 0.16, 1, 0.98])
    _caption(
        fig,
        "T = 0.65 is LOCKED from the separate 40-question FinQA DEV calibration set; it was not tuned on the frozen 140.\n"
        "Always-answer baselines have coverage = 100%, so selective accuracy equals overall displayed correctness.\n"
        "UQ abstains on 62/140 questions, raising accuracy among answered cases while reducing coverage. "
        "Error bars: Wilson 95% CI. n = 140.\n"
        "Source: results/metrics/phase17_descriptive.csv.",
    )
    return _save(fig, fig_dir, "rq3_coverage_selective")


def _fig_mcnemar(data: dict, fig_dir: Path) -> list[str]:
    row = data["tests"]["rq1_mcnemar_displayed_sa_vs_ma"]
    counts = [
        int(float(row["n11_both_positive"])),
        int(float(row["n10_left_only"])),
        int(float(row["n01_right_only"])),
        int(float(row["n00_both_negative"])),
    ]
    if counts != [19, 13, 10, 98]:
        raise ValueError(f"Unexpected McNemar counts {counts}; refusing to draw appendix RQ1")
    labels = [
        "Both correct",
        "Single-Agent\nonly",
        "Multi-Agent\nonly",
        "Both incorrect",
    ]
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    bars = ax.bar(labels, counts, color=[COLOR_UQ, COLOR_SA, COLOR_MA, "#8C8C8C"], edgecolor="white")
    for bar, val in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.6,
            str(val), ha="center", va="bottom", fontsize=10,
        )
    ax.set_ylabel("Number of questions")
    ax.set_ylim(0, max(counts) + 18)
    ax.set_title("Appendix: RQ1 McNemar Counts — Single-Agent vs Multi-Agent")
    fig.tight_layout(rect=[0, 0.14, 1, 0.98])
    _caption(
        fig,
        "Paired n = 140 frozen FinQA test questions. Discordant pairs = 23 "
        "(13 Single-Agent only, 10 Multi-Agent only).\n"
        "Exact McNemar p = 0.6776 (Holm p = 0.6776; not significant). "
        "Source: results/metrics/phase17_tests.csv.",
    )
    return _save(fig, fig_dir, "rq1_mcnemar_counts")


def _fig_box(data: dict, fig_dir: Path) -> list[str]:
    labels = [ARCH_LABELS[a] for a in ARCHITECTURES]
    values = [data["llm_by_arch"][a] for a in ARCHITECTURES]
    for arch, vals in zip(ARCHITECTURES, values):
        if len(vals) != N_QUESTIONS:
            raise ValueError(f"{arch} faithfulness n={len(vals)}, expected {N_QUESTIONS}")
    fig, ax = plt.subplots(figsize=(7.6, 5.5))
    box_common = dict(
        showfliers=True,
        patch_artist=True,
        medianprops={"color": "black", "linewidth": 1.2},
        whiskerprops={"color": "#333333"},
        capprops={"color": "#333333"},
        flierprops={
            "marker": "o", "markersize": 3.5, "alpha": 0.55,
            "markerfacecolor": "#666666", "markeredgecolor": "none",
        },
    )
    try:
        box = ax.boxplot(values, tick_labels=labels, **box_common)
    except TypeError:
        box = ax.boxplot(values, labels=labels, **box_common)
    for patch, color in zip(box["boxes"], [COLOR_SA, COLOR_MA, COLOR_UQ]):
        patch.set_facecolor(color)
        patch.set_alpha(0.55)
        patch.set_edgecolor("#333333")
    ax.set_ylim(0, 1)
    ax.set_ylabel(YLABEL_FAITHFULNESS)
    ax.set_title("Appendix: RQ2 Faithfulness Distribution by Architecture")
    fig.tight_layout(rect=[0, 0.14, 1, 0.98])
    _caption(
        fig,
        f"n = {N_QUESTIONS} questions per architecture. "
        f"{JUDGE_METRIC_LABEL} — not official RAGAS.\n"
        "Source: official Phase 16 judge JSONL joined to Phase 16 processed cases. "
        "UQ includes abstained drafts.",
    )
    return _save(fig, fig_dir, "rq2_llm_faithfulness_box")


def _fig_outcomes(data: dict, fig_dir: Path) -> list[str]:
    out = data["summary"]["rq3_abstention_outcomes"]
    counts = [
        int(out["true_positive_answer_displayed_correct"]),
        int(out["false_positive_answer_displayed_incorrect"]),
        int(out["true_abstain_incorrect_draft"]),
        int(out["false_abstain_correct_draft"]),
    ]
    if counts != [32, 46, 60, 2]:
        raise ValueError(f"Unexpected UQ outcome counts {counts}; refusing to draw appendix RQ3")
    labels = [
        "ANSWER,\ncorrect",
        "ANSWER,\nincorrect",
        "ABSTAIN,\nincorrect draft",
        "ABSTAIN,\ncorrect draft",
    ]
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    bars = ax.bar(labels, counts, color=[COLOR_UQ, COLOR_ABSTAIN, COLOR_SA, COLOR_MA], edgecolor="white")
    for bar, val in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.3,
            str(val), ha="center", va="bottom", fontsize=10,
        )
    ax.set_ylabel("Number of questions")
    ax.set_ylim(0, max(counts) + 12)
    ax.set_title("Appendix: RQ3 UQ Outcomes at Locked T=0.65")
    fig.tight_layout(rect=[0, 0.14, 1, 0.98])
    _caption(
        fig,
        "n = 140. Coverage = 78 ANSWER + 62 ABSTAIN. Two ABSTAIN cases had a numerically correct draft.\n"
        "T = 0.65 locked on the separate 40-question DEV calibration set. "
        "Source: results/config/phase17_statistics_summary.json.",
    )
    return _save(fig, fig_dir, "rq3_uq_outcomes")


def render_from_saved(root: Path | None = None) -> dict[str, list[str]]:
    """Redraw Phase 17 figures from saved tables/JSONL. Does not write statistical CSVs."""
    _style()
    root = root or project_root()
    fig_dir = root / "results" / "metrics" / "phase17_figures"
    data = _load_saved(root)
    return {
        "rq1_accuracy_wilson_ci": _fig1(data, fig_dir),
        "rq2_confidence_vs_faithfulness": _fig2(data, fig_dir),
        "rq3_coverage_selective": _fig3(data, fig_dir),
        "rq1_mcnemar_counts": _fig_mcnemar(data, fig_dir),
        "rq2_llm_faithfulness_box": _fig_box(data, fig_dir),
        "rq3_uq_outcomes": _fig_outcomes(data, fig_dir),
    }
