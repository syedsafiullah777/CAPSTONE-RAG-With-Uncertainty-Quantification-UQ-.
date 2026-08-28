"""Read-only frozen FinQA 140-question catalogue for the live artefact UI.

Loads only ``data/final/selected_140_questions.csv``.
Does not run RAG, call the LLM, or read Phase 15/16 result files.
Does not write the CSV.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from src.config import get_path, load_experiment_config

FROZEN_N = 140
PAGE_SIZE = 20
CATALOGUE_CSV_REL = "data/final/selected_140_questions.csv"
APP_PAGES = (
    "Live RAG Demo",
    "Benchmark Results",
    "Benchmark Questions",
)

# Display/filter fields only. Gold context/table/pre_text/post_text are not shown.
CATALOGUE_FIELDS = (
    "id",
    "question",
    "company_name",
    "company_symbol",
    "report_year",
    "file_name",
    "page_number",
    "split",
    "context_id",
    "company_sector",
    "program_answer",
)

ALL_COMPANIES = "All"


def frozen_catalogue_path() -> Path:
    return get_path(load_experiment_config(), "data_final") / "selected_140_questions.csv"


def load_frozen_catalogue() -> list[dict[str, str]]:
    """Read the frozen 140-question CSV (read-only)."""
    csv_path = frozen_catalogue_path()
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append({field: str(raw.get(field) or "").strip() for field in CATALOGUE_FIELDS})
    return rows


def validate_catalogue(rows: list[dict[str, str]]) -> dict[str, Any]:
    ids = [row["id"] for row in rows]
    questions = [row["question"] for row in rows]
    return {
        "n": len(rows),
        "unique_ids": len(set(ids)),
        "empty_ids": sum(1 for item in ids if not item),
        "empty_questions": sum(1 for item in questions if not item),
        "ok": len(rows) == FROZEN_N and len(set(ids)) == FROZEN_N and all(ids) and all(questions),
    }


def company_options(rows: list[dict[str, str]]) -> list[str]:
    names = sorted({row.get("company_name") or "" for row in rows if (row.get("company_name") or "").strip()})
    return [ALL_COMPANIES, *names]


def filter_catalogue(
    rows: list[dict[str, str]],
    *,
    id_query: str = "",
    text_query: str = "",
    company: str = ALL_COMPANIES,
) -> list[dict[str, str]]:
    id_q = (id_query or "").strip().lower()
    text_q = (text_query or "").strip().lower()
    company_q = (company or ALL_COMPANIES).strip()
    out: list[dict[str, str]] = []
    for row in rows:
        if id_q and id_q not in row["id"].lower():
            continue
        if text_q and text_q not in row["question"].lower():
            continue
        if company_q and company_q != ALL_COMPANIES and row.get("company_name") != company_q:
            continue
        out.append(row)
    return out


def paginate(
    rows: list[dict[str, str]],
    page: int,
    page_size: int = PAGE_SIZE,
) -> tuple[list[dict[str, str]], int, int, int, int, int]:
    """Return (page_rows, showing_from, showing_to, n_total, page, n_pages)."""
    n = len(rows)
    n_pages = max(1, (n + page_size - 1) // page_size) if n else 1
    page = min(max(1, int(page)), n_pages)
    start = (page - 1) * page_size
    end = min(start + page_size, n)
    showing_from = start + 1 if n else 0
    return rows[start:end], showing_from, end, n, page, n_pages


def live_prefill_from_row(row: dict[str, str]) -> dict[str, str]:
    """Question text only for Live RAG Demo. Does not copy gold or Phase 15 answers."""
    return {
        "question": row.get("question") or "",
        "source_id": row.get("id") or "",
    }
