# Phase 5 validation evidence

| Field | Value |
| --- | --- |
| Phase | 5 — Freeze DEV calibration 40 |
| Evidence file | `project_record/evidence/phase5_validation.md` |
| Last updated | 2026-08-21 (freeze); tests re-verified 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Calibration selection tests | PASS | `tests/test_phase5_calibration.py` |
| 2 | Calibration CSV | PASS | `data/calibration/calibration_questions.csv` |
| 3 | Calibration manifest | PASS | `data/calibration/calibration_manifest.json` |

---

## Test records

### 1. 40-question calibration freeze

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-21 (manifest) |
| Phase | 5 |
| Test name | `select_calibration` + overlap guard |
| Command | `PYTHONPATH=. python scripts/select_calibration.py` |
| Environment | Local Mac; FinQA **dev** only; seed **42** |
| Expected | 40 questions; no overlap with test 140; threshold not locked |
| Actual (observed) | **40** questions; **32** companies; SHA-256 `b229d45331fc18dd7c784175abd37cee3550775f268c843b2417d3f9d2e3aeca`; `threshold_locked: false` |
| Status | **PASS** |
| Error | — |
| Output path | `data/calibration/calibration_manifest.json` |

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 5 — Freeze DEV calibration 40
