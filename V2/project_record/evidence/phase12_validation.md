# Phase 12 validation evidence

| Field | Value |
| --- | --- |
| Phase | 12 — Pilot (6 frozen questions × 3 architectures = 18 cases) |
| Evidence file | `project_record/evidence/phase12_validation.md` |
| Last updated | 2026-08-24 |
| Phase 12 status | **Local complete.** Colab T4 / Qwen3-8B execution is **NEEDS VERIFICATION**. |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 12 unit/integration (subset, store, resume, duplicates, errors) | **PASS** | `tests/test_phase12_pilot.py` |
| 2 | Full pytest suite | **PASS** | 87 passed (2026-08-24) |
| 3 | Local mock pilot — 18 cases, real Chroma KB | **PASS** | `results/config/phase12_smoke_test.json` |
| 4 | Resume / duplicate prevention on the same run | **PASS** | same run_id; 18 skipped, 0 re-executed |
| 5 | Colab T4 / Qwen3-8B `llama_cpp` pilot | **NEEDS VERIFICATION** | `notebooks/colab_phase12_pilot.ipynb` |

Threshold used: `0.55` **smoke/demo — NOT LOCKED**. Frozen 140 and calibration 40 were not modified.

---

## Test records

### 1. Unit/integration tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-24T01:14:00Z |
| Phase | 12 |
| Test name | `test_phase12_pilot` |
| Command | `PYTHONPATH=. pytest tests/test_phase12_pilot.py -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | First-6 subset of frozen 140; 18 planned keys; checkpoint skip/resume; no duplicate writes; error isolation; refuse n=140 and locked threshold |
| Actual (observed) | **10 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase12_pilot.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-24T01:14:20Z |
| Phase | 12 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **87 passed** |
| Status | **PASS** |
| Error | — |
| Output path | — |

### 3. Local mock 18-case pilot (real retrieval)

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-24T01:15:15Z** |
| Phase | 12 |
| Test name | `phase12_pilot` |
| Command | `PYTHONPATH=. python scripts/run_pilot.py --backend mock --n-questions 6` |
| Environment | Local Mac; mock LLM; real Chroma KB (1239 chunks); device `mps_capable_host` |
| Expected | 18 COMPLETED cases; common raw schema; incremental JSONL; threshold 0.55 NOT LOCKED |
| Actual (observed) | **PASS** — run_id `phase12_20260824T011511Z_415d75de`; completed=18 failed=0 pending=0; 4 evidence chunks each; all decisions ANSWER; UQ confidence 0.5637–0.6349 vs threshold 0.55 NOT LOCKED. Mock answers are not Qwen3 answers. |
| Status | **PASS** (local mock) |
| Error | — |
| Output path | `results/raw/phase12_pilot/phase12_20260824T011511Z_415d75de/cases.jsonl` |

Observed UQ diagnostics (smoke threshold 0.55, **NOT LOCKED**):

| question_id | confidence | decision |
| --- | --- | --- |
| finqa_test_1000 | 0.6185 | ANSWER |
| finqa_test_1012 | 0.5886 | ANSWER |
| finqa_test_1017 | 0.6000 | ANSWER |
| finqa_test_1027 | 0.6349 | ANSWER |
| finqa_test_1039 | 0.5637 | ANSWER |
| finqa_test_1040 | 0.5918 | ANSWER |

### 4. Resume / duplicate prevention

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-24T01:15:26Z** |
| Phase | 12 |
| Test name | `phase12_pilot_resume_latest` |
| Command | `PYTHONPATH=. python scripts/run_pilot.py --backend mock --n-questions 6 --resume-latest` |
| Environment | Same local store as record 3 |
| Expected | Skip all 18 completed keys; do not append duplicates |
| Actual (observed) | executed_this_session=0 skipped_this_session=18; JSONL still 18 unique `case_key`s |
| Status | **PASS** |
| Error | — |
| Output path | `results/raw/phase12_pilot/phase12_20260824T011511Z_415d75de/cases.jsonl` |

### 5. Colab T4 / Qwen3-8B

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-24 |
| Phase | 12 |
| Test name | `phase12_colab_t4_qwen3` |
| Command / notebook | `notebooks/colab_phase12_pilot.ipynb` |
| Environment | Not run in this session |
| Expected | `llama_cpp` + CUDA T4; 18 cases; raw + checkpoint on Drive |
| Actual (observed) | Notebook and runner are implemented. This session did not execute Colab. |
| Status | **NEEDS VERIFICATION** |
| Error | — |
| Output path | — |

**Notes:** Push V2 to `cursor/empty-v2-workspace` before cloning on Colab. If disconnected, use `--resume-latest` (section 5b). Do not treat the local mock JSON as a T4 result.

---

## Constraints checked

| Constraint | Observed |
| --- | --- |
| Frozen 140 unmodified | `git status` clean for `data/final/selected_140_questions.csv` |
| Frozen calibration 40 unmodified | `git status` clean for `data/calibration/calibration_questions.csv` |
| Threshold not locked | `threshold_locked: false`; no `threshold.lock.json` |
| 420-case benchmark not started | runner capped at 6 questions / 18 cases |
| V1 unmodified | no V1 paths edited |
| Architectures unchanged | Phase 8–10 modules not modified |

---

## Master record reference

Validation evidence: `project_record/evidence/phase12_validation.md`
