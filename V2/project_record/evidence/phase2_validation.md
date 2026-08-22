# Phase 2 validation evidence

| Field | Value |
| --- | --- |
| Phase | 2 — V1 audit + FinQA live profile |
| Evidence file | `project_record/evidence/phase2_validation.md` |
| Last updated | 2026-08-21 (profile run); tests re-verified 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | FinQA profile tests | PASS | `tests/test_phase2_profile.py` |
| 2 | Live profile JSON | PASS | `data/processed/finqa_profile.json` |
| 3 | Profile documentation | PASS | `docs/dataset_profile.md` |

---

## Test records

### 1. FinQA live profile

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-21 (profile generation) |
| Phase | 2 |
| Test name | `test_phase2_profile` + live dataset load |
| Command | `PYTHONPATH=. python scripts/inspect_dataset.py` (historical); `pytest tests/test_phase2_profile.py` |
| Environment | Local Mac; Hugging Face `datasets` |
| Expected | FinQA loads; split counts documented |
| Actual (observed) | train **6251**, dev **883**, test **1147**, total **8281**; 21 columns |
| Status | **PASS** |
| Error | — |
| Output path | `data/processed/finqa_profile.json`, `docs/dataset_profile.md` |

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 2 — V1 audit + FinQA live profile
