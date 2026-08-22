# Phase 1 validation evidence

| Field | Value |
| --- | --- |
| Phase | 1 — Project foundation |
| Evidence file | `project_record/evidence/phase1_validation.md` |
| Last updated | 2026-08-21 (phase work); pytest re-verified 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Config load + paths + logging | PASS | `tests/test_config_loads.py` |
| 2 | Full suite (includes Phase 1 tests) | PASS | `project_record/evidence/artifacts/phase7_pytest_20260822T145200Z.txt` (34 passed) |

---

## Test records

### 1. `test_config_loads` (Phase 1)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T14:52:07 (suite run) |
| Phase | 1 |
| Test name | config_loads + run_id + logging |
| Command | `PYTHONPATH=. pytest tests/test_config_loads.py -v` |
| Environment | Local Mac; Python 3.9.6; no GPU required |
| Expected | V2 root resolves; `experiment.yaml` loads; paths under V2; threshold null; run_id prefix |
| Actual (observed) | 6 tests in module pass as part of full suite (34 passed total) |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_config_loads.py` |

**Observed checks:** `project.name == msc-rag-v2`, `dataset.subset == FinQA`, `frozen_test_size == 140`, `confidence_threshold is None`.

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 1 — Project foundation
