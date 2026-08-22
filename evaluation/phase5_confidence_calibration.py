#!/usr/bin/env python3
"""Phase 5 confidence calibration analysis for RQ3.

This script analyses the frozen evaluation dataset to show how system confidence
relates to correctness, how confidence is distributed, and how well confidence
tracks observed correctness under a simple calibration view.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress, pearsonr, spearmanr


WORKSPACE = Path(__file__).resolve().parent.parent
RESULTS_DIR = WORKSPACE / "results"
SOURCE_FILE = RESULTS_DIR / "evaluation_results_final.csv"
SUMMARY_FILE = RESULTS_DIR / "phase5_confidence_summary.csv"
METRICS_FILE = RESULTS_DIR / "phase5_calibration_metrics.csv"
BIN_FILE = RESULTS_DIR / "phase5_calibration_bins.csv"
REPORT_FILE = RESULTS_DIR / "phase5_calibration_report.csv"
PLOT_DIR = RESULTS_DIR / "phase5_calibration_plots"

SYSTEMS = ["Multi-Agent RAG + UQ"]
PRIMARY_TARGET = ("ragas_answer_correctness", "RAGAS Answer Correctness")
CONFIDENCE_BINS = np.linspace(0.0, 1.0, 6)


def setup_logging() -> logging.Logger:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("Phase5ConfidenceCalibration")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(RESULTS_DIR / "phase5_confidence_calibration.log", mode="a", encoding="utf-8")
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

    logger.info(f"Loading frozen evaluation data from {SOURCE_FILE}")
    df = pd.read_csv(SOURCE_FILE)

    required_columns = ["System", "confidence", PRIMARY_TARGET[0]]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in source file: {missing}")

    for column in ["confidence", PRIMARY_TARGET[0]]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if df[column].isna().any():
            raise ValueError(f"Column {column} contains invalid or missing values")

    return df


def validate_source(df: pd.DataFrame) -> None:
    if len(df) != 420:
        raise ValueError(f"Expected 420 rows, found {len(df)}")

    counts = df["System"].value_counts(dropna=False).to_dict()
    if sorted(counts.values()) != [140, 140, 140]:
        raise ValueError(f"Expected 140 rows per system, found {counts}")

    for column in ["confidence", PRIMARY_TARGET[0]]:
        series = pd.to_numeric(df[column], errors="coerce")
        if ((series < 0) | (series > 1)).any():
            raise ValueError(f"Column {column} has values outside 0..1")


def safe_correlation(x: pd.Series, y: pd.Series, method: str) -> tuple[float, float, str]:
    paired = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": pd.to_numeric(y, errors="coerce")}).dropna()
    if len(paired) < 2:
        return float("nan"), float("nan"), "Not enough paired observations"
    if paired["x"].nunique() <= 1 or paired["y"].nunique() <= 1:
        return float("nan"), float("nan"), "Constant input; correlation undefined"

    if method == "spearman":
        stat, p_value = spearmanr(paired["x"], paired["y"])
    elif method == "pearson":
        stat, p_value = pearsonr(paired["x"], paired["y"])
    else:
        raise ValueError(f"Unsupported correlation method: {method}")

    return float(stat), float(p_value), f"Computed on {len(paired)} rows"


def safe_linregress(x: pd.Series, y: pd.Series) -> tuple[float, float, float, float, float, str]:
    paired = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": pd.to_numeric(y, errors="coerce")}).dropna()
    if len(paired) < 2:
        return float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Not enough paired observations"
    if paired["x"].nunique() <= 1 or paired["y"].nunique() <= 1:
        return float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), "Constant input; regression undefined"

    result = linregress(paired["x"], paired["y"])
    return (
        float(result.slope),
        float(result.intercept),
        float(result.rvalue),
        float(result.pvalue),
        float(result.stderr),
        f"Computed on {len(paired)} rows",
    )


def calibration_bins(frame: pd.DataFrame, target_column: str, target_label: str) -> tuple[pd.DataFrame, dict[str, float]]:
    work = frame[["System", "confidence", target_column]].copy()
    work["confidence_bin"] = pd.cut(work["confidence"], bins=CONFIDENCE_BINS, include_lowest=True, right=True)

    rows: list[dict[str, object]] = []
    metrics: dict[str, float] = {}

    for system in SYSTEMS:
        system_frame = work[work["System"] == system].copy()
        bin_rows = []
        for interval, group in system_frame.groupby("confidence_bin", observed=False):
            if group.empty or pd.isna(interval):
                continue
            mean_confidence = float(group["confidence"].mean())
            mean_target = float(group[target_column].mean())
            gap = mean_confidence - mean_target
            abs_gap = abs(gap)
            bin_rows.append({
                "target_metric": target_label,
                "system": system,
                "bin": str(interval),
                "bin_left": float(interval.left),
                "bin_right": float(interval.right),
                "count": int(len(group)),
                "mean_confidence": mean_confidence,
                "mean_target": mean_target,
                "gap": gap,
                "abs_gap": abs_gap,
            })

        if bin_rows:
            bin_frame = pd.DataFrame(bin_rows)
            total = int(bin_frame["count"].sum())
            ece = float((bin_frame["count"] / total * bin_frame["abs_gap"]).sum())
            mce = float(bin_frame["abs_gap"].max())
        else:
            bin_frame = pd.DataFrame(columns=["target_metric", "system", "bin", "bin_left", "bin_right", "count", "mean_confidence", "mean_target", "gap", "abs_gap"])
            ece = float("nan")
            mce = float("nan")

        rows.extend(bin_frame.to_dict("records"))
        metrics[f"{system}::{target_label}::ece_5"] = ece
        metrics[f"{system}::{target_label}::mce_5"] = mce

    return pd.DataFrame(rows), metrics


def build_metrics(df: pd.DataFrame, target_column: str, target_label: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    bin_tables = []

    for system in SYSTEMS:
        frame = df[df["System"] == system]
        confidence = pd.to_numeric(frame["confidence"], errors="coerce")
        target = pd.to_numeric(frame[target_column], errors="coerce")

        spearman_r, spearman_p, spearman_note = safe_correlation(confidence, target, "spearman")
        pearson_r, pearson_p, pearson_note = safe_correlation(confidence, target, "pearson")
        slope, intercept, r_value, reg_p, std_err, reg_note = safe_linregress(confidence, target)
        abs_gap = float((confidence - target).abs().mean())

        rows.append({
            "target_metric": target_label,
            "system": system,
            "count": int(len(frame)),
            "confidence_mean": float(confidence.mean()),
            "confidence_std": float(confidence.std()),
            "confidence_median": float(confidence.median()),
            "confidence_min": float(confidence.min()),
            "confidence_max": float(confidence.max()),
            "target_mean": float(target.mean()),
            "target_std": float(target.std()),
            "target_median": float(target.median()),
            "target_min": float(target.min()),
            "target_max": float(target.max()),
            "mean_absolute_gap": abs_gap,
            "linear_slope": slope,
            "linear_intercept": intercept,
            "linear_r": r_value,
            "linear_p_value": reg_p,
            "linear_stderr": std_err,
            "linear_note": reg_note,
            "spearman_r": spearman_r,
            "spearman_p_value": spearman_p,
            "spearman_note": spearman_note,
            "pearson_r": pearson_r,
            "pearson_p_value": pearson_p,
            "pearson_note": pearson_note,
        })

        bin_table, _ = calibration_bins(frame, target_column, target_label)
        bin_tables.append(bin_table)

    metrics = pd.DataFrame(rows).round(4)
    bins = pd.concat(bin_tables, ignore_index=True) if bin_tables else pd.DataFrame()
    if not bins.empty:
        bins = bins.round(4)
    return metrics, bins


def plot_confidence_distribution(df: pd.DataFrame) -> None:
    fig, axis = plt.subplots(figsize=(7, 4))
    bins = np.linspace(0.0, 1.0, 21)
    system = SYSTEMS[0]
    series = pd.to_numeric(df.loc[df["System"] == system, "confidence"], errors="coerce")
    axis.hist(series, bins=bins, color="#4C72B0", alpha=0.85, edgecolor="white")
    axis.axvline(series.mean(), color="black", linestyle="--", linewidth=1, label=f"Mean {series.mean():.3f}")
    axis.set_title(f"Confidence Distribution: {system}")
    axis.set_xlim(0, 1)
    axis.set_xlabel("Confidence")
    axis.set_ylabel("Count")
    axis.grid(True, axis="y", alpha=0.2)
    axis.legend(fontsize=8)
    fig.suptitle("Confidence Distribution: Multi-Agent RAG + UQ")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(PLOT_DIR / "phase5_confidence_distribution.png", dpi=200)
    plt.close(fig)


def plot_confidence_vs_target(df: pd.DataFrame, target_column: str, target_label: str, filename: str) -> None:
    fig, axis = plt.subplots(figsize=(7.5, 5.5))
    system = SYSTEMS[0]
    frame = df[df["System"] == system].copy()
    confidence = pd.to_numeric(frame["confidence"], errors="coerce")
    target = pd.to_numeric(frame[target_column], errors="coerce")
    axis.scatter(confidence, target, alpha=0.45, s=22, color="#4C72B0", edgecolors="none", label="Questions")

    bin_table, _ = calibration_bins(frame, target_column, target_label)
    if not bin_table.empty:
        axis.plot(bin_table["mean_confidence"], bin_table["mean_target"], marker="o", linewidth=2.5, color="black", label="Binned mean")

    slope, intercept, r_value, p_value, std_err, _ = safe_linregress(confidence, target)
    if not pd.isna(slope):
        x_line = np.linspace(float(confidence.min()), float(confidence.max()), 100)
        axis.plot(x_line, slope * x_line + intercept, color="#C44E52", linewidth=2, label="Trend line")
        axis.text(
            0.02,
            0.98,
            f"Pearson r = {safe_correlation(confidence, target, 'pearson')[0]:.3f}\nSpearman ρ = {safe_correlation(confidence, target, 'spearman')[0]:.3f}\np = {p_value:.3g}",
            transform=axis.transAxes,
            va="top",
            ha="left",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cccccc"),
        )

    axis.set_title(f"Confidence vs {target_label} ({system})")
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.set_xlabel("Confidence")
    axis.set_ylabel(target_label)
    axis.grid(True, alpha=0.2)
    axis.legend(fontsize=8)
    fig.suptitle("Calibration Scatter for Multi-Agent RAG + UQ")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(PLOT_DIR / filename, dpi=200)
    plt.close(fig)


def plot_reliability_curve(bins_df: pd.DataFrame, target_label: str, filename: str) -> None:
    fig, axis = plt.subplots(figsize=(7, 5))
    subset = bins_df[bins_df["system"] == SYSTEMS[0]].copy()
    subset["bin_center"] = (subset["bin_left"] + subset["bin_right"]) / 2
    ece = float((subset["count"] / subset["count"].sum() * subset["abs_gap"]).sum()) if not subset.empty else float("nan")
    axis.plot(subset["mean_confidence"], subset["mean_target"], marker="o", linewidth=2.5, color="#4C72B0")
    for _, row in subset.iterrows():
        axis.annotate(f"{int(row['count'])}", (row["mean_confidence"], row["mean_target"]), textcoords="offset points", xytext=(4, 4), fontsize=7)

    axis.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1, alpha=0.6)
    axis.set_title(f"Reliability Curve: {SYSTEMS[0]}")
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.set_xlabel("Mean Confidence in Bin")
    axis.set_ylabel(target_label)
    axis.grid(True, alpha=0.2)
    axis.text(0.02, 0.98, f"ECE = {ece:.3f}", transform=axis.transAxes, va="top", ha="left", fontsize=9,
              bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cccccc"))
    fig.suptitle("Reliability Curve for Multi-Agent RAG + UQ")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(PLOT_DIR / filename, dpi=200)
    plt.close(fig)


def run_target_analysis(df: pd.DataFrame, target_column: str, target_label: str, slug: str, logger: logging.Logger) -> tuple[pd.DataFrame, pd.DataFrame]:
    logger.info(f"Analysing confidence against {target_label}")
    metrics_df, bins_df = build_metrics(df, target_column, target_label)
    metrics_df.insert(0, "target_slug", slug)
    if not bins_df.empty:
        bins_df.insert(0, "target_slug", slug)
    return metrics_df, bins_df


def build_report(metrics_df: pd.DataFrame, bins_df: pd.DataFrame) -> pd.DataFrame:
    row = metrics_df.iloc[0].to_dict()
    bin_subset = bins_df[bins_df["system"] == SYSTEMS[0]].copy()
    ece = float((bin_subset["count"] / bin_subset["count"].sum() * bin_subset["abs_gap"]).sum()) if not bin_subset.empty else float("nan")

    if pd.isna(row["pearson_r"]):
        interpretation = "No calibration signal available because confidence is constant or insufficient."
    elif abs(row["pearson_r"]) < 0.2:
        interpretation = "Very weak alignment between confidence and answer correctness."
    elif abs(row["pearson_r"]) < 0.4:
        interpretation = "Weak alignment between confidence and answer correctness."
    elif abs(row["pearson_r"]) < 0.6:
        interpretation = "Moderate alignment between confidence and answer correctness."
    else:
        interpretation = "Strong alignment between confidence and answer correctness."

    return pd.DataFrame([{
        "system": SYSTEMS[0],
        "target_metric": PRIMARY_TARGET[1],
        "count": int(row["count"]),
        "mean_confidence": row["confidence_mean"],
        "std_confidence": row["confidence_std"],
        "mean_target": row["target_mean"],
        "std_target": row["target_std"],
        "pearson_r": row["pearson_r"],
        "pearson_p_value": row["pearson_p_value"],
        "spearman_r": row["spearman_r"],
        "spearman_p_value": row["spearman_p_value"],
        "mean_absolute_gap": row["mean_absolute_gap"],
        "ece_5": round(ece, 4),
        "calibration_interpretation": interpretation,
    }])


def create_plots(df: pd.DataFrame, primary_bins: pd.DataFrame, primary_label: str) -> None:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    plot_confidence_distribution(df)
    plot_confidence_vs_target(df, PRIMARY_TARGET[0], primary_label, "phase5_confidence_vs_ragas_answer_correctness.png")
    plot_reliability_curve(primary_bins, primary_label, "phase5_reliability_curve.png")


def main() -> None:
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("PHASE 5: CONFIDENCE CALIBRATION")
    logger.info("=" * 80)

    df = load_source(logger)
    validate_source(df)

    metrics_df, bins_df = run_target_analysis(df, PRIMARY_TARGET[0], PRIMARY_TARGET[1], PRIMARY_TARGET[0], logger)
    report_df = build_report(metrics_df, bins_df)

    atomic_write_csv(report_df, REPORT_FILE)
    atomic_write_csv(metrics_df, METRICS_FILE)
    atomic_write_csv(bins_df, BIN_FILE)
    atomic_write_csv(report_df, SUMMARY_FILE)

    create_plots(df, bins_df, PRIMARY_TARGET[1])

    logger.info(f"Saved summary report to {SUMMARY_FILE}")
    logger.info(f"Saved calibration report to {REPORT_FILE}")
    logger.info(f"Saved calibration metrics to {METRICS_FILE}")
    logger.info(f"Saved calibration bins to {BIN_FILE}")
    logger.info(f"Saved plots to {PLOT_DIR}")
    logger.info("Phase 5 confidence calibration complete")


if __name__ == "__main__":
    main()