"""Write Phase 19 audit evidence and the research artefact manifest. Read-only on results."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.statistics.constants import (
    CAL_40_REL,
    EXPECTED_CAL40_SHA256,
    EXPECTED_FROZEN140_SHA256,
    EXPECTED_JUDGE_SHA256,
    EXPECTED_LOCK_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
    FROZEN_140_REL,
    JUDGE_METRIC_LABEL,
    JUDGE_REL,
    LOCKED_T,
    LOCK_REL,
    PHASE15_REL,
    PROCESSED_REL,
)


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _rows(checks: list[dict[str, str]]) -> str:
    lines = ["| # | Check | Status | Detail |", "| --- | --- | --- | --- |"]
    for i, item in enumerate(checks, start=1):
        detail = item["detail"].replace("\n", " ").replace("|", "\\|")
        if len(detail) > 280:
            detail = detail[:277] + "…"
        lines.append(f"| {i} | `{item['name']}` | **{item['status']}** | {detail} |")
    return "\n".join(lines)


def write_audit_documents(result: dict[str, Any], root: Path) -> dict[str, str]:
    evidence = root / "project_record/evidence/phase19_reproducibility_audit.md"
    manifest = root / "results/final/phase19_artefact_manifest.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    hashes = result.get("hashes") or {}
    expected = result.get("expected_hashes") or {}
    hash_table = [
        "| Artefact | Path | Expected SHA-256 | Observed |",
        "| --- | --- | --- | --- |",
        f"| Phase 15 raw JSONL | `{PHASE15_REL}` | `{EXPECTED_PHASE15_SHA256}` | `{hashes.get('phase15', expected.get('phase15', ''))}` |",
        f"| Phase 16 processed | `{PROCESSED_REL}` | `{EXPECTED_PROCESSED_SHA256}` | `{hashes.get('processed', expected.get('processed', ''))}` |",
        f"| Phase 16 judge JSONL | `{JUDGE_REL}` | `{EXPECTED_JUDGE_SHA256}` | `{hashes.get('judge', expected.get('judge', ''))}` |",
        f"| Frozen 140 | `{FROZEN_140_REL}` | `{EXPECTED_FROZEN140_SHA256}` | `{hashes.get('frozen140', expected.get('frozen140', ''))}` |",
        f"| Calibration 40 | `{CAL_40_REL}` | `{EXPECTED_CAL40_SHA256}` | `{hashes.get('cal40', expected.get('cal40', ''))}` |",
        f"| Threshold lock | `{LOCK_REL}` | `{EXPECTED_LOCK_SHA256}` | `{hashes.get('lock', expected.get('lock', ''))}` |",
    ]

    nv_items = [c for c in result["checks"] if c["status"] == "NEEDS VERIFICATION"]
    fail_items = [c for c in result["checks"] if c["status"] == "FAIL"]
    nv_list = "\n".join(f"- `{c['name']}`: {c['detail'][:400]}" for c in nv_items) or "- none"
    fail_list = "\n".join(f"- `{c['name']}`: {c['detail'][:400]}" for c in fail_items) or "- none"

    evidence.write_text(
        f"""# Phase 19 — Final reproducibility and research-integrity audit

| Field | Value |
| --- | --- |
| Phase | 19 |
| Phase name | Final reproducibility and research-integrity audit |
| Evidence file | `project_record/evidence/phase19_reproducibility_audit.md` |
| Last updated | {_utc()} |
| Overall scientific chain | **{result['overall']}** |
| Checks PASS / FAIL / NEEDS VERIFICATION | {result['n_pass']} / {result['n_fail']} / {result['n_needs_verification']} |
| RAG / Qwen / judge / stats rerun | **false** / **false** / **false** / **false** |

This audit is read-only on frozen research artefacts. It does **not** rerun RAG, Qwen3-8B generation, LLM-as-judge, benchmark, calibration, or statistical tests. It does **not** modify the frozen 140, DEV 40, T={LOCKED_T}, Phase 15–18 result files, RAG architectures, or V1.

## Research chain audited

40 DEV calibration → locked T={LOCKED_T} → frozen 140 test set → 420 benchmark cases → Phase 16 CPU metrics → 420 LLM-judge faithfulness results → Phase 17 statistics → Phase 18 error analysis.

## Summary

{_rows(result['checks'])}

## FAIL items (not repaired)

{fail_list}

## NEEDS VERIFICATION (not repaired)

{nv_list}

Do not treat a NEEDS VERIFICATION item as a PASS. Do not rewrite Phase 15–18 result files to make a citation key appear.

## Frozen artefact hashes

{chr(10).join(hash_table)}

## Metric definitions (locked wording)

- **RQ1:** displayed numeric FinQA correctness (rel_tol=0.01). Primary confirmatory test: McNemar, Single-Agent vs Multi-Agent, n=140 paired.
- **RQ2:** `{JUDGE_METRIC_LABEL}` — **not official RAGAS**.
- **RQ3:** coverage, selective accuracy, `unsupported_emitted` at locked T={LOCKED_T}. `unsupported_emitted` = ANSWER and displayed numeric incorrect. This is **not** a hallucination label.
- Judge-call settings source of truth: official judge JSONL (`temperature=0.0`, `max_new_tokens=32`, `n_ctx=4096`). Do not use `phase16_judge_runtime_fingerprint.json` `model_config` (`0.1` / `512`) as judge-call settings.

## What this audit did not do

- Did not rerun RAG, Qwen3-8B, the judge, calibration, or statistical tests.
- Did not retune T or the frozen 140/40.
- Did not start Phase 20 (dissertation evidence pack).

## Master record reference

Add to `PROJECT_MASTER_RECORD.md` phase section:

