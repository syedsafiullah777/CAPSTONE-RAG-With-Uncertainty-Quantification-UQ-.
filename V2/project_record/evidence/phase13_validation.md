# Phase 13 validation evidence

| Field | Value |
| --- | --- |
| Phase | 13 — DEV calibration / threshold lock |
| Evidence file | `project_record/evidence/phase13_validation.md` |
| Last updated | 2026-08-26 |
| Phase 13 status | **Local runner complete.** Official T lock on Colab T4 / Qwen3-8B is **NEEDS VERIFICATION**. Mock cannot lock T. |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 13 unit/integration (numeric match, selector, lock guards, resume) | **PASS** | `tests/test_phase13_calibration.py` |
| 2 | Full pytest suite | **PASS** | 94 passed (2026-08-26) |
| 3 | Local mock calibration smoke (n=3 DEV UQ cases, real KB) | **PASS** (NOT LOCKED) | `results/config/phase13_smoke_test.json` |
| 4 | Official `threshold.lock.json` from Colab T4 / 40 DEV cases | **NEEDS VERIFICATION** | `notebooks/colab_phase13_calibration.ipynb` |

Pre-registered rule: maximise selective accuracy subject to coverage ≥ 0.50; tie-break lowest T. Frozen 140 and calibration CSV were not modified. 420-case benchmark not started.

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
| Actual (observed) | **PASS** — run_id `phase13_20260826T190630Z_e3c9b993`; completed=3; IDs `finqa_dev_130`, `142`, `178`; `locked=false`; note `candidate only — NOT LOCKED (Mock backend cannot lock the official threshold.)`. Official lock file **absent**. |
| Status | **PASS** (local mock; T not locked) |
| Error | — |
| Output path | `results/raw/phase13_calibration/phase13_20260826T190630Z_e3c9b993/cases.jsonl` |

### 4. Colab T4 official lock (40 DEV)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26 |
| Phase | 13 |
| Test name | `phase13_colab_lock` |
| Command / notebook | `notebooks/colab_phase13_calibration.ipynb` |
| Environment | Not run in this session |
| Expected | `llama_cpp` + CUDA T4; 40 DEV UQ cases; `threshold.lock.json` with `locked: true`, `source_split: dev`, `used_frozen_test_140: false` |
| Actual (observed) | Notebook and runner implemented. Official lock requires Colab. |
| Status | **NEEDS VERIFICATION** |
| Error | — |
| Output path | — |

---

## Constraints checked

| Constraint | Observed |
| --- | --- |
| Frozen 140 unmodified | not written by this phase |
| Frozen calibration 40 unmodified | CSV used as input only |
| T not locked from mock | `threshold.lock.json` absent; candidate `locked: false` |
| 420-case benchmark not started | runner capped at 40 DEV UQ cases |
| V1 unmodified | no V1 paths edited |

---

## Master record reference

Validation evidence: `project_record/evidence/phase13_validation.md`
