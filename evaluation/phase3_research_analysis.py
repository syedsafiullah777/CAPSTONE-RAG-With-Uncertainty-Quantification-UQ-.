#!/usr/bin/env python3
"""Phase 3 research analysis: build a master dataset and summary statistics from saved RAGAS results."""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, PercentFormatter
import pandas as pd


WORKSPACE = Path(__file__).resolve().parent.parent
RESULTS_DIR = WORKSPACE / "results"
CHECKPOINT_DIR = RESULTS_DIR / ".checkpoints"
SOURCE_FILE = RESULTS_DIR / "evaluation_results_final.csv"
LEGACY_SOURCE_FILE = RESULTS_DIR / "evaluation_results.csv"
MASTER_FILE = RESULTS_DIR / "phase3_master_dataset.csv"
SUMMARY_FILE = RESULTS_DIR / "phase3_summary_statistics.csv"
COMPARISON_FILE = RESULTS_DIR / "phase3_comparison_table.csv"
THRESHOLD_FILE = RESULTS_DIR / "phase3_threshold_analysis.csv"
THRESHOLD_PLOT_DIR = RESULTS_DIR / "phase3_threshold_plots"
CHECKPOINT_FILE = CHECKPOINT_DIR / "phase3_analysis_checkpoint.json"
MASTER_BACKUP_FILE = RESULTS_DIR / "phase3_master_dataset.before_update.csv"
FINAL_BACKUP_FILE = RESULTS_DIR / "evaluation_results_final.before_update.csv"

REQUIRED_COLUMNS = [
    "question",
    "system",
    "ragas_faithfulness",
    "ragas_answer_correctness",
    "ragas_context_precision",
    "ragas_context_recall",
    "confidence",
    "response_time",
]

FINAL_REQUIRED_COLUMNS = [
    "Question",
    "Ground Truth",
    "Retrieved Context",
    "Generated Answer",
    "System",
    "Question ID",
]

MASTER_COLUMNS = [
    "dataset",
    "question",
    "ground_truth",
    "system",
    "answer",
    "ragas_faithfulness",
    "ragas_answer_correctness",
    "ragas_context_precision",
    "ragas_context_recall",
    "confidence",
    "response_time",
    "decision",
    "retrieval_score",
    "verification_score",
    "consistency_score",
    "sources",
    "accuracy",
    "faithfulness",
    "context_precision",
    "hallucinated",
    "abstained",
]


def setup_logging() -> logging.Logger:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("Phase3ResearchAnalysis")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(RESULTS_DIR / "phase3.log", mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())
    return logger


def load_source(logger: logging.Logger) -> pd.DataFrame:
    source_path = SOURCE_FILE if SOURCE_FILE.exists() else LEGACY_SOURCE_FILE
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE_FILE} or {LEGACY_SOURCE_FILE}")

    logger.info(f"Loading source results from {source_path}")
    df = pd.read_csv(source_path)

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in source file: {missing}")

    if not pd.api.types.is_numeric_dtype(df["confidence"]):
        df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce")
    if not pd.api.types.is_numeric_dtype(df["response_time"]):
        df["response_time"] = pd.to_numeric(df["response_time"], errors="coerce")

    return df


def validate_final_dataset(df: pd.DataFrame) -> None:
    if len(df) != 420:
        raise ValueError(f"Expected 420 evaluated rows, found {len(df)}")

    counts = df["system"].value_counts(dropna=False).to_dict()
    if sorted(counts.values()) != [140, 140, 140]:
        raise ValueError(f"Expected 140 rows per system, found {counts}")

    metric_columns = [
        "ragas_faithfulness",
        "ragas_answer_correctness",
        "ragas_context_precision",
        "ragas_context_recall",
    ]

    for column in metric_columns + ["confidence", "response_time"]:
        series = pd.to_numeric(df[column], errors="coerce")
        if series.isna().any():
            raise ValueError(f"Column {column} contains NaN/invalid values")
        if column in metric_columns and ((series < 0).any() or (series > 1).any()):
            raise ValueError(f"Metric column {column} has values outside 0..1")
        if column == "confidence" and ((series < 0).any() or (series > 1).any()):
            raise ValueError("Confidence must be between 0 and 1")
        if column == "response_time" and (series <= 0).any():
            raise ValueError("Response time must be positive")

    if df.duplicated().any():
        raise ValueError("Final dataset contains duplicate rows")

    if df.duplicated(subset=["Question ID", "System"]).any():
        raise ValueError("Final dataset contains duplicate Question ID/System pairs")

    missing_required = [col for col in FINAL_REQUIRED_COLUMNS if col not in df.columns]
    if missing_required:
        raise ValueError(f"Missing required presentation columns: {missing_required}")

    for column in FINAL_REQUIRED_COLUMNS:
        empty_mask = df[column].astype(str).str.strip().eq("") | df[column].isna()
        if empty_mask.any():
            raise ValueError(f"Column {column} contains empty cells")


