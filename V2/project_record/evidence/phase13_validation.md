# Phase 13 validation evidence

| Field | Value |
| --- | --- |
| Phase | 13 — DEV calibration / threshold lock |
| Evidence file | `project_record/evidence/phase13_validation.md` |
| Last updated | 2026-08-26 |
| Phase 13 status | **Complete.** Official T = **0.65** locked on Colab T4 / Qwen3-8B from frozen FinQA **dev** 40. |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 13 unit/integration (numeric match, selector, lock guards, resume) | **PASS** | `tests/test_phase13_calibration.py` |
| 2 | Full pytest suite | **PASS** | 94 passed (2026-08-26) |
| 3 | Local mock calibration smoke (n=3 DEV UQ cases, real KB) | **PASS** (NOT LOCKED) | historical mock run_id `phase13_20260826T190630Z_e3c9b993` |
| 4 | Official `threshold.lock.json` from Colab T4 / 40 DEV cases | **PASS** | `results/config/threshold.lock.json` |

Pre-registered rule: maximise selective accuracy subject to coverage ≥ 0.50; tie-break lowest T. Frozen 140 and calibration CSV were not modified. 420-case benchmark not started.

Official lock (observed): **T=0.65**, coverage **0.55** (22 ANSWER / 18 ABSTAIN), selective accuracy **12/22 ≈ 0.5455**.

---

## Test records

### 1. Unit/integration tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T19:05:00Z |
| Phase | 13 |
| Test name | `test_phase13_calibration` |
| Command | `PYTHONPATH=. pytest tests/test_phase13_calibration.py -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | DEV-only IDs; no test leakage; mock cannot lock; resume skip/complete; numeric %/ratio match |
| Actual (observed) | **7 passed** (plus Phase 5 artefact test still **PASS**) |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase13_calibration.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T19:05:30Z |
| Phase | 13 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **94 passed** |
| Status | **PASS** |
| Error | — |
| Output path | — |

### 3. Local mock calibration smoke

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-26T19:06:34Z** |
| Phase | 13 |
| Test name | `phase13_calibration` |
| Command | `PYTHONPATH=. python scripts/run_calibration.py --backend mock --n-questions 3` |
| Environment | Local Mac; mock LLM; real Chroma (1239 chunks) |
| Expected | 3 DEV `multi_agent_uq` cases; candidate only; no `threshold.lock.json` |
| Actual (observed) | **PASS** — run_id `phase13_20260826T190630Z_e3c9b993`; completed=3; IDs `finqa_dev_130`, `142`, `178`; `locked=false`; note `candidate only — NOT LOCKED (Mock backend cannot lock the official threshold.)`. Official lock file was absent at that time. Later Colab files were copied into this folder name and overwrote the mock JSONL. |
| Status | **PASS** (local mock; T not locked from mock) |
| Error | — |
| Output path | historical mock path (JSONL later overwritten by Colab copy) |

### 4. Colab T4 official lock (40 DEV)

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-26T19:37:00Z** |
| Phase | 13 |
| Test name | `phase13_colab_lock` |
| Command / notebook | `PYTHONPATH=. python scripts/run_calibration.py --backend llama_cpp --n-questions 40` (`notebooks/colab_phase13_calibration.ipynb`) |
| Environment | Google Colab; Linux x86_64; Python 3.13.15; Tesla T4; `llama_cpp` 0.3.35; Qwen3-8B Q4_K_M; git `19368f1a53aacc4c4396b6d648e0722cc1c802ea` |
| Expected | `llama_cpp` + CUDA T4; 40 DEV UQ cases; `threshold.lock.json` with `locked: true`, `source_split: dev`, `used_frozen_test_140: false` |
| Actual (observed) | **PASS** — run_id `phase13_20260826T192003Z_7bcd6ed3`; completed=40; failed=0; all IDs `finqa_dev_*` and equal to Phase 5 `selected_ids`; 4 evidence chunks each; latency 19.41–47.95 s. Lock: `locked=true`, **T=0.65**, coverage=0.55, selective_accuracy=0.5454545454545454 (12/22), n_answer=22, n_abstain=18, `used_frozen_test_140=false`. Collection at smoke 0.55: 28 ANSWER / 12 ABSTAIN. |
| Status | **PASS** |
| Error | — |
| Output path | `results/raw/phase13_calibration/phase13_20260826T192003Z_7bcd6ed3/cases.jsonl`; `results/config/threshold.lock.json` |

---

## Constraints checked

| Constraint | Observed |
| --- | --- |
| Frozen 140 unmodified | not written by this phase; no `finqa_test_*` in calibration JSONL |
| Frozen calibration 40 unmodified | CSV used as input only; IDs match Phase 5 manifest |
| T not locked from mock | official lock is Colab `llama_cpp` + CUDA + n=40 |
| Official lock on DEV only | `source_split=dev`, `used_frozen_test_140=false` |
| 420-case benchmark not started | runner capped at 40 DEV UQ cases |
| V1 unmodified | no V1 paths edited |

---

## Master record reference

Validation evidence: `project_record/evidence/phase13_validation.md`
