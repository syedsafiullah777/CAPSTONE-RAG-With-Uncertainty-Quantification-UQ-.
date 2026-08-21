"""Profile T²-RAGBench FinQA without selecting the frozen 140 set.

Phase 2 only: inspect schema, quality, and source-document availability.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


HF_DATASET_ID = "G4KMU/t2-ragbench"
HF_SUBSET = "FinQA"
EXPECTED_COLUMNS = [
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
    "company_date_added",
    "company_cik",
    "company_founded",
]


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _text_stats(values: list[str]) -> dict[str, Any]:
    lengths = [len(v) for v in values]
    if not lengths:
        return {"n": 0}
    lengths_sorted = sorted(lengths)
    mid = len(lengths_sorted) // 2
    median = (
        lengths_sorted[mid]
        if len(lengths_sorted) % 2 == 1
        else (lengths_sorted[mid - 1] + lengths_sorted[mid]) / 2
    )
    return {
        "n": len(lengths),
        "min": min(lengths),
        "max": max(lengths),
        "mean": round(sum(lengths) / len(lengths), 2),
        "median": median,
    }


def profile_split(split_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    columns = list(rows[0].keys()) if rows else []

    missing: dict[str, int] = {}
    for col in columns:
        missing[col] = sum(1 for row in rows if _is_empty(row.get(col)))

    ids = [str(row.get("id", "")) for row in rows]
    questions = [str(row.get("question", "")).strip() for row in rows]
    context_ids = [str(row.get("context_id", "")) for row in rows]
    file_names = [str(row.get("file_name", "")).strip() for row in rows]
    companies = [str(row.get("company_name", "")).strip() for row in rows]

    id_counts = Counter(ids)
    question_counts = Counter(questions)
    duplicate_ids = {k: v for k, v in id_counts.items() if k and v > 1}
    duplicate_questions = {k: v for k, v in question_counts.items() if k and v > 1}

    essential_ok = 0
    for row in rows:
        if (
            not _is_empty(row.get("id"))
            and not _is_empty(row.get("question"))
            and (not _is_empty(row.get("program_answer")) or not _is_empty(row.get("original_answer")))
            and not _is_empty(row.get("context_id"))
            and not _is_empty(row.get("file_name"))
            and not _is_empty(row.get("context"))
        ):
            essential_ok += 1

    # Sample a few rows for structure illustration (truncated).
    samples = []
    for row in rows[:2]:
        samples.append(
            {
                "id": row.get("id"),
                "context_id": row.get("context_id"),
                "file_name": row.get("file_name"),
                "company_name": row.get("company_name"),
                "report_year": row.get("report_year"),
                "page_number": row.get("page_number"),
                "question": (str(row.get("question", ""))[:240] + "…")
                if len(str(row.get("question", ""))) > 240
                else row.get("question"),
                "program_answer": row.get("program_answer"),
                "original_answer": row.get("original_answer"),
                "context_chars": len(str(row.get("context") or "")),
                "table_chars": len(str(row.get("table") or "")),
                "pre_text_chars": len(str(row.get("pre_text") or "")),
                "post_text_chars": len(str(row.get("post_text") or "")),
                "table_preview": (str(row.get("table") or "")[:200] + "…")
                if len(str(row.get("table") or "")) > 200
                else row.get("table"),
            }
        )

    year_values = [row.get("report_year") for row in rows if row.get("report_year") is not None]
    year_counter = Counter(str(y) for y in year_values)

    return {
        "split": split_name,
        "n_rows": n,
        "columns": columns,
        "missing_counts": missing,
        "missing_rates": {k: round(v / n, 4) if n else 0.0 for k, v in missing.items()},
        "unique_ids": len(set(ids)),
        "duplicate_id_groups": len(duplicate_ids),
        "duplicate_id_examples": list(duplicate_ids.items())[:5],
        "unique_questions": len(set(questions)),
        "duplicate_question_groups": len(duplicate_questions),
        "duplicate_question_extra_rows": sum(v - 1 for v in duplicate_questions.values()),
        "duplicate_question_examples": [
            {"question": q[:160], "count": c} for q, c in list(duplicate_questions.items())[:5]
        ],
        "unique_context_ids": len(set(context_ids)),
        "unique_file_names": len({f for f in file_names if f}),
        "unique_companies": len({c for c in companies if c}),
        "rows_with_essential_fields": essential_ok,
        "eligible_for_sampling_estimate": essential_ok,
        "question_length_chars": _text_stats(questions),
        "context_length_chars": _text_stats([str(row.get("context") or "") for row in rows]),
        "table_length_chars": _text_stats([str(row.get("table") or "") for row in rows]),
        "program_answer_equals_original_rate": round(
            sum(
                1
                for row in rows
                if str(row.get("program_answer", "")).strip()
                == str(row.get("original_answer", "")).strip()
            )
            / n,
            4,
        )
        if n
        else 0.0,
        "report_year_top": year_counter.most_common(10),
        "company_top": Counter(c for c in companies if c).most_common(10),
        "samples": samples,
    }


def check_pdf_availability(dataset_info: Any, file_names: set[str]) -> dict[str, Any]:
    """Inspect whether PDF paths are advertised; do not download the full PDF tree here."""
    result: dict[str, Any] = {
        "dataset_card_claims_pdfs": True,
        "pdfs_bundled_in_arrow_rows": False,
        "unique_file_names_observed": len(file_names),
        "example_file_names": sorted(file_names)[:10],
        "local_pdf_probe": {},
        "notes": [],
    }

    # Hugging Face datasets load for FinQA returns tabular fields only; PDFs are in the
    # repository data tree (clone) according to the dataset card — not as row blobs.
    result["notes"].append(
        "Official card: clone G4KMU/t2-ragbench to obtain PDFs under data/ organised by "
        "dataset/split. load_dataset() returns text/metadata columns, not PDF bytes."
    )

    # Optional local cache probe (HF datasets cache) — informational only.
    try:
        from huggingface_hub import hf_hub_url  # type: ignore

        _ = hf_hub_url
        result["notes"].append("huggingface_hub is available for later PDF fetch/clone.")
    except Exception:
        result["notes"].append("huggingface_hub not imported; PDF clone still required later.")

    return result


def build_profile(ds: Any) -> dict[str, Any]:
    splits = list(ds.keys())
    split_profiles = {}
    all_file_names: set[str] = set()
    all_ids: list[str] = []

    for split_name in splits:
        rows = [dict(row) for row in ds[split_name]]
        split_profiles[split_name] = profile_split(split_name, rows)
        all_file_names.update(
            str(row.get("file_name", "")).strip()
            for row in rows
            if str(row.get("file_name", "")).strip()
        )
        all_ids.extend(str(row.get("id", "")) for row in rows)

    # Cross-split ID collisions (should be rare).
    id_counts = Counter(all_ids)
    cross_dupes = {k: v for k, v in id_counts.items() if k and v > 1}

    test_n = split_profiles.get("test", {}).get("n_rows", 0)
    test_eligible = split_profiles.get("test", {}).get("eligible_for_sampling_estimate", 0)
    dev_n = split_profiles.get("dev", {}).get("n_rows", 0)

    rq_issues = []
    if test_eligible < 140:
        rq_issues.append(
            {
                "rq": "RQ1/RQ2/RQ3",
                "issue": f"Eligible test rows ({test_eligible}) < 140 after essential-field check.",
                "severity": "high",
            }
        )
    else:
        rq_issues.append(
            {
                "rq": "RQ1/RQ2/RQ3",
                "issue": f"Test pool size {test_n}, essential-eligible ≈ {test_eligible} — enough for a 140 sample.",
                "severity": "info",
            }
        )

    if split_profiles.get("test", {}).get("duplicate_question_groups", 0) > 0:
        rq_issues.append(
            {
                "rq": "RQ1 (paired tests)",
                "issue": "Duplicate question text exists in test; sampling must dedupe by question/id.",
                "severity": "medium",
            }
        )

    rq_issues.append(
        {
            "rq": "RQ2",
            "issue": (
                "No native hallucination/unsupported label. Must pre-register an evidence-grounded "
                "definition using retrieved evidence + verification (not wrong≠hallucination)."
            ),
            "severity": "medium",
        }
    )
    rq_issues.append(
        {
            "rq": "RQ3",
            "issue": (
                "No insufficient_evidence label. Gold context is oracle; every row has supporting C. "
                "Abstention/insufficient criteria must be pre-registered from retrieval/verify signals "
                "(and optional withheld-document probes), not a dataset field."
            ),
            "severity": "high",
        }
    )
    rq_issues.append(
        {
            "rq": "All",
            "issue": (
                "Feeding gold `context` to the generator as retrieval would invalidate RAG claims. "
                "KB must use source documents (file_name / PDFs), with gold context for evaluation only."
            ),
            "severity": "high",
        }
    )

    pdf_info = check_pdf_availability(None, all_file_names)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": HF_DATASET_ID,
        "subset": HF_SUBSET,
        "splits": {name: split_profiles[name]["n_rows"] for name in splits},
        "total_rows": sum(split_profiles[name]["n_rows"] for name in splits),
        "columns": EXPECTED_COLUMNS,
        "columns_match_expected": all(
            split_profiles[name]["columns"] == EXPECTED_COLUMNS for name in splits
        ),
        "split_profiles": split_profiles,
        "cross_split_duplicate_id_groups": len(cross_dupes),
        "unique_file_names_all_splits": len(all_file_names),
        "pdf_source_documents": pdf_info,
        "rq_implications": rq_issues,
        "sampling_readiness": {
            "recommended_test_pool": "test",
            "recommended_calibration_pool": "dev",
            "frozen_test_target": 140,
            "test_rows": test_n,
            "test_essential_eligible_estimate": test_eligible,
            "dev_rows": dev_n,
            "can_support_140_from_test": test_eligible >= 140,
            "phase2_selected_140": False,
        },
    }


def render_markdown(profile: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# FinQA (T²-RAGBench) dataset profile — Phase 2")
    lines.append("")
    lines.append(f"Generated (UTC): `{profile['generated_at_utc']}`")
    lines.append("")
    lines.append(f"- Dataset: `{profile['dataset_id']}` subset `{profile['subset']}`")
    lines.append(f"- Load: `load_dataset(\"{HF_DATASET_ID}\", \"{HF_SUBSET}\")`")
    lines.append(f"- Total rows: **{profile['total_rows']}**")
    lines.append(f"- Columns match expected schema: **{profile['columns_match_expected']}**")
    lines.append("")
    lines.append("## Splits and row counts")
    lines.append("")
    for split, n in profile["splits"].items():
        lines.append(f"- **{split}**: {n}")
    lines.append("")
    lines.append("## Columns")
    lines.append("")
    for col in profile["columns"]:
        lines.append(f"- `{col}`")
    lines.append("")

    for split_name, sp in profile["split_profiles"].items():
        lines.append(f"## Split `{split_name}`")
        lines.append("")
        lines.append(f"- Rows: **{sp['n_rows']}**")
        lines.append(f"- Unique `id`: {sp['unique_ids']} (duplicate id groups: {sp['duplicate_id_groups']})")
        lines.append(
            f"- Unique questions: {sp['unique_questions']} "
            f"(duplicate question groups: {sp['duplicate_question_groups']}; "
            f"extra rows: {sp['duplicate_question_extra_rows']})"
        )
        lines.append(f"- Unique `context_id`: {sp['unique_context_ids']}")
        lines.append(f"- Unique `file_name`: {sp['unique_file_names']}")
        lines.append(f"- Unique `company_name`: {sp['unique_companies']}")
        lines.append(
            f"- Essential-field rows (id, question, answer, context_id, file_name, context): "
            f"**{sp['rows_with_essential_fields']}**"
        )
        lines.append(
            f"- `program_answer` == `original_answer` rate: {sp['program_answer_equals_original_rate']}"
        )
        lines.append(
            f"- Question length (chars): mean={sp['question_length_chars'].get('mean')}, "
            f"median={sp['question_length_chars'].get('median')}"
        )
        lines.append(
            f"- Context length (chars): mean={sp['context_length_chars'].get('mean')}, "
            f"median={sp['context_length_chars'].get('median')}"
        )
        lines.append(
            f"- Table length (chars): mean={sp['table_length_chars'].get('mean')}, "
            f"median={sp['table_length_chars'].get('median')}"
        )
        lines.append("")
        lines.append("### Missing values")
        lines.append("")
        nonzero_missing = {k: v for k, v in sp["missing_counts"].items() if v > 0}
        if not nonzero_missing:
            lines.append("- None (all listed fields non-empty for every row).")
        else:
            for k, v in sorted(nonzero_missing.items(), key=lambda x: -x[1]):
                lines.append(f"- `{k}`: {v} ({sp['missing_rates'][k]:.2%})")
        lines.append("")
        if sp["duplicate_question_examples"]:
            lines.append("### Duplicate question examples")
            lines.append("")
            for ex in sp["duplicate_question_examples"]:
                lines.append(f"- count={ex['count']}: {ex['question']!r}")
            lines.append("")

    lines.append("## Question / answer / context structure")
    lines.append("")
    lines.append(
        "- **Question:** context-independent FinQA query string (`question`)."
    )
    lines.append(
        "- **Reference answers:** `program_answer` (numeric/program-normalised; primary for evaluation) "
        "and `original_answer` (source form)."
    )
    lines.append(
        "- **Oracle context:** `context` combines supporting text/table evidence for the item; "
        "also available as `pre_text`, `table`, `post_text`."
    )
    lines.append(
        "- **Provenance:** `context_id`, `file_name`, `page_number`, company/report metadata."
    )
    lines.append("")
    lines.append("## Source documents / PDFs")
    lines.append("")
    pdf = profile["pdf_source_documents"]
    lines.append(f"- Unique `file_name` values across splits: **{pdf['unique_file_names_observed']}**")
    lines.append(f"- PDFs as row blobs in `load_dataset`: **{pdf['pdfs_bundled_in_arrow_rows']}**")
    lines.append(f"- Dataset card claims PDFs available via repo clone: **{pdf['dataset_card_claims_pdfs']}**")
    for note in pdf["notes"]:
        lines.append(f"- Note: {note}")
    lines.append("- Example `file_name` values:")
    for name in pdf["example_file_names"]:
        lines.append(f"  - `{name}`")
    lines.append("")
    lines.append("## Sampling readiness (no 140 selected in Phase 2)")
    lines.append("")
    sr = profile["sampling_readiness"]
    for k, v in sr.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("## RQ implications")
    lines.append("")
    for item in profile["rq_implications"]:
        lines.append(f"- **{item['rq']}** [{item['severity']}]: {item['issue']}")
    lines.append("")
    lines.append("## Phase 2 boundary")
    lines.append("")
    lines.append("- Final 140 **not** selected.")
    lines.append("- Knowledge base **not** built.")
    lines.append("- RAG architectures **not** implemented.")
    lines.append("")
    return "\n".join(lines)


def save_profile(profile: dict[str, Any], processed_dir: Path, docs_dir: Path) -> dict[str, Path]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    json_path = processed_dir / "finqa_profile.json"
    md_path = docs_dir / "dataset_profile.md"
    json_path.write_text(json.dumps(profile, indent=2, default=str) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(profile), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def load_finqa():
    from datasets import load_dataset

    return load_dataset(HF_DATASET_ID, HF_SUBSET)