def freeze_final_dataset(df: pd.DataFrame) -> pd.DataFrame:
    final_path = SOURCE_FILE
    final_path.parent.mkdir(parents=True, exist_ok=True)
    if final_path.exists():
        backup_existing_file(final_path, FINAL_BACKUP_FILE)
    atomic_write_csv(df, final_path)
    try:
        final_path.chmod(0o444)
    except Exception:
        pass
    return df


def build_master_dataset(df: pd.DataFrame) -> pd.DataFrame:
    master = df.copy()

    for column in MASTER_COLUMNS:
        if column not in master.columns:
            master[column] = pd.NA

    master = master[MASTER_COLUMNS].copy()
    return master


def atomic_write_csv(df: pd.DataFrame, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.with_suffix(target.suffix + ".tmp")
    df.to_csv(temp_path, index=False)
    temp_path.replace(target)


def backup_existing_file(path: Path, backup_path: Path) -> None:
    if path.exists():
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if backup_path.exists():
                try:
                    backup_path.chmod(0o644)
                except Exception:
                    pass
            shutil.copy2(path, backup_path)
        except PermissionError:
            try:
                if backup_path.exists():
                    backup_path.unlink()
            except Exception:
                pass
            shutil.copy2(path, backup_path)


def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        ("ragas_faithfulness", "faithfulness"),
        ("ragas_answer_correctness", "answer_correctness"),
        ("ragas_context_precision", "context_precision"),
        ("ragas_context_recall", "context_recall"),
        ("confidence", "confidence"),
        ("response_time", "response_time"),
    ]

    rows = []
    grouped = list(df.groupby("system", dropna=False))
    grouped.append(("Overall", df))

    for system_name, frame in grouped:
        row = {"system": system_name, "count": len(frame)}
        row["answered_count"] = int((frame["decision"] == "Answer").sum()) if "decision" in frame.columns else 0
        row["warning_count"] = int((frame["decision"] == "Answer with warning").sum()) if "decision" in frame.columns else 0
        row["abstained_count"] = int((frame["decision"] == "Abstain").sum()) if "decision" in frame.columns else 0
        row["abstention_rate"] = float(frame["abstained"].mean()) if "abstained" in frame.columns else 0.0
        for source_col, prefix in metrics:
            series = pd.to_numeric(frame[source_col], errors="coerce")
            row[f"{prefix}_mean"] = series.mean()
            row[f"{prefix}_median"] = series.median()
            row[f"{prefix}_std"] = series.std()
            row[f"{prefix}_min"] = series.min()
            row[f"{prefix}_max"] = series.max()
        rows.append(row)

    summary = pd.DataFrame(rows)
    return summary.round(4)


def compute_comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    metric_map = [
        ("ragas_faithfulness", "Faithfulness"),
        ("ragas_answer_correctness", "Answer Correctness"),
        ("ragas_context_precision", "Context Precision"),
        ("ragas_context_recall", "Context Recall"),
        ("confidence", "Confidence"),
        ("response_time", "Response Time"),
    ]

    rows = []
    grouped = list(df.groupby("system", dropna=False))
    for metric_column, display_name in metric_map:
        row = {"Metric": display_name}
        for system_name, frame in grouped:
            series = pd.to_numeric(frame[metric_column], errors="coerce")
            row[system_name] = f"{series.mean():.4f} ± {series.std():.4f}"
        rows.append(row)

    return pd.DataFrame(rows)


