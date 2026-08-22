#!/usr/bin/env python3
"""Phase 4 statistical analysis for paired comparison of RAG systems."""

from __future__ import annotations

import json
import logging
import math
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
from scipy import stats


WORKSPACE = Path(__file__).resolve().parent.parent
RESULTS_DIR = WORKSPACE / "results"
CHECKPOINT_DIR = RESULTS_DIR / ".checkpoints"
SOURCE_FILE = RESULTS_DIR / "evaluation_results_final.csv"
LEGACY_SOURCE_FILE = RESULTS_DIR / "phase3_master_dataset.csv"
OUTPUT_FILE = RESULTS_DIR / "phase4_pairwise_statistics.csv"
SUMMARY_FILE = RESULTS_DIR / "phase4_metric_summary.csv"
ASSUMPTION_FILE = RESULTS_DIR / "phase4_assumption_checks.csv"
PLOT_DIR = RESULTS_DIR / "phase4_statistics_plots"
CHECKPOINT_FILE = CHECKPOINT_DIR / "phase4_statistical_analysis_checkpoint.json"

SYSTEMS = ["Single-Agent RAG", "Multi-Agent RAG", "Multi-Agent RAG + UQ"]
PAIRINGS = [
    ("Single-Agent RAG", "Multi-Agent RAG"),
    ("Single-Agent RAG", "Multi-Agent RAG + UQ"),
    ("Multi-Agent RAG", "Multi-Agent RAG + UQ"),
]
METRICS = [
    ("ragas_faithfulness", "Faithfulness"),
    ("ragas_answer_correctness", "Answer Correctness"),
    ("ragas_context_precision", "Context Precision"),
    ("ragas_context_recall", "Context Recall"),
]


def setup_logging() -> logging.Logger:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("Phase4StatisticalAnalysis")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(RESULTS_DIR / "phase4.log", mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger


def load_source(logger: logging.Logger) -> pd.DataFrame:
    source_path = SOURCE_FILE if SOURCE_FILE.exists() else LEGACY_SOURCE_FILE
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_FILE} or {LEGACY_SOURCE_FILE}")

    logger.info(f"Loading statistical source data from {source_path}")
    df = pd.read_csv(source_path)
    required = ["Question ID", "System", *[metric for metric, _ in METRICS]]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for metric, _ in METRICS:
        df[metric] = pd.to_numeric(df[metric], errors="coerce")

    return df


def validate_source(df: pd.DataFrame) -> None:
    if len(df) != 420:
        raise ValueError(f"Expected 420 rows, found {len(df)}")

    counts = df["System"].value_counts(dropna=False).to_dict()
    if sorted(counts.values()) != [140, 140, 140]:
        raise ValueError(f"Expected 140 rows per system, found {counts}")

    if df["Question ID"].duplicated().any():
        raise ValueError("Duplicate Question ID values present in the source data")

    missing_metrics = []
    for metric, _ in METRICS:
        series = df[metric]
        if series.isna().any():
            missing_metrics.append(metric)
        if ((series < 0).any() or (series > 1).any()):
            raise ValueError(f"Metric {metric} has values outside 0..1")
    if missing_metrics:
        raise ValueError(f"Missing values found in metrics: {missing_metrics}")

    pair_index = np.arange(len(df)) // 3
    grouped = df.assign(_pair_index=pair_index).groupby("_pair_index")
    if len(grouped) != 140:
        raise ValueError(f"Expected 140 question blocks, found {len(grouped)}")
    for _, group in grouped:
        if len(group) != 3:
            raise ValueError("Each question block must contain exactly 3 rows")
        if set(group["System"]) != set(SYSTEMS):
            raise ValueError(f"Question block has unexpected system set: {set(group['System'])}")
        if group["Question"].nunique() != 1:
            raise ValueError("Each question block must contain one shared question text")


def save_checkpoint(status: str, row_count: int, result_count: int) -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "phase": "phase4_statistical_analysis",
        "status": status,
        "source_file": str(SOURCE_FILE),
        "row_count": row_count,
        "result_count": result_count,
        "last_updated": datetime.now().isoformat(),
    }
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))


