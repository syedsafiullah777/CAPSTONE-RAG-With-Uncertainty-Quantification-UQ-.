# Phase 18 validation evidence

| Field | Value |
| --- | --- |
| Phase | 18 — Qualitative error analysis |
| Evidence file | `project_record/evidence/phase18_validation.md` |
| Last updated | 2026-08-28 |
| Phase 18 status | **PASS** on frozen Phase 15/16/17 artefacts. No RAG/Qwen/judge/statistics rerun. Phase 19 not started. |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 18 unit/integration tests | **PASS** | `tests/test_phase18_error_analysis.py` (4 passed) |
| 2 | Official error-analysis run | **PASS** | `results/config/phase18_smoke_test.json` |
| 3 | Frozen SHA gates | **PASS** | Phase 15/16 JSONL and Phase 17 tables unchanged after the run |
| 4 | Phase 19 dissertation pack | **not started** | — |

Locked T=0.65 unchanged. Frozen 140/40 unchanged. V1 unmodified.

---

## Test records

### 1. Unit / integration tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 18 |
| Test name | `test_phase18_error_analysis` |
| Command | `PYTHONPATH=. pytest tests/test_phase18_error_analysis.py -q` |
| Environment | Local Mac; `V2/.venv`; CPU |
| Expected | Taxonomy rules; no RAG imports; 420 cases labelled; both false abstentions in sample; source SHA unchanged |
| Actual (observed) | **4 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase18_error_analysis.py` |

Full suite excluding `test_analyse_paired_140` (not re-run to avoid recomputing Phase 17 tests): **134 passed**.

### 2. Official analysis run

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 18 |
| Test name | `phase18_error_analysis` |
| Command | `PYTHONPATH=. python scripts/run_error_analysis.py` |
| Environment | Local Mac CPU; `used_llm_inference=false`; `used_gpu=false`; `used_rag_rerun=false` |
| Expected | Rule-based taxonomy on 420 frozen cases plus stratified sample; T=0.65 unchanged |
| Actual (observed) | `status=PASS n_cases=420 n_sample=81 n_sample_questions=42 seed=18 false_abstentions_in_sample=2 source_artefacts_unchanged=true` |
| Status | **PASS** |
| Error | — |
| Output path | `results/final/phase18_error_analysis.md`; `results/analysis/phase18_error_cases.csv`; `results/analysis/phase18_error_summary.csv` |

Source hashes (verified, unchanged):

- Phase 15: `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa`
- Phase 16 processed: `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91`
- Judge JSONL: `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3`

### 3. Constraints checked

| Constraint | Observed |
| --- | --- |
| No RAG / Qwen / judge rerun | `used_rag_rerun=false`; error_analysis import graph excludes architecture runners and `llama_cpp` |
| No Phase 17 test recomputation | `src.statistics.analysis` not imported by Phase 18 |
| Phase 15/16 JSONL unchanged | SHA matched before and after `run_error_analysis()` |
| T not retuned | lock still 0.65 |
| Not official RAGAS | report uses custom/RAGAS-inspired label |
| Numeric error ≠ hallucination | taxonomy never uses hallucination as a category |
| Phase 19 not started | no dissertation pack |

---

## Master record reference

> Validation evidence: `project_record/evidence/phase18_validation.md`