def compute_threshold_analysis(df: pd.DataFrame) -> pd.DataFrame:
    uq = df[df["system"] == "Multi-Agent RAG + UQ"].copy()
    answer_thresholds = [0.48, 0.49, 0.50, 0.51, 0.52, 0.53, 0.54, 0.55]
    warning_thresholds = [0.46, 0.47, 0.48, 0.49]
    baseline_accuracy = pd.to_numeric(uq["ragas_answer_correctness"], errors="coerce").mean()

    rows = []
    for warning_threshold in warning_thresholds:
        for answer_threshold in answer_thresholds:
            if answer_threshold <= warning_threshold:
                continue

            answer_count = int((uq["confidence"] >= answer_threshold).sum())
            warning_count = int(
                ((uq["confidence"] < answer_threshold) & (uq["confidence"] >= warning_threshold)).sum()
            )
            abstain_count = int((uq["confidence"] < warning_threshold).sum())
            answered = uq[uq["confidence"] >= answer_threshold]
            abstained = uq[uq["confidence"] < warning_threshold]
            answered_accuracy = pd.to_numeric(answered["ragas_answer_correctness"], errors="coerce").mean()
            expected_incorrect_answers_avoided = float((1 - pd.to_numeric(abstained["ragas_answer_correctness"], errors="coerce")).sum())
            accuracy_gain = answered_accuracy - baseline_accuracy if pd.notna(answered_accuracy) else pd.NA
            direct_answer_coverage = answer_count / 140
            all_response_coverage = (answer_count + warning_count) / 140

            rows.append({
                "answer_threshold": answer_threshold,
                "warning_threshold": warning_threshold,
                "answer_count": answer_count,
                "warning_count": warning_count,
                "abstain_count": abstain_count,
                "answered_accuracy": answered_accuracy,
                "baseline_accuracy": baseline_accuracy,
                "accuracy_gain": accuracy_gain,
                "expected_incorrect_answers_avoided": expected_incorrect_answers_avoided,
                "coverage_all_responses": all_response_coverage,
                "coverage_direct_answers": direct_answer_coverage,
            })

    threshold_table = pd.DataFrame(rows)
    threshold_table["answer_share"] = (threshold_table["answer_count"] / 140).round(4)
    threshold_table["warning_share"] = (threshold_table["warning_count"] / 140).round(4)
    threshold_table["abstain_share"] = (threshold_table["abstain_count"] / 140).round(4)
    threshold_table["answered_accuracy"] = threshold_table["answered_accuracy"].round(4)
    threshold_table["baseline_accuracy"] = threshold_table["baseline_accuracy"].round(4)
    threshold_table["accuracy_gain"] = threshold_table["accuracy_gain"].round(4)
    threshold_table["expected_incorrect_answers_avoided"] = threshold_table["expected_incorrect_answers_avoided"].round(4)
    threshold_table["coverage_all_responses"] = threshold_table["coverage_all_responses"].round(4)
    threshold_table["coverage_direct_answers"] = threshold_table["coverage_direct_answers"].round(4)
    return threshold_table


