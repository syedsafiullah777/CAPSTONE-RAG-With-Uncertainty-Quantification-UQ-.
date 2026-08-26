# Phase 12 validation evidence

| Field | Value |
| --- | --- |
| Phase | 12 — Pilot (6 frozen questions × 3 architectures = 18 cases) |
| Evidence file | `project_record/evidence/phase12_validation.md` |
| Last updated | 2026-08-26 |
| Phase 12 status | **Complete** (local mock 18/18 + Colab T4 / Qwen3-8B `llama_cpp` 18/18 **PASS**, raw JSONL archived locally). |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 12 unit/integration (subset, store, resume, duplicates, errors) | **PASS** | `tests/test_phase12_pilot.py` |
| 2 | Full pytest suite | **PASS** | 87 passed (2026-08-24) |
| 3 | Local mock pilot — 18 cases, real Chroma KB | **PASS** | `results/config/phase12_smoke_test.json` |
| 4 | Resume / duplicate prevention on the same run | **PASS** | same run_id; 18 skipped, 0 re-executed |
| 5 | Colab T4 / Qwen3-8B `llama_cpp` pilot | **PASS** | `results/config/phase12_smoke_test.json`, `phase12_pilot_summary.json`, `phase12_runtime_fingerprint.json` |
| 6 | Local copy of Colab raw JSONL / checkpoint | **PASS** | `results/raw/phase12_pilot/phase12_20260826T183704Z_9773516a/cases.jsonl` |

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
| Date/time (UTC) | **2026-08-26T18:44:41Z** |
| Phase | 12 |
| Test name | `phase12_colab_t4_qwen3` |
| Command / notebook | `notebooks/colab_phase12_pilot.ipynb` → `PYTHONPATH=. python scripts/run_pilot.py --backend llama_cpp --n-questions 6` |
| Environment | Linux Colab; `llama_cpp`; Qwen3-8B Q4_K_M; device **cuda**; GPU **Tesla T4** (15360 MB; driver 580.82.07); torch 2.11.0+cu128; llama_cpp 0.3.35; Python 3.13.15; git `162fe3c` |
| Expected | `llama_cpp` + CUDA T4; 18 cases; threshold 0.55 NOT LOCKED; not the 420-case benchmark |
| Actual (observed) | **PASS** — run_id `phase12_20260826T183704Z_9773516a`; completed=18 failed=0 pending=0; executed_this_session=18 (not a resume); `threshold_locked: false`; `threshold_note: smoke/demo — NOT LOCKED`. All 18 planned case keys listed completed. |
| Status | **PASS** |
| Error | — |
| Output path | `results/config/phase12_smoke_test.json`; `results/config/phase12_pilot_summary.json`; `results/config/phase12_runtime_fingerprint.json` |

**Notes:** These three config files were copied locally on 2026-08-26. Per-case fields were not in the summary. **Correction (later 2026-08-26):** the Colab `cases.jsonl` was then copied locally — see record 6.

### 6. Local copy of Colab raw JSONL

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T18:53 (local file mtime) / run recorded 2026-08-26T18:44:41Z |
| Phase | 12 |
| Test name | `phase12_colab_raw_local_copy` |
| Command / notebook | inspect `V2/results/raw/phase12_pilot/` |
| Environment | Local Mac copy of Colab T4 `llama_cpp` JSONL; 18 unique case keys; device cuda; GPU Tesla T4; Qwen3-8B Q4_K_M |
| Expected | Colab run directory with 18 COMPLETED cases, schema fields, retrieval, generation, verification, confidence, ANSWER/ABSTAIN, latency |
| Actual (observed) | **PASS** — 18/18 unique keys; 0 errors; 4 evidence chunks each; no empty answers; latency 21.01–45.58 s (sum 457.46 s); seed 42; `threshold_locked: false`. Files were first dropped into the old mock folder name `phase12_20260824T011511Z_415d75de`; contents are run_id `phase12_20260826T183704Z_9773516a`. Canonical copy written to `results/raw/phase12_pilot/phase12_20260826T183704Z_9773516a/`. |
| Status | **PASS** |
| Error | — |
| Output path | `results/raw/phase12_pilot/phase12_20260826T183704Z_9773516a/cases.jsonl` |

Observed UQ (smoke threshold 0.55, **NOT LOCKED**):

| question_id | confidence | retrieval | verification | decision |
| --- | --- | --- | --- | --- |
| finqa_test_1000 | 0.5032 | 0.8119 | 0.1944 | **ABSTAIN** |
| finqa_test_1012 | 0.7743 | 0.7521 | 0.7964 | ANSWER |
| finqa_test_1017 | 0.7409 | 0.7750 | 0.7067 | ANSWER |
| finqa_test_1027 | 0.7909 | 0.8448 | 0.7369 | ANSWER |
| finqa_test_1039 | 0.6464 | 0.7024 | 0.5905 | ANSWER |
| finqa_test_1040 | 0.7113 | 0.7586 | 0.6641 | ANSWER |

Multi-Agent verification status: 1000 WEAK_EVIDENCE; 1012 VERIFIED; 1017 WEAK_EVIDENCE; 1027 VERIFIED; 1039 VERIFIED; 1040 VERIFIED.

**Notes:** `finqa_test_1000` UQ ABSTAIN is the existing gate (`0.5032 < 0.55`), not a forced abstain. Single-Agent and Multi-Agent still `decision=ANSWER` on that question (no UQ gate). This is not an accuracy evaluation of the 18 answers. The previous local mock JSONL in the misnamed folder is no longer present (replaced by these Colab files).

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
