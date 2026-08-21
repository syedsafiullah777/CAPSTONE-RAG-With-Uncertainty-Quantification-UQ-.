"""Phase 4: filter FinQA test split and freeze a reproducible 140-question set.

Does not build a knowledge base or select calibration data (Phase 5).
"""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
from typing import Any


EXPORT_COLUMNS = [
    "id",
    "context_id",
    "split",
    "question",
    "program_answer",
    "original_answer",
    "context",
    "table",
    "pre_text",
    "post_text",
    "file_name",
    "company_name",
    "company_symbol",
    "report_year",
    "page_number",
    "company_sector",
    "company_industry",
    "company_headquarters",
    "company_cik",
    "company_founded",
    "repo_pdf_path",
]


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def normalize_question(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def repo_pdf_path(split: str, file_name: str) -> str:
    return f"data/FinQA/{split}/{file_name}"


def row_to_record(row: dict[str, Any], split: str) -> dict[str, Any]:
    record = {col: row.get(col) for col in EXPORT_COLUMNS if col != "repo_pdf_path"}
    record["split"] = split
    record["repo_pdf_path"] = repo_pdf_path(split, str(row.get("file_name", "")))
    # Serialize non-JSON-friendly values for CSV/JSON stability.
    for key, value in list(record.items()):
        if value is None:
            record[key] = ""
        elif hasattr(value, "isoformat"):
            record[key] = value.isoformat()
        else:
            record[key] = value
    return record


def is_essential_eligible(row: dict[str, Any]) -> bool:
    if _is_empty(row.get("id")):
        return False
    if _is_empty(row.get("question")):
        return False
    if _is_empty(row.get("program_answer")):
        # Primary evaluation field must exist for the frozen test set.
        return False
    if _is_empty(row.get("context_id")):
        return False
    if _is_empty(row.get("file_name")):
        return False
    if _is_empty(row.get("context")):
        return False
    return True


def filter_and_dedupe(rows: list[dict[str, Any]], split: str = "test") -> dict[str, Any]:
    """Filter malformed rows and dedupe by normalized question (keep lowest id)."""
    stats = {
        "input_rows": len(rows),
        "dropped_not_essential": 0,
        "dropped_duplicate_question": 0,
    }
    eligible: list[dict[str, Any]] = []
    for row in rows:
        if not is_essential_eligible(row):
            stats["dropped_not_essential"] += 1
            continue
        eligible.append(row_to_record(dict(row), split))

    # Deterministic dedupe: sort by id, keep first occurrence of normalized question.
    eligible.sort(key=lambda r: str(r["id"]))
    seen_questions: set[str] = set()
    unique: list[dict[str, Any]] = []
    for row in eligible:
        key = normalize_question(str(row["question"]))
        if key in seen_questions:
            stats["dropped_duplicate_question"] += 1
            continue
        seen_questions.add(key)
        unique.append(row)

    stats["eligible_unique_questions"] = len(unique)
    return {"rows": unique, "stats": stats}


def stratified_sample(
    rows: list[dict[str, Any]],
    *,
    n: int = 140,
    seed: int = 42,
    max_per_company: int = 3,
    max_per_file: int = 1,
) -> dict[str, Any]:
    """Greedy stratified sample with company and file caps.

    Rows are shuffled with a seeded RNG, then accepted if they do not exceed
    ``max_per_company`` (by company_symbol, fallback company_name) or
    ``max_per_file`` (by file_name). Caps relax once if n cannot be reached.
    """
    if n > len(rows):
        raise ValueError(f"Requested n={n} exceeds eligible pool size {len(rows)}")

    rng = random.Random(seed)
    order = list(rows)
    rng.shuffle(order)

    def _company_key(row: dict[str, Any]) -> str:
        symbol = str(row.get("company_symbol") or "").strip()
        if symbol:
            return f"sym:{symbol}"
        name = str(row.get("company_name") or "").strip()
        if name:
            return f"name:{name}"
        return "unknown"

    def _select(cap_company: int, cap_file: int) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        company_counts: Counter[str] = Counter()
        file_counts: Counter[str] = Counter()
        for row in order:
            if len(selected) >= n:
                break
            company = _company_key(row)
            file_name = str(row.get("file_name") or "")
            if company_counts[company] >= cap_company:
                continue
            if file_counts[file_name] >= cap_file:
                continue
            selected.append(row)
            company_counts[company] += 1
            file_counts[file_name] += 1
        return selected

    caps_used = {"max_per_company": max_per_company, "max_per_file": max_per_file}
    selected = _select(max_per_company, max_per_file)
    if len(selected) < n:
        caps_used = {"max_per_company": max_per_company + 1, "max_per_file": max_per_file + 1}
        selected = _select(max_per_company + 1, max_per_file + 1)
    if len(selected) < n:
        caps_used = {"max_per_company": max_per_company + 2, "max_per_file": max_per_file + 2}
        selected = _select(max_per_company + 2, max_per_file + 2)
    if len(selected) < n:
        raise RuntimeError(
            f"Could only select {len(selected)}/{n} rows under diversity caps {caps_used}"
        )

    # Stable output order by id for readable diffs; selection set is what matters.
    selected_sorted = sorted(selected, key=lambda r: str(r["id"]))
    company_dist = Counter(_company_key(r) for r in selected_sorted)
    file_dist = Counter(str(r.get("file_name") or "") for r in selected_sorted)
    year_dist = Counter(str(r.get("report_year") or "") for r in selected_sorted)

    return {
        "rows": selected_sorted,
        "seed": seed,
        "n": len(selected_sorted),
        "caps_used": caps_used,
        "unique_companies": len(company_dist),
        "unique_files": len(file_dist),
        "max_questions_per_company": max(company_dist.values()) if company_dist else 0,
        "max_questions_per_file": max(file_dist.values()) if file_dist else 0,
        "company_distribution": dict(sorted(company_dist.items())),
        "report_year_distribution": dict(sorted(year_dist.items())),
    }


def rows_fingerprint(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps([r["id"] for r in rows], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in EXPORT_COLUMNS})


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")


def freeze_test_140(
    test_rows: list[dict[str, Any]],
    *,
    output_csv: Path,
    output_manifest: Path,
    n: int = 140,
    seed: int = 42,
    max_per_company: int = 3,
    max_per_file: int = 1,
    dataset_id: str = "G4KMU/t2-ragbench",
    subset: str = "FinQA",
) -> dict[str, Any]:
    filtered = filter_and_dedupe(test_rows, split="test")
    sampled = stratified_sample(
        filtered["rows"],
        n=n,
        seed=seed,
        max_per_company=max_per_company,
        max_per_file=max_per_file,
    )
    write_csv(output_csv, sampled["rows"])
    manifest = {
        "phase": 4,
        "frozen": True,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": dataset_id,
        "subset": subset,
        "source_split": "test",
        "n": sampled["n"],
        "sampling_seed": seed,
        "filter_rules": {
            "require_non_empty": [
                "id",
                "question",
                "program_answer",
                "context_id",
                "file_name",
                "context",
            ],
            "dedupe": "normalize_question keep_lowest_id",
        },
        "diversity_caps_requested": {
            "max_per_company": max_per_company,
            "max_per_file": max_per_file,
        },
        "diversity_caps_used": sampled["caps_used"],
        "filter_stats": filtered["stats"],
        "unique_companies": sampled["unique_companies"],
        "unique_files": sampled["unique_files"],
        "max_questions_per_company": sampled["max_questions_per_company"],
        "max_questions_per_file": sampled["max_questions_per_file"],
        "report_year_distribution": sampled["report_year_distribution"],
        "selected_ids": [r["id"] for r in sampled["rows"]],
        "selected_ids_sha256": rows_fingerprint(sampled["rows"]),
        "output_csv": str(output_csv),
        "note": (
            "Do not alter this freeze because of experimental results. "
            "Calibration data is selected separately from FinQA dev (Phase 5)."
        ),
    }
    write_manifest(output_manifest, manifest)
    return {"rows": sampled["rows"], "manifest": manifest}