def create_threshold_plots(threshold_table: pd.DataFrame) -> None:
    THRESHOLD_PLOT_DIR.mkdir(parents=True, exist_ok=True)
    representative_warning_threshold = 0.48

    plot_specs = [
        ("answer_threshold", "answered_accuracy", "Threshold vs Answered Accuracy", "Answered Accuracy", "threshold_vs_answered_accuracy.png", "decimal"),
        ("answer_threshold", "abstain_share", "Threshold vs Abstention Rate", "Abstention Rate", "threshold_vs_abstention_rate.png", "percent"),
        ("answer_threshold", "coverage_all_responses", "Threshold vs Coverage (All Responses)", "Coverage (Answer + Warning)", "threshold_vs_coverage_all_responses.png", "percent"),
        ("answer_threshold", "coverage_direct_answers", "Threshold vs Coverage (Direct Answers)", "Coverage (Answer Only)", "threshold_vs_coverage_direct_answers.png", "percent"),
        ("answer_threshold", "expected_incorrect_answers_avoided", "Threshold vs Expected Incorrect Answers Avoided", "Expected Incorrect Answers Avoided", "threshold_vs_expected_incorrect_answers_avoided.png", "decimal"),
        ("coverage_direct_answers", "answered_accuracy", "Coverage vs Answered Accuracy", "Answered Accuracy", "coverage_vs_answered_accuracy.png", "decimal"),
    ]

    for x_col, y_col, title, y_label, filename, value_style in plot_specs:
        fig, ax = plt.subplots(figsize=(8, 5))
        if x_col in {"answer_threshold"}:
            subset = threshold_table[threshold_table["warning_threshold"] == representative_warning_threshold].sort_values(x_col)
            label = f"warning >= {representative_warning_threshold:.2f}"
            ax.plot(subset[x_col], subset[y_col], marker="o", linewidth=2.5, label=label)
            for x_value, y_value in zip(subset[x_col], subset[y_col]):
                if value_style == "percent":
                    point_label = f"{y_value * 100:.1f}%"
                else:
                    point_label = f"{y_value:.3f}"
                ax.annotate(point_label, (x_value, y_value), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=7)
        else:
            subset = threshold_table.sort_values(x_col)
            ax.plot(subset[x_col], subset[y_col], marker="o", linewidth=2.5)
            for x_value, y_value in zip(subset[x_col], subset[y_col]):
                if value_style == "percent":
                    point_label = f"{y_value * 100:.1f}%"
                else:
                    point_label = f"{y_value:.3f}"
                ax.annotate(point_label, (x_value, y_value), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=7)

        ax.set_title(title)
        if x_col == "coverage_direct_answers":
            ax.set_xlabel("Coverage (Direct Answers)")
        else:
            ax.set_xlabel("Confidence Threshold")
        ax.set_ylabel(y_label)
        if value_style == "percent":
            ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
        else:
            ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
        if x_col == "coverage_direct_answers":
            ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
        else:
            ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.grid(True, alpha=0.25)
        if x_col == "answer_threshold":
            ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(THRESHOLD_PLOT_DIR / filename, dpi=200)
        plt.close(fig)


def save_checkpoint(status: str, master_rows: int, summary_rows: int) -> None:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "phase": "phase3_research_analysis",
        "status": status,
        "source_file": str(SOURCE_FILE),
        "master_file": str(MASTER_FILE),
        "summary_file": str(SUMMARY_FILE),
        "master_rows": master_rows,
        "summary_rows": summary_rows,
        "last_updated": datetime.now().isoformat(),
    }
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))


def main() -> None:
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("PHASE 3: RESEARCH ANALYSIS")
    logger.info("=" * 80)

    save_checkpoint("starting", 0, 0)

    df = load_source(logger)
    logger.info(f"Loaded {len(df)} rows from phase 2 results")
    validate_final_dataset(df)
    freeze_final_dataset(df)

    master = build_master_dataset(df)
    summary = compute_summary(df)
    comparison = compute_comparison_table(df)
    threshold_analysis = compute_threshold_analysis(df)
    create_threshold_plots(threshold_analysis)

    backup_existing_file(MASTER_FILE, MASTER_BACKUP_FILE)
    backup_existing_file(SUMMARY_FILE, SUMMARY_FILE.with_suffix(".before_update.csv"))
    backup_existing_file(COMPARISON_FILE, COMPARISON_FILE.with_suffix(".before_update.csv"))
    backup_existing_file(THRESHOLD_FILE, THRESHOLD_FILE.with_suffix(".before_update.csv"))

    atomic_write_csv(master, MASTER_FILE)
    atomic_write_csv(summary, SUMMARY_FILE)
    atomic_write_csv(comparison, COMPARISON_FILE)
    atomic_write_csv(threshold_analysis, THRESHOLD_FILE)

    save_checkpoint("complete", len(master), len(summary))

    logger.info(f"Saved master dataset to {MASTER_FILE}")
    logger.info(f"Saved summary statistics to {SUMMARY_FILE}")
    logger.info(f"Saved comparison table to {COMPARISON_FILE}")
    logger.info(f"Saved threshold analysis to {THRESHOLD_FILE}")
    logger.info(f"Master rows: {len(master)}")
    logger.info(f"Summary rows: {len(summary)}")
    logger.info(f"Threshold rows: {len(threshold_analysis)}")
    logger.info("Phase 3 research analysis complete")


if __name__ == "__main__":
    main()