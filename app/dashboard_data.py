from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError

from config import PROJECT_ROOT, RESULTS_DIR, SAMPLED_QUESTIONS_PATH


FINAL_RESULTS_PATH = RESULTS_DIR / "evaluation_results_final.csv"
PHASE3_SUMMARY_PATH = RESULTS_DIR / "phase3_summary_statistics.csv"
PHASE3_COMPARISON_PATH = RESULTS_DIR / "phase3_comparison_table.csv"
PHASE3_THRESHOLD_PATH = RESULTS_DIR / "phase3_threshold_analysis.csv"
PHASE5_REPORT_PATH = RESULTS_DIR / "phase5_calibration_report.csv"
PHASE5_METRICS_PATH = RESULTS_DIR / "phase5_calibration_metrics.csv"
PHASE5_BINS_PATH = RESULTS_DIR / "phase5_calibration_bins.csv"
PHASE2_SUMMARY_PATH = RESULTS_DIR / "phase2_summary.csv"
SUMMARY_BY_DATASET_PATH = RESULTS_DIR / "summary_by_dataset.csv"
SUMMARY_BY_SYSTEM_PATH = RESULTS_DIR / "summary_by_system.csv"
ERROR_ANALYSIS_PATH = RESULTS_DIR / "phase7_error_analysis.md"
SOURCE_DOCUMENTS_DIR = PROJECT_ROOT / "knowledge_base" / "documents"


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        frame = pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()
    frame.columns = [column.strip() for column in frame.columns]
    frame = frame.loc[:, ~frame.columns.duplicated()].copy()
    return frame


def _canonical_results(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    rename_map = {
        "Question ID": "question_id_alt",
        "Retrieved Context": "retrieved_context",
        "Generated Answer": "generated_answer",
        "Ground Truth": "ground_truth_alt",
    }
    return frame.rename(columns=rename_map)


@st.cache_data(show_spinner=False)
def load_final_results() -> pd.DataFrame:
    return _canonical_results(_read_csv(FINAL_RESULTS_PATH))


@st.cache_data(show_spinner=False)
def load_phase3_summary() -> pd.DataFrame:
    return _read_csv(PHASE3_SUMMARY_PATH)


@st.cache_data(show_spinner=False)
def load_phase3_comparison() -> pd.DataFrame:
    return _read_csv(PHASE3_COMPARISON_PATH)


@st.cache_data(show_spinner=False)
def load_phase3_threshold() -> pd.DataFrame:
    return _read_csv(PHASE3_THRESHOLD_PATH)


@st.cache_data(show_spinner=False)
def load_phase5_report() -> pd.DataFrame:
    return _read_csv(PHASE5_REPORT_PATH)


@st.cache_data(show_spinner=False)
def load_phase5_metrics() -> pd.DataFrame:
    return _read_csv(PHASE5_METRICS_PATH)


@st.cache_data(show_spinner=False)
def load_phase5_bins() -> pd.DataFrame:
    return _read_csv(PHASE5_BINS_PATH)


@st.cache_data(show_spinner=False)
def load_phase2_summary() -> pd.DataFrame:
    return _read_csv(PHASE2_SUMMARY_PATH)


@st.cache_data(show_spinner=False)
def load_summary_by_dataset() -> pd.DataFrame:
    return _read_csv(SUMMARY_BY_DATASET_PATH)


@st.cache_data(show_spinner=False)
def load_summary_by_system() -> pd.DataFrame:
    return _read_csv(SUMMARY_BY_SYSTEM_PATH)


@st.cache_data(show_spinner=False)
def load_error_analysis_text() -> str:
    return ERROR_ANALYSIS_PATH.read_text(encoding="utf-8") if ERROR_ANALYSIS_PATH.exists() else ""


def _extract_markdown_table(text: str) -> pd.DataFrame:
    rows = []
    for line in text.splitlines():
        if line.startswith("|") and line.count("|") >= 2:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            rows.append(cells)
    if len(rows) < 2:
        return pd.DataFrame()
    header = rows[0]
    body = [row for row in rows[2:] if len(row) == len(header)]
    if not body:
        return pd.DataFrame(columns=header)
    return pd.DataFrame(body, columns=header)


@st.cache_data(show_spinner=False)
def load_error_cases() -> pd.DataFrame:
    text = load_error_analysis_text()
    table = _extract_markdown_table(text)
    if table.empty:
        return table
    rename_map = {column: column.strip().lower().replace(" ", "_") for column in table.columns}
    return table.rename(columns=rename_map)


@st.cache_data(show_spinner=False)
def load_source_documents() -> pd.DataFrame:
    if not SOURCE_DOCUMENTS_DIR.exists():
        return pd.DataFrame(columns=["name", "path", "extension", "size_kb"])
    rows = []
    for path in sorted(SOURCE_DOCUMENTS_DIR.glob("**/*")):
        if path.is_file():
            rows.append(
                {
                    "name": path.stem,
                    "path": path,
                    "extension": path.suffix.lower().lstrip("."),
                    "size_kb": round(path.stat().st_size / 1024, 1),
                }
            )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_benchmark_question_count() -> int:
    frame = _read_csv(SAMPLED_QUESTIONS_PATH)
    return len(frame)


@st.cache_data(show_spinner=False)
def load_document_text(path: str) -> str:
    file_path = Path(path)
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return "Requires manual input."


def unique_questions(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    question_key = "question_id" if "question_id" in frame.columns else "Question ID"
    question_col = "question" if "question" in frame.columns else "Question"
    # Question IDs can be system-specific across runs; dedupe by dataset + question text.
    unique = frame[[question_key, question_col, "dataset"]].copy()
    unique[question_col] = unique[question_col].astype(str)
    unique["dataset"] = unique["dataset"].astype(str)
    unique["_question_norm"] = unique[question_col].str.strip().str.lower()
    unique = unique.drop_duplicates(subset=["dataset", "_question_norm"]).drop(columns=["_question_norm"])
    return unique.reset_index(drop=True)


def question_similarity(query: str, question: str) -> float:
    return SequenceMatcher(None, query.lower().strip(), question.lower().strip()).ratio()


def pick_best_question(frame: pd.DataFrame, query: str) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype="object")
    question_col = "question" if "question" in frame.columns else "Question"
    question_key = "question_id" if "question_id" in frame.columns else "Question ID"
    unique_frame = unique_questions(frame)[[question_key, question_col, "dataset"]].copy()
    unique_frame["score"] = unique_frame[question_col].map(lambda value: question_similarity(query, str(value)))
    return unique_frame.sort_values("score", ascending=False).iloc[0]


def format_percentage(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "Requires manual input."
    return f"{float(value) * 100:.1f}%"