> Validation evidence: `project_record/evidence/phase19_reproducibility_audit.md`
> Artefact manifest: `results/final/phase19_artefact_manifest.md`
""",
        encoding="utf-8",
    )

    manifest.write_text(
        f"""# Final research artefact manifest (Phase 19)

Concise index of the frozen research chain. Paths are relative to `V2/`. Hashes below are the Phase 17/18 pin values; Phase 19 re-verified them and did not rewrite the files.

Last updated: {_utc()}
Locked threshold: **T = {LOCKED_T}** (FinQA DEV 40 only; `used_frozen_test_140=false`)
Judge metric: `{JUDGE_METRIC_LABEL}` — not official RAGAS

## Datasets

| Artefact | Path | Notes |
| --- | --- | --- |
| Frozen 140 FinQA **test** | `{FROZEN_140_REL}` | seed 42; SHA-256 `{EXPECTED_FROZEN140_SHA256}` |
| Sampling manifest | `data/final/sampling_manifest.json` | `selected_ids_sha256` uses JSON-array fingerprint |
| Calibration 40 FinQA **dev** | `{CAL_40_REL}` | seed 42; SHA-256 `{EXPECTED_CAL40_SHA256}` |
| Calibration manifest | `data/calibration/calibration_manifest.json` | set freeze; `threshold_locked: false` is Phase 5 leftover — official T is the lock file |

## Threshold

| Artefact | Path | Notes |
| --- | --- | --- |
| Official lock | `{LOCK_REL}` | T={LOCKED_T}; n=40; coverage 0.55; selective 12/22; SHA-256 `{EXPECTED_LOCK_SHA256}` |
| YAML `confidence_threshold` | `config/experiment.yaml` | **null** by design (Phase 12 isolation). Smoke fallback 0.55 is **not** T. |

## Raw results

| Artefact | Path | Notes |
| --- | --- | --- |
| Phase 15 420-case JSONL | `{PHASE15_REL}` | SHA-256 `{EXPECTED_PHASE15_SHA256}`; **gitignored** (do not commit) |
| Phase 16 processed cases | `{PROCESSED_REL}` | SHA-256 `{EXPECTED_PROCESSED_SHA256}`; allowlisted for git |
| Phase 16 judge JSONL | `{JUDGE_REL}` | SHA-256 `{EXPECTED_JUDGE_SHA256}`; **gitignored** (do not commit) |
| Judge fingerprint | `results/config/phase16_judge_runtime_fingerprint.json` | GPU/runtime only; not judge-call settings |

## Metrics

| Artefact | Path | Notes |
| --- | --- | --- |
| Phase 16 CPU summary | `results/metrics/phase16_summary.csv` | displayed SA/MA/UQ 32/29/32; UQ 78/62 |
| Phase 16 judge summary | `results/metrics/phase16_judge_summary.csv` | means 0.3241 / 0.3484 / 0.3749; UQ ANSWER-only 0.6548 |

## Statistics

| Artefact | Path | Notes |
| --- | --- | --- |
| Descriptive | `results/metrics/phase17_descriptive.csv` | Wilson CIs; do not recompute tests |
| Tests | `results/metrics/phase17_tests.csv` | RQ1 McNemar p=0.6776 (n.s.); Spearman ρ=0.6988 |
| Effect sizes | `results/metrics/phase17_effect_sizes.csv` | |
| Assumptions | `results/metrics/phase17_assumptions.csv` | |
| Summary JSON | `results/config/phase17_statistics_summary.json` | includes `rq3_abstention_outcomes` 32/46/60/2 |
| Interpretation | `results/final/phase17_interpretation.md` | same text as `phase17_summary.md` |

## Figures

| Artefact | Path | Notes |
| --- | --- | --- |
| Canonical directory | `results/metrics/phase17_figures/` | 6 stems × PNG+PDF + `FIGURE_INDEX.md`; no SVG |
| Main body | `rq1_answer_correctness_95ci`, `rq2_confidence_vs_faithfulness`, `rq3_coverage_vs_selective_accuracy` | |
| Appendix | `rq1_mcnemar_counts`, `rq2_faithfulness_distribution`, `rq3_uq_outcomes` | outcome counts 32/46/60/2 |

## Error analysis

| Artefact | Path | Notes |
| --- | --- | --- |
| Case table | `results/analysis/phase18_error_cases.csv` | 420 rows; sample seed 18 (81 cases / 42 questions) |
| Category summary | `results/analysis/phase18_error_summary.csv` | full-420 mutually exclusive taxonomy |
| Narrative | `results/final/phase18_error_analysis.md` | |

## Documentation

| Artefact | Path |
| --- | --- |
| Master record | `project_record/PROJECT_MASTER_RECORD.md` |
| Implementation plan | `docs/IMPLEMENTATION_PLAN.md` |
| This audit | `project_record/evidence/phase19_reproducibility_audit.md` |
| Phase 16 eval / judge | `docs/phase16_evaluation.md`, `docs/phase16_judge.md` |
| Phase 17 stats / figures | `docs/phase17_statistics.md`, `docs/phase17_figures.md` |
| Phase 18 | `docs/phase18_error_analysis.md` |
| Storage spec | `docs/storage_backup_recovery.md` |

## Git / backup (audit-time)

- Do **not** `git add` Phase 15 `cases.jsonl` or Phase 16 `judge.jsonl`.
- Google Drive `MSc-RAG` archive: **NEEDS VERIFICATION** from this Mac.
- GitHub: source remote exists; commit of Phase 15–19 code/docs is a user action, not claimed complete here.

Phase 20 (dissertation evidence pack) is **not started**.
""",
        encoding="utf-8",
    )

    return {
        "evidence": str(evidence.relative_to(root)),
        "manifest": str(manifest.relative_to(root)),
    }
