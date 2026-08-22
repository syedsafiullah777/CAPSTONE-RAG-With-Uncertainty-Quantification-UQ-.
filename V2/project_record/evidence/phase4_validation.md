# Phase 4 validation evidence

| Field | Value |
| --- | --- |
| Phase | 4 — Freeze 140 test questions |
| Evidence file | `project_record/evidence/phase4_validation.md` |
| Last updated | 2026-08-21 (freeze); tests re-verified 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Selection + manifest tests | PASS | `tests/test_phase4_select_140.py` |
| 2 | Frozen CSV | PASS | `data/final/selected_140_questions.csv` |
| 3 | Sampling manifest | PASS | `data/final/sampling_manifest.json` |

---

## Test records

### 1. 140-question freeze

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-21T16:01:49Z (manifest `frozen_at_utc`) |
| Phase | 4 |
| Test name | `select_140` + manifest replay |
| Command | `PYTHONPATH=. python scripts/select_140.py` |
| Environment | Local Mac; seed **42** |
| Expected | 140 unique questions; diversity caps; reproducible manifest hash |
| Actual (observed) | **140** questions; **77** companies; **140** files; SHA-256 `1a69d93e412097a076e8ec836253b8fff53366aefc5ea5f8998020984f6bbd8a` |
| Status | **PASS** |
| Error | — |
| Output path | `data/final/sampling_manifest.json` |

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 4 — Freeze test 140
