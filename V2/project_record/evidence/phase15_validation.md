# Phase 15 validation evidence

| Field | Value |
| --- | --- |
| Phase | 15 — Final 420-case benchmark |
| Evidence file | `project_record/evidence/phase15_validation.md` |
| Last updated | 2026-08-26 |
| Phase 15 status | **Notebook and entrypoint created.** Official 420-case Colab run **not launched**. |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 15 notebook / entrypoint structure | **PASS** | `tests/test_phase15_benchmark.py` |
| 2 | Official Colab T4 420-case execution | **not launched** | `notebooks/colab_phase15_full_benchmark.ipynb` |

Phase 14 9-case notebook left unchanged as engineering evidence.

---

## Test records

### 1. Notebook and runner structure

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26 |
| Phase | 15 |
| Test name | `test_phase15_benchmark` |
| Command | `PYTHONPATH=. pytest tests/test_phase15_benchmark.py -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | Notebook is 140×3=420; uses `run_full_benchmark.py`; T=0.65; Drive/resume; Phase 14 9-case notebook unchanged; mock refused |
| Actual (observed) | **5 passed**. Notebook JSON valid (nbformat 4, 18 cells). Frozen 140/40 and T not modified. 420-case job **not** run. |
| Status | **PASS** (structure only) |
| Error | — |
| Output path | `notebooks/colab_phase15_full_benchmark.ipynb`; `scripts/run_full_benchmark.py` |

### 2. Official 420-case Colab run

| Field | Value |
| --- | --- |
| Date/time (UTC) | — |
| Phase | 15 |
| Test name | `phase15_full_benchmark` |
| Command / notebook | `notebooks/colab_phase15_full_benchmark.ipynb` |
| Environment | Not started |
| Expected | `llama_cpp` + Colab GPU; 420 unique cases; T=0.65; Drive checkpoints |
| Actual (observed) | Not launched during notebook creation. |
| Status | **not launched** |
| Error | — |
| Output path | — |

---

## Constraints checked

| Constraint | Observed |
| --- | --- |
| Frozen 140 unmodified | not written |
| Frozen calibration 40 unmodified | not written |
| T not recalibrated | lock file not rewritten by this phase |
| Phase 14 9-case notebook unchanged | still `--n-questions 3` |
| V1 unmodified | no V1 paths edited |
| 420 not executed here | structure only |

---

## Master record reference

Validation evidence: `project_record/evidence/phase15_validation.md`
