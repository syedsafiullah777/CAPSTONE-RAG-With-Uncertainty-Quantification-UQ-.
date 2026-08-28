# Phase 17 validation evidence

| Field | Value |
| --- | --- |
| Phase | 17 — Statistics + final tables |
| Evidence file | `project_record/evidence/phase17_validation.md` |
| Last updated | 2026-08-28 |
| Phase 17 status | **PASS** on frozen Phase 15/16 artefacts. Figure refresh **PASS** (presentation only). No RAG/Qwen/judge rerun. No statistical tests recomputed. Phase 18 not started. |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 17 unit tests | **PASS** | `tests/test_phase17_statistics.py` (6 passed excluding `analyse()`; `test_analyse_paired_140` not re-run) |
| 2 | Full pytest suite | **PASS** | 130 passed, 1 deselected (`test_analyse_paired_140` not re-run to avoid recomputing statistics) |
| 3 | Official paired analysis n=140 | **PASS** | `results/config/phase17_smoke_test.json` (existing; not re-run) |
| 4 | Frozen SHA gates | **PASS** | Phase 15/16/140/40/lock hashes unchanged after figure render |
| 5 | Dissertation figure refresh | **PASS** | `results/config/phase17_figure_render.json`; `docs/phase17_figures.md` |
| 6 | Phase 18 dissertation pack | **not started** | — |

Locked T=0.65 unchanged. Frozen 140/40 unchanged. Phase 15 JSONL and Phase 16 judge JSONL not rewritten. V1 unmodified.

---

## Test records

### 1. Unit tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 17 |
| Test name | `test_phase17_statistics` |
| Command | `PYTHONPATH=. pytest tests/test_phase17_statistics.py -q` |
| Environment | Local Mac; `V2/.venv`; CPU |
| Expected | McNemar/Wilson/Holm helpers; stats modules do not import RAG/LLM; frozen SHAs stable; analyse() n=140 and does not rewrite JSONL |
| Actual (observed) | **6 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase17_statistics.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 17 |
| Test name | full suite |
| Command | `PYTHONPATH=. pytest -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | Existing phases still pass after statistics code is added |
| Actual (observed) | **130 passed** |
| Status | **PASS** |
| Error | — |
| Output path | — |

### 3. Official paired analysis

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 17 |
| Test name | `phase17_statistics` |
| Command | `PYTHONPATH=. python scripts/run_statistics.py` |
| Environment | Local Mac CPU; `used_llm_inference=false`; `used_gpu=false`; `used_rag_rerun=false` |
| Expected | Paired tests on frozen 140 questions; T=0.65 unchanged; Phase 15 SHA unchanged |
| Actual (observed) | `status=PASS n_questions=140 n_tests=18`; confirmatory RQ1 McNemar p=0.6776 (not significant) |
| Status | **PASS** |
| Error | — |
| Output path | `results/config/phase17_statistics_summary.json`; `results/metrics/phase17_tests.csv` |

Source hashes (verified, unchanged):

- Phase 15: `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa`
- Phase 16 processed: `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91`
- Judge JSONL: `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3`
- Frozen 140: `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087`
- Calibration 40: `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845`
- Lock T=0.65: `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88`

### 4. Observed confirmatory results (not official RAGAS)

**RQ1 (McNemar exact, displayed numeric correctness, n=140 paired):** SA 32/140 vs MA 29/140; discordant 23 (13 SA-only, 10 MA-only); p=0.6776; Holm p=0.6776; Cohen's g=−0.0652. **Not significant.** Does not support a Multi-Agent accuracy gain.

**RQ2 (Holm family of 3; metric = LLM-as-judge faithfulness, Qwen3-8B, custom/RAGAS-inspired):**

- Spearman UQ confidence vs faithfulness: ρ=0.6988, df=138, p=8.011×10⁻²², Holm p=2.403×10⁻²¹ (**significant**)
- Mann–Whitney ANSWER vs ABSTAIN faithfulness: U=4033, means 0.6548 vs 0.0229, p=8.833×10⁻¹⁵, Holm p=1.767×10⁻¹⁴ (**significant**)
- Wilcoxon MA vs UQ faithfulness (all 140): W=154.5, p=0.4032, Holm p=0.4032 (**not significant**)

**RQ3 (T=0.65):** coverage 78/140=0.5571 (Wilson 0.4744–0.6368); selective accuracy 32/78=0.4103 (Wilson 0.3078–0.5211); true abstain 60 / false abstain (correct draft) 2. Unsupported-emitted McNemar vs SA Holm p=6.418×10⁻¹⁴ and vs MA Holm p=1.843×10⁻¹⁸ (**both significant**). Bootstrap 95% CI (selective − SA accuracy) 0.0755–0.2901.

Shapiro–Wilk on paired LLM-faithfulness differences: normality **not** met (p≪0.05); Wilcoxon used as primary continuous test.

### 5. Constraints checked

| Constraint | Observed |
| --- | --- |
| No RAG / Qwen / judge rerun | `used_rag_rerun=false`; statistics import graph excludes architecture runners and `llama_cpp` |
| Phase 15 JSONL unchanged | SHA matched before and after `analyse()` |
| Phase 16 judge JSONL unchanged | SHA matched |
| Frozen 140/40 unchanged | SHA matched |
| T not retuned | lock still 0.65 |
| Paired unit = question | n=140 per architecture comparison |
| Not official RAGAS | metric label is custom/RAGAS-inspired |
| Phase 18 not started | no dissertation pack |
| Figure refresh does not change results | Phase 17 CSV/JSON SHA-256 unchanged after `scripts/render_phase17_figures.py` |

---

### 6. Dissertation figure refresh (presentation only)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 17 |
| Test name | `phase17_figure_refresh` |
| Command | `PYTHONPATH=. python scripts/render_phase17_figures.py` |
| Environment | Local Mac; `V2/.venv`; CPU; matplotlib 3.11.1 |
| Expected | Redraw six figures from saved Phase 17 tables; PNG 300 dpi + PDF + SVG; no change to statistical result files or frozen JSONL |
| Actual (observed) | **PASS**; 18 files written; `recomputed_statistics=false`; result-file SHA-256 unchanged; frozen SHA-256 unchanged |
| Status | **PASS** |
| Error | — |
| Output path | `results/config/phase17_figure_render.json`; `results/metrics/phase17_figures/`; `docs/phase17_figures.md` |

Primary (main body): `rq1_accuracy_wilson_ci`, `rq2_confidence_vs_faithfulness`, `rq3_coverage_selective`.  
Appendix: `rq1_mcnemar_counts`, `rq2_llm_faithfulness_box`, `rq3_uq_outcomes`.

Pytest: `tests/test_phase17_statistics.py::test_render_figures_does_not_change_results` **PASS**. Full suite `pytest -q -k "not test_analyse_paired_140"`: **130 passed** (analyse not re-run).

---

## Master record reference

> Validation evidence: `project_record/evidence/phase17_validation.md`
