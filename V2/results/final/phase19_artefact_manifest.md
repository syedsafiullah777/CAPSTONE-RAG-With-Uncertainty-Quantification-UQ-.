# Final research artefact manifest (Phase 19)

Concise index of the frozen research chain. Paths are relative to `V2/`. Hashes below are the Phase 17/18 pin values; Phase 19 re-verified them and did not rewrite the files.

Last updated: 2026-08-28 17:58 UTC
Locked threshold: **T = 0.65** (FinQA DEV 40 only; `used_frozen_test_140=false`)
Judge metric: `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — not official RAGAS

## Datasets

| Artefact | Path | Notes |
| --- | --- | --- |
| Frozen 140 FinQA **test** | `data/final/selected_140_questions.csv` | seed 42; SHA-256 `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087` |
| Sampling manifest | `data/final/sampling_manifest.json` | `selected_ids_sha256` uses JSON-array fingerprint |
| Calibration 40 FinQA **dev** | `data/calibration/calibration_questions.csv` | seed 42; SHA-256 `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845` |
| Calibration manifest | `data/calibration/calibration_manifest.json` | set freeze; `threshold_locked: false` is Phase 5 leftover — official T is the lock file |

## Threshold

| Artefact | Path | Notes |
| --- | --- | --- |
| Official lock | `results/config/threshold.lock.json` | T=0.65; n=40; coverage 0.55; selective 12/22; SHA-256 `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88` |
| YAML `confidence_threshold` | `config/experiment.yaml` | **null** by design (Phase 12 isolation). Smoke fallback 0.55 is **not** T. |

## Raw results

| Artefact | Path | Notes |
| --- | --- | --- |
| Phase 15 420-case JSONL | `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` | SHA-256 `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa`; **gitignored** (do not commit) |
| Phase 16 processed cases | `results/processed/phase16_cases.jsonl` | SHA-256 `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91`; allowlisted for git |
| Phase 16 judge JSONL | `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl` | SHA-256 `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3`; **gitignored** (do not commit) |
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
