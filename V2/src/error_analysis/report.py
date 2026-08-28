"""Write Phase 18 tables and narrative. Does not rewrite Phase 15/16/17 result files."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from src.error_analysis.constants import (
    ARCH_LABELS,
    ARCHITECTURES,
    JUDGE_METRIC_LABEL,
    LOCKED_T,
    PRIMARY_CATEGORIES,
    SAMPLE_SEED,
)


CASE_FIELDS = [
    "question_id",
    "architecture",
    "architecture_label",
    "case_key",
    "in_qualitative_sample",
    "sample_strata",
    "displayed_correct",
    "claim_correct",
    "decision",
    "confidence",
    "threshold",
    "llm_faithfulness",
    "token_overlap",
    "context_precision",
    "context_recall",
    "context_recall_numeric",
    "verification_status",
    "verification_score",
    "n_evidence",
    "gold_program_answer",
    "gold_file_name",
    "retrieved_files",
    "primary_category",
    "error_layer",
    "tags",
    "explanation",
    "question_excerpt",
    "displayed_answer_excerpt",
    "draft_excerpt",
]


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def summarise(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for arch in ARCHITECTURES:
        subset = [r for r in rows if r["architecture"] == arch]
        n = len(subset)
        counts = Counter(r["primary_category"] for r in subset)
        for cat in PRIMARY_CATEGORIES:
            k = counts.get(cat, 0)
            out.append({
                "architecture": arch,
                "architecture_label": ARCH_LABELS[arch],
                "primary_category": cat,
                "n": k,
                "n_architecture": n,
                "pct_of_architecture": round(100.0 * k / n, 2) if n else 0.0,
                "scope": "full_420_rule_based",
            })
    return out


def write_markdown(
    path: Path,
    *,
    n_sample: int,
    n_sample_questions: int,
    sample_method: str,
    summary_rows: list[dict[str, Any]],
    sample_rows: list[dict[str, Any]],
    hashes: dict[str, str],
) -> None:
    by_arch = {arch: [r for r in summary_rows if r["architecture"] == arch] for arch in ARCHITECTURES}

    def _tbl(arch: str) -> list[str]:
        lines = ["| Category | n | % of 140 |", "| --- | ---: | ---: |"]
        for row in by_arch[arch]:
            lines.append(
                f"| {row['primary_category']} | {row['n']} | {row['pct_of_architecture']:.2f} |"
            )
        return lines

    examples = []
    wanted = [
        "incorrect_abstention",
        "appropriate_abstention",
        "retrieval_failure",
        "incorrect_numerical_reasoning",
        "unsupported_claim",
        "non_numeric_answer",
        "correct_answer",
        "incorrect_despite_partial_evidence",
    ]
    seen = set()
    for cat in wanted:
        for row in sample_rows:
            key = (cat, row["architecture"])
            if row["primary_category"] == cat and key not in seen:
                seen.add(key)
                examples.append(row)
                break

    lines = [
        "# Phase 18 — Qualitative error analysis",
        "",
        "CPU analysis of frozen Phase 15/16/17 artefacts. **No RAG rerun. No Qwen generation. No LLM-as-judge calls. No change to T=0.65 or the frozen 140/40.**",
        "",
        f"**Judge metric:** `{JUDGE_METRIC_LABEL}` — **not official RAGAS.**",
        "",
        f"**Locked T:** {LOCKED_T} (DEV 40 only).",
        "",
        "## Sampling",
        "",
        f"- Method: {sample_method}",
        f"- Seed: {SAMPLE_SEED}",
        f"- Qualitative sample: **{n_sample} cases** on **{n_sample_questions} questions**.",
        "- Rule-based taxonomy is applied to **all 420 cases**; percentages below use the full frozen set.",
        "- The sample is for narrative inspection, not a second test set.",
        "",
        "## Taxonomy (primary, mutually exclusive)",
        "",
        "| Category | Meaning (recorded-field rule) | Layer |",
        "| --- | --- | --- |",
        "| `correct_answer` | Displayed numeric match to FinQA `program_answer`. | numeric_correct |",
        "| `appropriate_abstention` | UQ ABSTAIN and draft/claim is numerically incorrect. | abstention |",
        "| `incorrect_abstention` | UQ ABSTAIN and draft/claim is numerically correct (false abstention). | abstention |",
        "| `retrieval_failure` | Displayed incorrect and `context_recall=0` (gold file/context_id not in top-k). | retrieval |",
        "| `non_numeric_answer` | ANSWER with no parseable number in the displayed text. | answer_format |",
        "| `incorrect_numerical_reasoning` | Gold number is in evidence text but displayed number does not match. | numeric_error |",
        "| `unsupported_claim` | ANSWER incorrect, gold number not in evidence, LLM-as-judge faithfulness < 0.5. | unsupported_emission |",
        "| `incorrect_despite_partial_evidence` | Residual ANSWER error with gold file retrieved but gold number not in chunk text. | numeric_error |",
        "",
        "Numeric incorrectness is **not** called hallucination. `unsupported_emitted` remains answered-and-numerically-wrong, not a labelled hallucination corpus.",
        "",
        "The 0.5 faithfulness cut is a **taxonomy split** only. It is not a new operating threshold and was not tuned on the frozen 140.",
        "",
        "## Full-set category counts (n=140 per architecture)",
        "",
        "| Category | Single-Agent | Multi-Agent | Multi-Agent + UQ |",
        "| --- | ---: | ---: | ---: |",
    ]
    sa_map = {r["primary_category"]: r["n"] for r in by_arch["single_agent"]}
    ma_map = {r["primary_category"]: r["n"] for r in by_arch["multi_agent"]}
    uq_map = {r["primary_category"]: r["n"] for r in by_arch["multi_agent_uq"]}
    for cat in PRIMARY_CATEGORIES:
        lines.append(f"| `{cat}` | {sa_map.get(cat, 0)} | {ma_map.get(cat, 0)} | {uq_map.get(cat, 0)} |")
    lines.append("")
    lines.append("### Single-Agent")
    lines.extend(_tbl("single_agent"))
    lines.append("")
    lines.append("### Multi-Agent")
    lines.extend(_tbl("multi_agent"))
    lines.append("")
    lines.append("### Multi-Agent + UQ")
    lines.extend(_tbl("multi_agent_uq"))
    lines.extend([
        "",
        "## Architecture comparison",
        "",
        "Retrieval (`context_precision` / `context_recall`) is identical across architectures by design (shared index). A retrieval miss is therefore a **question-level** failure, not an architecture effect.",
        "",
        "Multi-Agent verification is informational: it does not rewrite the draft. VERIFIED + numerically wrong cases are verification false positives, not proof of a Multi-Agent accuracy gain.",
        "",
        "## Interpretation",
        "",
        "### RQ1",
        "",
        "Displayed correctness is 32/140 (Single-Agent) vs 29/140 (Multi-Agent); McNemar was not significant in Phase 17. Shared retrieval and a large both-incorrect cell (98/140) dominate. Multi-Agent verification often agrees with a wrong number (verification false positives). The qualitative sample of discordant pairs should be read as case illustrations, not as a new significance test.",
        "",
        "### RQ2",
        "",
        f"UQ confidence tracks `{JUDGE_METRIC_LABEL}` in Phase 17 (Spearman ρ=0.6988). Abstentions are mostly drafts with weak recorded support. UQ **ANSWER** errors still often have high judge faithfulness: abstention filters low-support cases; it does not reliably fix numerical reasoning. This is not official RAGAS and is not a labelled hallucination study.",
        "",
        "### RQ3",
        "",
        "At locked T=0.65, UQ answers 78/140 and abstains 62/140, including **2 false abstentions** (correct drafts withheld). Appropriate abstention is the main UQ behaviour among abstains. Selective accuracy rises because low-confidence errors are withheld, at the cost of coverage. T was not retuned on the frozen 140.",
        "",
        "## Representative sampled cases",
        "",
    ])
    for row in examples:
        lines.extend([
            f"### {row['case_key']} — `{row['primary_category']}`",
            "",
            row["explanation"],
            "",
        ])
    lines.extend([
        "## Limitations",
        "",
        "- Categories use recorded metrics (numeric match, gold file/`context_id` overlap, judge score). They cannot see unpublished gold table cells that were not chunked.",
        "- LLM-as-judge is same-model Qwen3-8B, custom/RAGAS-inspired, **not official RAGAS**.",
        "- Sample percentages must not be treated as population rates; use the full-420 tables for that.",
        "- Qualitative text excerpts are truncated.",
        "",
        "## Source hashes (verified, unchanged)",
        "",
    ])
    for key, digest in hashes.items():
        lines.append(f"- {key}: `{digest}`")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
