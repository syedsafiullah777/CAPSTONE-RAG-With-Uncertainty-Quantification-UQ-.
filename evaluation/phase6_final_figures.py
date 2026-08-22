#!/usr/bin/env python3
"""Phase 6: publication-quality figures for the dissertation.

This script reuses the frozen evaluation data and the saved Phase 3/5 analysis
tables to produce the final figures for the dissertation:
- performance means with 95% confidence intervals
- response time comparison
- threshold analysis with coverage and answer/warning/abstain percentages
- confidence distribution, calibration scatter, and reliability curve
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter, FormatStrFormatter
from scipy.stats import sem, t


WORKSPACE = Path(__file__).resolve().parent.parent
RESULTS_DIR = WORKSPACE / "results"
SOURCE_FILE = RESULTS_DIR / "evaluation_results_final.csv"
THRESHOLD_FILE = RESULTS_DIR / "phase3_threshold_analysis.csv"
CALIBRATION_REPORT_FILE = RESULTS_DIR / "phase5_calibration_report.csv"
CALIBRATION_BINS_FILE = RESULTS_DIR / "phase5_calibration_bins.csv"
OUTPUT_DIR = RESULTS_DIR / "phase6_final_figures"

SYSTEM_ORDER = ["Single-Agent RAG", "Multi-Agent RAG", "Multi-Agent RAG + UQ"]
SYSTEM_LABELS = {
    "Single-Agent RAG": "Single-Agent",
    "Multi-Agent RAG": "Multi-Agent",
    "Multi-Agent RAG + UQ": "Multi-Agent + UQ",
}
PERFORMANCE_METRICS = [
    ("ragas_faithfulness", "Mean Faithfulness"),
    ("ragas_answer_correctness", "Mean Answer Correctness"),
    ("ragas_context_precision", "Mean Context Precision"),
    ("ragas_context_recall", "Mean Context Recall"),
]
PLOT_STYLE = {
    "Single-Agent RAG": "#4C72B0",
    "Multi-Agent RAG": "#55A868",
    "Multi-Agent RAG + UQ": "#C44E52",
}


def setup_logging() -> logging.Logger:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("Phase6FinalFigures")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(RESULTS_DIR / "phase6_final_figures.log", mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger


def atomic_write_csv(df: pd.DataFrame, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.with_suffix(target.suffix + ".tmp")
    df.to_csv(temp_path, index=False)
    temp_path.replace(target)


def load_source(logger: logging.Logger) -> pd.DataFrame:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_FILE}")

    df = pd.read_csv(SOURCE_FILE)
    required_columns = ["System", "confidence", "response_time", "ragas_faithfulness", "ragas_answer_correctness", "ragas_context_precision", "ragas_context_recall"]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in source file: {missing}")

    for column in ["confidence", "response_time", "ragas_faithfulness", "ragas_answer_correctness", "ragas_context_precision", "ragas_context_recall"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if df[column].isna().any():
            raise ValueError(f"Column {column} contains invalid values")

    logger.info(f"Loaded {len(df)} rows from frozen evaluation data")
    return df


def load_thresholds(logger: logging.Logger) -> pd.DataFrame:
    if not THRESHOLD_FILE.exists():
        raise FileNotFoundError(f"Threshold file not found: {THRESHOLD_FILE}")

    df = pd.read_csv(THRESHOLD_FILE)
    required_columns = [
        "answer_threshold",
        "warning_threshold",
        "answer_count",
        "warning_count",
        "abstain_count",
        "answered_accuracy",
        "baseline_accuracy",
        "accuracy_gain",
        "coverage_all_responses",
        "coverage_direct_answers",
        "answer_share",
        "warning_share",
        "abstain_share",
    ]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required threshold columns: {missing}")

    for column in required_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    logger.info(f"Loaded {len(df)} threshold rows")
    return df


def load_calibration(logger: logging.Logger) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not CALIBRATION_REPORT_FILE.exists() or not CALIBRATION_BINS_FILE.exists():
        raise FileNotFoundError("Calibration report or bins file not found; run Phase 5 first.")

    report = pd.read_csv(CALIBRATION_REPORT_FILE)
    bins = pd.read_csv(CALIBRATION_BINS_FILE)
    logger.info(f"Loaded calibration report with {len(report)} row(s)")
    logger.info(f"Loaded calibration bins with {len(bins)} row(s)")
    return report, bins


def mean_ci(series: pd.Series, confidence: float = 0.95) -> tuple[float, float, float]:
    values = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if len(values) == 0:
        return float("nan"), float("nan"), float("nan")
    mean_value = float(values.mean())
    if len(values) == 1:
        return mean_value, mean_value, mean_value
    standard_error = float(sem(values))
    if standard_error == 0 or np.isnan(standard_error):
        return mean_value, mean_value, mean_value
    critical = float(t.ppf((1 + confidence) / 2.0, len(values) - 1))
    margin = critical * standard_error
    return mean_value, mean_value - margin, mean_value + margin


def plot_performance_metrics(df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharey=False)
    axes = axes.flatten()

    for axis, (column, title) in zip(axes, PERFORMANCE_METRICS):
        means = []
        lows = []
        highs = []
        for system in SYSTEM_ORDER:
            system_values = df.loc[df["System"] == system, column]
            mean_value, low, high = mean_ci(system_values)
            means.append(mean_value)
            lows.append(mean_value - low)
            highs.append(high - mean_value)

        x_positions = np.arange(len(SYSTEM_ORDER))
        colors = [PLOT_STYLE[system] for system in SYSTEM_ORDER]
        axis.bar(x_positions, means, yerr=[lows, highs], capsize=5, color=colors, alpha=0.92, edgecolor="black", linewidth=0.4)
        axis.set_xticks(x_positions)
        axis.set_xticklabels([SYSTEM_LABELS[system] for system in SYSTEM_ORDER], rotation=12)
        axis.set_ylim(0, 1)
        axis.set_title(title)
        axis.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        axis.grid(True, axis="y", alpha=0.25)

    fig.suptitle("Phase 6 Performance Comparison with 95% Confidence Intervals", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    output = OUTPUT_DIR / "phase6_performance_metrics_ci.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


def plot_response_time(df: pd.DataFrame) -> Path:
    fig, axis = plt.subplots(figsize=(8, 5))
    summaries = []
    for system in SYSTEM_ORDER:
        values = pd.to_numeric(df.loc[df["System"] == system, "response_time"], errors="coerce")
        mean_value, low, high = mean_ci(values)
        summaries.append((system, mean_value, low, high))

    x_positions = np.arange(len(summaries))
    means = [item[1] for item in summaries]
    lower = [item[1] - item[2] for item in summaries]
    upper = [item[3] - item[1] for item in summaries]
    colors = [PLOT_STYLE[item[0]] for item in summaries]
    axis.bar(x_positions, means, yerr=[lower, upper], capsize=6, color=colors, alpha=0.92, edgecolor="black", linewidth=0.4)
    axis.set_xticks(x_positions)
    axis.set_xticklabels([SYSTEM_LABELS[item[0]] for item in summaries], rotation=12)
    axis.set_ylabel("Response Time (s)")
    axis.set_title("Phase 6 Response Time Comparison")
    axis.grid(True, axis="y", alpha=0.25)
    axis.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    fig.tight_layout()
    output = OUTPUT_DIR / "phase6_response_time_ci.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


def plot_threshold_composition(threshold_df: pd.DataFrame) -> Path:
    selected_answer_threshold = 0.49
    selected_warning_threshold = 0.46
    subset = threshold_df[
        (threshold_df["answer_threshold"] == selected_answer_threshold)
        & (threshold_df["warning_threshold"] == selected_warning_threshold)
    ]
    if subset.empty:
        raise ValueError("No threshold row found for the selected operating point.")

    row = subset.iloc[0]
    labels = ["Answer", "Warning", "Abstain"]
    values = [row["answer_share"], row["warning_share"], row["abstain_share"]]
    colors = ["#4C72B0", "#55A868", "#C44E52"]

    fig, axis = plt.subplots(figsize=(7.5, 5.5))
    bottom = 0.0
    for label, value, color in zip(labels, values, colors):
        axis.bar([0], [value], bottom=[bottom], width=0.6, label=f"{label} ({value*100:.1f}%)", color=color, edgecolor="black", linewidth=0.4, alpha=0.92)
        bottom += float(value)

    axis.text(0, 1.03, f"Answered accuracy = {row['answered_accuracy']*100:.1f}%\nCoverage (all responses) = {row['coverage_all_responses']*100:.1f}%", ha="center", va="bottom", fontsize=9)
    axis.set_xticks([0])
    axis.set_xticklabels([f"Threshold = {selected_answer_threshold:.2f}\nWarning = {selected_warning_threshold:.2f}"])
    axis.set_ylim(0, 1.18)
    axis.set_ylabel("Share of Responses")
    axis.set_title("Selected Threshold Composition")
    axis.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    axis.grid(True, axis="y", alpha=0.25)
    axis.legend(fontsize=8, loc="upper right")

    fig.tight_layout()
    output = OUTPUT_DIR / "phase6_threshold_composition.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


def plot_threshold_coverage_accuracy(threshold_df: pd.DataFrame) -> Path:
    representative_warning = 0.48
    subset = threshold_df[threshold_df["warning_threshold"] == representative_warning].sort_values("answer_threshold")
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.plot(subset["answer_threshold"], subset["answered_accuracy"], marker="o", linewidth=2.5, label="Answered accuracy")
    axis.plot(subset["answer_threshold"], subset["coverage_direct_answers"], marker="o", linewidth=2.5, label="Direct answer coverage")
    axis.plot(subset["answer_threshold"], subset["coverage_all_responses"], marker="o", linewidth=2.5, label="All response coverage")
    axis.axhline(subset["baseline_accuracy"].iloc[0], color="gray", linestyle="--", linewidth=1.5, label="Baseline accuracy")
    axis.set_title("Threshold Analysis: Coverage vs Accuracy")
    axis.set_xlabel("Confidence Threshold")
    axis.set_ylabel("Value")
    axis.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    axis.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    axis.grid(True, alpha=0.25)
    axis.legend(fontsize=8)
    fig.tight_layout()
    output = OUTPUT_DIR / "phase6_threshold_coverage_accuracy.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


def plot_confidence_distribution(df: pd.DataFrame) -> Path:
    fig, axis = plt.subplots(figsize=(8, 5))
    values = pd.to_numeric(df.loc[df["System"] == "Multi-Agent RAG + UQ", "confidence"], errors="coerce")
    bins = np.linspace(0.0, 1.0, 18)
    axis.hist(values, bins=bins, color="#4C72B0", alpha=0.88, edgecolor="white")
    axis.axvline(values.mean(), color="black", linestyle="--", linewidth=1.8, label=f"Mean = {values.mean():.3f}")
    axis.axvline(values.mean() - values.std(), color="#C44E52", linestyle=":", linewidth=1.5, label=f"SD = {values.std():.3f}")
    axis.axvline(values.mean() + values.std(), color="#C44E52", linestyle=":", linewidth=1.5)
    axis.set_title("Confidence Distribution: Multi-Agent RAG + UQ")
    axis.set_xlabel("Confidence")
    axis.set_ylabel("Count")
    axis.set_xlim(0, 1)
    axis.grid(True, axis="y", alpha=0.25)
    axis.legend(fontsize=8)
    fig.tight_layout()
    output = OUTPUT_DIR / "phase6_confidence_distribution.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


def plot_confidence_scatter(calibration_report: pd.DataFrame, df: pd.DataFrame) -> Path:
    fig, axis = plt.subplots(figsize=(8, 5.5))
    subset = df[df["System"] == "Multi-Agent RAG + UQ"].copy()
    confidence = pd.to_numeric(subset["confidence"], errors="coerce")
    target = pd.to_numeric(subset["ragas_answer_correctness"], errors="coerce")
    axis.scatter(confidence, target, s=26, alpha=0.5, color="#4C72B0", edgecolors="none", label="Questions")

    if len(subset) >= 2:
        x = np.linspace(confidence.min(), confidence.max(), 100)
        coeffs = np.polyfit(confidence, target, deg=1)
        axis.plot(x, np.poly1d(coeffs)(x), color="#C44E52", linewidth=2.2, label="Trend line")

    row = calibration_report.iloc[0]
    annotation = (
        f"Pearson r = {row['pearson_r']:.3f}\n"
        f"Spearman ρ = {row['spearman_r']:.3f}\n"
        f"p = {row['pearson_p_value']:.3g}"
    )
    axis.text(
        0.03,
        0.98,
        annotation,
        transform=axis.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cccccc"),
    )
    axis.set_title("Calibration Scatter: Confidence vs RAGAS Answer Correctness")
    axis.set_xlabel("Confidence")
    axis.set_ylabel("RAGAS Answer Correctness")
    axis.set_xlim(0.45, 0.57)
    axis.set_ylim(0, 1)
    axis.grid(True, alpha=0.25)
    axis.legend(fontsize=8)
    fig.tight_layout()
    output = OUTPUT_DIR / "phase6_confidence_scatter.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


def plot_reliability_curve(calibration_bins: pd.DataFrame, calibration_report: pd.DataFrame) -> Path:
    fig, axis = plt.subplots(figsize=(8, 5.5))
    subset = calibration_bins[calibration_bins["system"] == "Multi-Agent RAG + UQ"].copy()
    subset["bin_center"] = (subset["bin_left"] + subset["bin_right"]) / 2
    axis.plot(subset["mean_confidence"], subset["mean_target"], marker="o", linewidth=2.5, color="#4C72B0", label="Binned mean")
    axis.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1.5, label="Perfect calibration")

    for _, row in subset.iterrows():
        axis.annotate(f"{int(row['count'])}", (row["mean_confidence"], row["mean_target"]), textcoords="offset points", xytext=(4, 4), fontsize=8)

    ece = float(calibration_report.iloc[0]["ece_5"])
    axis.text(
        0.03,
        0.98,
        f"ECE (5 bins) = {ece:.3f}",
        transform=axis.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cccccc"),
    )
    axis.set_title("Reliability Curve: Multi-Agent RAG + UQ")
    axis.set_xlabel("Mean Confidence in Bin")
    axis.set_ylabel("Mean RAGAS Answer Correctness in Bin")
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.grid(True, alpha=0.25)
    axis.legend(fontsize=8)
    fig.tight_layout()
    output = OUTPUT_DIR / "phase6_reliability_curve.png"
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output


def main() -> None:
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("PHASE 6: FINAL FIGURES")
    logger.info("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    source_df = load_source(logger)
    threshold_df = load_thresholds(logger)
    calibration_report, calibration_bins = load_calibration(logger)

    outputs = [
        plot_performance_metrics(source_df),
        plot_response_time(source_df),
        plot_threshold_coverage_accuracy(threshold_df),
        plot_threshold_composition(threshold_df),
        plot_confidence_distribution(source_df),
        plot_confidence_scatter(calibration_report, source_df),
        plot_reliability_curve(calibration_bins, calibration_report),
    ]

    report = pd.DataFrame({
        "figure": [path.name for path in outputs],
        "path": [str(path) for path in outputs],
    })
    atomic_write_csv(report, OUTPUT_DIR / "phase6_final_figures_index.csv")

    logger.info(f"Saved {len(outputs)} figure(s) to {OUTPUT_DIR}")
    logger.info("Phase 6 final figures complete")


if __name__ == "__main__":
    main()