def atomic_write_csv(df: pd.DataFrame, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.with_suffix(target.suffix + ".tmp")
    df.to_csv(temp_path, index=False)
    temp_path.replace(target)


def cohen_dz(differences: pd.Series) -> float:
    values = pd.to_numeric(differences, errors="coerce").dropna().astype(float)
    if len(values) < 2:
        return float("nan")
    std = values.std(ddof=1)
    if std == 0 or math.isnan(std):
        return float("nan")
    return float(values.mean() / std)


def confidence_interval_mean(series: pd.Series) -> tuple[float, float, float]:
    values = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    n = len(values)
    mean = float(values.mean())
    if n < 2:
        return mean, float("nan"), float("nan")
    std = float(values.std(ddof=1))
    sem = std / math.sqrt(n)
    margin = stats.t.ppf(0.975, n - 1) * sem
    return mean, mean - margin, mean + margin


def interpret_result(mean_diff: float, p_value: float, effect_size: float) -> str:
    direction = "improved" if mean_diff > 0 else "reduced" if mean_diff < 0 else "did not change"
    magnitude = abs(effect_size)
    if math.isnan(effect_size):
        effect = "unclear effect size"
    elif magnitude < 0.2:
        effect = "negligible effect"
    elif magnitude < 0.5:
        effect = "small effect"
    elif magnitude < 0.8:
        effect = "medium effect"
    else:
        effect = "large effect"

    if p_value < 0.001:
        significance = "highly significant"
    elif p_value < 0.05:
        significance = "statistically significant"
    else:
        significance = "not statistically significant"

    return f"{direction.capitalize()} {significance} with a {effect}."


def shapiro_or_normality(values: pd.Series) -> tuple[float, bool]:
    cleaned = pd.to_numeric(values, errors="coerce").dropna().astype(float)
    if len(cleaned) < 3:
        return float("nan"), False
    if len(cleaned) > 5000:
        sample = cleaned.sample(n=5000, random_state=42)
    else:
        sample = cleaned
    stat, p_value = stats.shapiro(sample)
    return float(p_value), bool(p_value >= 0.05)


def paired_analysis(df: pd.DataFrame) -> pd.DataFrame:
    paired_source = df.copy().reset_index(drop=True)
    paired_source["pair_index"] = np.arange(len(paired_source)) // 3
    rows = []
    for metric, metric_label in METRICS:
        pivot = paired_source.pivot(index="pair_index", columns="System", values=metric).reindex(columns=SYSTEMS)

        for left_system, right_system in PAIRINGS:
            paired = pivot[[left_system, right_system]].dropna()
            left = paired[left_system].astype(float)
            right = paired[right_system].astype(float)
            differences = right - left

            t_stat, p_value = stats.ttest_rel(right, left)
            shapiro_p, normality_met = shapiro_or_normality(differences)
            if len(differences) > 0:
                try:
                    wilcoxon_stat, wilcoxon_p = stats.wilcoxon(right, left, zero_method="wilcox", alternative="two-sided")
                except ValueError:
                    wilcoxon_stat, wilcoxon_p = float("nan"), float("nan")
            else:
                wilcoxon_stat, wilcoxon_p = float("nan"), float("nan")
            mean_diff = float(differences.mean())
            std_diff = float(differences.std(ddof=1)) if len(differences) > 1 else float("nan")
            dz = cohen_dz(differences)
            sem = std_diff / math.sqrt(len(differences)) if len(differences) > 1 and not math.isnan(std_diff) else float("nan")
            ci_low = mean_diff - stats.t.ppf(0.975, len(differences) - 1) * sem if len(differences) > 1 else float("nan")
            ci_high = mean_diff + stats.t.ppf(0.975, len(differences) - 1) * sem if len(differences) > 1 else float("nan")
            selected_test = "paired t-test" if normality_met else "Wilcoxon signed-rank"
            selected_p = p_value if normality_met else wilcoxon_p

            rows.append({
                "metric": metric_label,
                "left_system": left_system,
                "right_system": right_system,
                "comparison": f"{left_system} → {right_system}",
                "n_pairs": len(differences),
                "mean_left": float(left.mean()),
                "mean_right": float(right.mean()),
                "mean_difference": mean_diff,
                "std_difference": std_diff,
                "ci95_low": ci_low,
                "ci95_high": ci_high,
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "wilcoxon_statistic": float(wilcoxon_stat),
                "wilcoxon_p_value": float(wilcoxon_p),
                "shapiro_p_value": shapiro_p,
                "normality_met": normality_met,
                "selected_test": selected_test,
                "selected_p_value": float(selected_p) if pd.notna(selected_p) else float("nan"),
                "cohen_dz": dz,
                "interpretation": interpret_result(mean_diff, p_value, dz),
            })

    results = pd.DataFrame(rows)
    return results.round(4)


def assumption_checks(df: pd.DataFrame) -> pd.DataFrame:
    paired_source = df.copy().reset_index(drop=True)
    paired_source["pair_index"] = np.arange(len(paired_source)) // 3
    rows = []
    for metric, metric_label in METRICS:
        pivot = paired_source.pivot(index="pair_index", columns="System", values=metric).reindex(columns=SYSTEMS)
        for left_system, right_system in PAIRINGS:
            paired = pivot[[left_system, right_system]].dropna()
            differences = paired[right_system].astype(float) - paired[left_system].astype(float)
            shapiro_p, normality_met = shapiro_or_normality(differences)
            rows.append({
                "metric": metric_label,
                "left_system": left_system,
                "right_system": right_system,
                "comparison": f"{left_system} → {right_system}",
                "n_pairs": len(differences),
                "shapiro_p_value": shapiro_p,
                "normality_met": normality_met,
                "recommended_test": "paired t-test" if normality_met else "Wilcoxon signed-rank",
                "assumption_note": (
                    "Paired difference normality acceptable." if normality_met else "Paired difference normality not met; Wilcoxon signed-rank is the safer non-parametric alternative."
                ),
            })
    return pd.DataFrame(rows).round(4)


def metric_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric, metric_label in METRICS:
        for system in SYSTEMS:
            series = pd.to_numeric(df.loc[df["System"] == system, metric], errors="coerce")
            rows.append({
                "metric": metric_label,
                "system": system,
                "count": int(series.count()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
            })
    summary = pd.DataFrame(rows)
    return summary.round(4)


def create_plots(df: pd.DataFrame, stats_df: pd.DataFrame) -> None:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    comparison_labels = [
        "Single-Agent RAG → Multi-Agent RAG",
        "Single-Agent RAG → Multi-Agent RAG + UQ",
        "Multi-Agent RAG → Multi-Agent RAG + UQ",
    ]
    metric_labels = [label for _, label in METRICS]

    difference_matrix = stats_df.pivot(index="metric", columns="comparison", values="mean_difference")
    effect_matrix = stats_df.pivot(index="metric", columns="comparison", values="cohen_dz")
    pvalue_matrix = stats_df.pivot(index="metric", columns="comparison", values="p_value")

    def plot_heatmap(matrix: pd.DataFrame, title: str, filename: str, cmap: str, fmt: str) -> None:
        display = matrix.copy()
        display.columns = comparison_labels
        display = display.reindex(metric_labels)

        fig, ax = plt.subplots(figsize=(10, 5))
        im = ax.imshow(display.values, aspect="auto", cmap=cmap)
        ax.set_xticks(np.arange(len(comparison_labels)))
        ax.set_xticklabels(comparison_labels, rotation=20, ha="right")
        ax.set_yticks(np.arange(len(metric_labels)))
        ax.set_yticklabels(metric_labels)
        ax.set_title(title)

        for i in range(display.shape[0]):
            for j in range(display.shape[1]):
                value = display.iloc[i, j]
                if pd.isna(value):
                    text = "NA"
                elif fmt == "percent":
                    text = f"{value:.1%}"
                elif fmt == "p":
                    text = f"{value:.3f}"
                else:
                    text = f"{value:.3f}"
                ax.text(j, i, text, ha="center", va="center", color="black", fontsize=8)

        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(PLOT_DIR / filename, dpi=200)
        plt.close(fig)

    plot_heatmap(difference_matrix, "Mean Paired Difference by Metric", "phase4_mean_difference_heatmap.png", "coolwarm", "decimal")
    plot_heatmap(effect_matrix, "Cohen's dz by Metric", "phase4_effect_size_heatmap.png", "viridis", "decimal")
    plot_heatmap(pvalue_matrix, "Paired Test p-values by Metric", "phase4_pvalue_heatmap.png", "magma_r", "p")

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True)
    axes = axes.flatten()
    for axis, (metric, metric_label) in zip(axes, METRICS):
        subset = df[["System", metric]].copy()
        subset[metric] = pd.to_numeric(subset[metric], errors="coerce")
        grouped = [subset.loc[subset["System"] == system, metric].dropna().astype(float).values for system in SYSTEMS]
        axis.boxplot(grouped, tick_labels=SYSTEMS, showmeans=True)
        axis.set_title(metric_label)
        axis.set_ylim(0, 1)
        axis.tick_params(axis="x", rotation=15)
        axis.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        axis.grid(True, axis="y", alpha=0.25)

    fig.suptitle("Metric Distributions by System")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(PLOT_DIR / "phase4_metric_boxplots.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharey=True)
    axes = axes.flatten()
    x_positions = np.arange(len(SYSTEMS))
    colors = ["#4C72B0", "#55A868", "#C44E52"]
    for axis, (metric, metric_label) in zip(axes, METRICS):
        means = []
        lower_errors = []
        upper_errors = []
        for system in SYSTEMS:
            series = pd.to_numeric(df.loc[df["System"] == system, metric], errors="coerce")
            mean, ci_low, ci_high = confidence_interval_mean(series)
            means.append(mean)
            lower_errors.append(mean - ci_low if not pd.isna(ci_low) else 0.0)
            upper_errors.append(ci_high - mean if not pd.isna(ci_high) else 0.0)

        axis.bar(x_positions, means, yerr=[lower_errors, upper_errors], capsize=5, color=colors, alpha=0.9)
        axis.set_xticks(x_positions)
        axis.set_xticklabels(SYSTEMS, rotation=15)
        axis.set_ylim(0, 1)
        axis.set_title(metric_label)
        axis.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        axis.grid(True, axis="y", alpha=0.25)

    fig.suptitle("Mean Metric Values with 95% Confidence Intervals")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(PLOT_DIR / "phase4_metric_mean_ci_barchart.png", dpi=200)
    plt.close(fig)


def main() -> None:
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("PHASE 4: STATISTICAL ANALYSIS")
    logger.info("=" * 80)

    save_checkpoint("starting", 0, 0)

    df = load_source(logger)
    validate_source(df)
    logger.info(f"Loaded {len(df)} rows for statistical analysis")

    summary_df = metric_summary(df)
    assumption_df = assumption_checks(df)
    stats_df = paired_analysis(df)

    atomic_write_csv(summary_df, SUMMARY_FILE)
    atomic_write_csv(assumption_df, ASSUMPTION_FILE)
    atomic_write_csv(stats_df, OUTPUT_FILE)
    create_plots(df, stats_df)

    save_checkpoint("complete", len(df), len(stats_df))

    logger.info(f"Saved summary statistics to {SUMMARY_FILE}")
    logger.info(f"Saved assumption checks to {ASSUMPTION_FILE}")
    logger.info(f"Saved paired statistics to {OUTPUT_FILE}")
    logger.info(f"Saved plots to {PLOT_DIR}")
    logger.info("Phase 4 statistical analysis complete")


if __name__ == "__main__":
    main()
