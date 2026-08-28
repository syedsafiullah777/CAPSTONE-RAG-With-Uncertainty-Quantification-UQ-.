# Phase 19 — Final reproducibility and research-integrity audit

| Field | Value |
| --- | --- |
| Phase | 19 |
| Phase name | Final reproducibility and research-integrity audit |
| Evidence file | `project_record/evidence/phase19_reproducibility_audit.md` |
| Last updated | 2026-08-28 17:58 UTC |
| Overall scientific chain | **PASS** |
| Checks PASS / FAIL / NEEDS VERIFICATION | 17 / 0 / 4 |
| RAG / Qwen / judge / stats rerun | **false** / **false** / **false** / **false** |

This audit is read-only on frozen research artefacts. It does **not** rerun RAG, Qwen3-8B generation, LLM-as-judge, benchmark, calibration, or statistical tests. It does **not** modify the frozen 140, DEV 40, T=0.65, Phase 15–18 result files, RAG architectures, or V1.

## Research chain audited

40 DEV calibration → locked T=0.65 → frozen 140 test set → 420 benchmark cases → Phase 16 CPU metrics → 420 LLM-judge faithfulness results → Phase 17 statistics → Phase 18 error analysis.

## Summary

| # | Check | Status | Detail |
| --- | --- | --- | --- |
| 1 | `frozen_artefact_sha256` | **PASS** | Phase 15/16/140/40/lock SHA-256 match src/statistics/constants.py: phase15=f5256ae40fa8…, processed=e9e4f80dafff…, judge=093c4699b68e…, frozen140=88899ae9c66f…, cal40=1325b595ae1f…, lock=8981233604e6… |
| 2 | `locked_threshold` | **PASS** | T=0.65 locked=True source_split=dev used_frozen_test_140=False n=40 rule=max_selective_accuracy_coverage_ge_0.50 coverage=0.55 selective=0.5454545454545454 |
| 3 | `frozen_140_and_dev_40` | **PASS** | n_test=140 unique_test=140 n_dev=40 overlap_test_dev=0 lock_ids_match_cal40=True |
| 4 | `benchmark_420_completeness` | **PASS** | phase15=420 unique=420 per_arch={'single_agent': 140, 'multi_agent': 140, 'multi_agent_uq': 140} ids_match_freeze=True processed_keys_match=True judge_keys_match=True uq_threshold_all_0.65=True uq_decisions={'ABSTAIN': 62, 'ANSWER': 78} judge_used_rag_rerun=False judge_noncomp… |
| 5 | `phase16_phase17_count_traceability` | **PASS** | Displayed correct SA/MA/UQ = 32/29/32; UQ ANSWER/ABSTAIN = 78/62; UQ claim correct = 34. Phase 16 summary CSV matches Phase 17 descriptive CSV on these counts. |
| 6 | `phase17_statistics_traceability` | **PASS** | McNemar SA vs MA p=0.6776 cells=19/13/10/98 Holm=0.6776 sig=false; Spearman rho=0.6988 layer=LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired) |
| 7 | `figure_to_table_consistency` | **PASS** | FIGURE_INDEX counts match Phase 17 descriptive/tests CSVs (SA/MA/UQ displayed 32/29/32; McNemar 19/13/10/98; Spearman 0.6988; coverage 78/140; selective 32/78; UQ outcomes 32/46/60/2; judge means 0.3241/0.3484/0.3749). |
| 8 | `phase17_json_rq3_abstention_outcomes_key` | **PASS** | phase17_statistics_summary.json `rq3_abstention_outcomes` is present and matches FIGURE_INDEX / Phase 18: ANSWER correct 32, ANSWER incorrect 46, ABSTAIN incorrect draft 60, ABSTAIN correct draft 2, T=0.65. |
| 9 | `no_accidental_phase17_result_changes` | **PASS** | Phase 17 table/JSON SHA-256 still match phase17_figure_render.json pins. |
| 10 | `judge_fingerprint_vs_jsonl_settings` | **NEEDS VERIFICATION** | Judge JSONL is the source of truth for judge-call settings (observed temperature=0.0, max_new_tokens=32, n_ctx=4096, all_match=True). phase16_judge_runtime_fingerprint.json model_config has temperature=0.1 max_new_tokens=512 (RAG generation defaults). Documented in Phase 16 ju… |
| 11 | `manifest_id_sets_vs_csv` | **PASS** | sampling_manifest.selected_ids_sha256=1a69d93e412097a076e8ec836253b8fff53366aefc5ea5f8998020984f6bbd8a (JSON array fingerprint); lock.question_ids_sha256=da2126411f3025570293725bc93e5bd8d118dfbc2c706ec53c51eddcf38c4853 (newline-joined ids_sha256); calibration_manifest.selected… |
| 12 | `phase17_figures_canonical_set` | **PASS** | files=['FIGURE_INDEX.md', 'rq1_answer_correctness_95ci.pdf', 'rq1_answer_correctness_95ci.png', 'rq1_mcnemar_counts.pdf', 'rq1_mcnemar_counts.png', 'rq2_confidence_vs_faithfulness.pdf', 'rq2_confidence_vs_faithfulness.png', 'rq2_faithfulness_distribution.pdf', 'rq2_faithfulnes… |
| 13 | `phase18_error_analysis_consistency` | **PASS** | n_cases=420 sample=81 UQ false_abstain=2 UQ true_abstain=60 unsupported_claim SA/MA/UQ=55/52/10 |
| 14 | `experiment_yaml_threshold_fields` | **NEEDS VERIFICATION** | Official T is threshold.lock.json; yaml confidence_threshold is null by design (Phase 12 isolation). dataset.phase5_threshold_locked remains false as a leftover Phase 5 freeze flag — stale relative to Phase 13 lock; not treated as the scientific source of T. |
| 15 | `metric_definitions` | **PASS** | Primary RQ2 label is `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — not official RAGAS. RQ1 = displayed numeric FinQA match. RQ3 = coverage/selective accuracy/unsupported_emitted at locked T. unsupported_emitted = ANSWER and displayed numeric incorrect (not a … |
| 16 | `git_does_not_track_raw_jsonl_dumps` | **PASS** | tracked jsonl count=1; forbidden_raw=[]; forbidden_judge=[]; tracked=['V2/results/processed/phase16_cases.jsonl'] |
| 17 | `google_drive_archive` | **NEEDS VERIFICATION** | No Google Drive MSc-RAG folder was listed from this Mac. Searched CloudStorage/GoogleDrive, ~/Google Drive, ~/My Drive. hits=none. Do not claim a Drive backup exists. |
| 18 | `github_status` | **NEEDS VERIFICATION** | branch=cursor/empty-v2-workspace. Remote: origin	https://github.com/syedsafiullah777/CAPSTONE--RAG-WITH-UNCERTAINITY-QUANTIFICATION-.git (fetch) origin	https://github.com/syedsafiullah777/CAPSTONE--RAG-WITH-UNCERTAINITY-QUANTIFICATION-.git (push) Working tree (short, may inclu… |
| 19 | `required_local_artefacts` | **PASS** | All required local chain files are present. |
| 20 | `documentation_chronology_pre_audit_write` | **PASS** | Historical Phase 15–18 remaining-issues lines that say a later phase was not started are dated history and were not rewritten. Current headers before this audit: headers already mention Phase 19 complete. |
| 21 | `v1_unmodified_in_this_audit` | **PASS** | Phase 19 audit writes only under V2/. V1 is reference-only. Non-V2 status lines=none |

## FAIL items (not repaired)

- none

## NEEDS VERIFICATION (not repaired)

- `judge_fingerprint_vs_jsonl_settings`: Judge JSONL is the source of truth for judge-call settings (observed temperature=0.0, max_new_tokens=32, n_ctx=4096, all_match=True). phase16_judge_runtime_fingerprint.json model_config has temperature=0.1 max_new_tokens=512 (RAG generation defaults). Documented in Phase 16 judge notes; not treated as a result rewrite.
- `experiment_yaml_threshold_fields`: Official T is threshold.lock.json; yaml confidence_threshold is null by design (Phase 12 isolation). dataset.phase5_threshold_locked remains false as a leftover Phase 5 freeze flag — stale relative to Phase 13 lock; not treated as the scientific source of T.
- `google_drive_archive`: No Google Drive MSc-RAG folder was listed from this Mac. Searched CloudStorage/GoogleDrive, ~/Google Drive, ~/My Drive. hits=none. Do not claim a Drive backup exists.
- `github_status`: branch=cursor/empty-v2-workspace. Remote:
origin	https://github.com/syedsafiullah777/CAPSTONE--RAG-WITH-UNCERTAINITY-QUANTIFICATION-.git (fetch)
origin	https://github.com/syedsafiullah777/CAPSTONE--RAG-WITH-UNCERTAINITY-QUANTIFICATION-.git (push)
Working tree (short, may include uncommitted V2 work):
M V2/.gitignore
 M V2/DECISIONS.md
 M V2/PROJECT_CONTEXT.md
 M V2/docs/IMPLEMENTATION_PLAN.md
 M V

Do not treat a NEEDS VERIFICATION item as a PASS. Do not rewrite Phase 15–18 result files to make a citation key appear.

## Frozen artefact hashes

| Artefact | Path | Expected SHA-256 | Observed |
| --- | --- | --- | --- |
| Phase 15 raw JSONL | `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` | `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` | `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` |
| Phase 16 processed | `results/processed/phase16_cases.jsonl` | `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91` | `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91` |
| Phase 16 judge JSONL | `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl` | `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3` | `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3` |
| Frozen 140 | `data/final/selected_140_questions.csv` | `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087` | `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087` |
| Calibration 40 | `data/calibration/calibration_questions.csv` | `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845` | `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845` |
| Threshold lock | `results/config/threshold.lock.json` | `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88` | `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88` |

## Metric definitions (locked wording)

- **RQ1:** displayed numeric FinQA correctness (rel_tol=0.01). Primary confirmatory test: McNemar, Single-Agent vs Multi-Agent, n=140 paired.
- **RQ2:** `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS**.
- **RQ3:** coverage, selective accuracy, `unsupported_emitted` at locked T=0.65. `unsupported_emitted` = ANSWER and displayed numeric incorrect. This is **not** a hallucination label.
- Judge-call settings source of truth: official judge JSONL (`temperature=0.0`, `max_new_tokens=32`, `n_ctx=4096`). Do not use `phase16_judge_runtime_fingerprint.json` `model_config` (`0.1` / `512`) as judge-call settings.

## What this audit did not do

- Did not rerun RAG, Qwen3-8B, the judge, calibration, or statistical tests.
- Did not retune T or the frozen 140/40.
- Did not start Phase 20 (dissertation evidence pack).

## Master record reference

Add to `PROJECT_MASTER_RECORD.md` phase section:

> Validation evidence: `project_record/evidence/phase19_reproducibility_audit.md`
> Artefact manifest: `results/final/phase19_artefact_manifest.md`
