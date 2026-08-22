# Phase 3 validation evidence

| Field | Value |
| --- | --- |
| Phase | 3 — PDF resolvability verification |
| Evidence file | `project_record/evidence/phase3_validation.md` |
| Last updated | 2026-08-21 (probe run); tests re-verified 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 3 verification tests | PASS | `tests/test_phase3_verification.py` |
| 2 | PDF probe (test split) | PASS | `data/processed/finqa_pdf_probe.json` |
| 3 | Checkpoint documentation | PASS | `docs/phase3_dataset_verification.md` |

---

## Test records

### 1. Test-split PDF resolvability

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-21 |
| Phase | 3 |
| Test name | HF repo PDF probe |
| Command | PDF probe script (see `docs/phase3_dataset_verification.md`) |
| Environment | Local Mac; Hugging Face Hub |
| Expected | Test PDFs resolvable at `data/FinQA/{split}/{file_name}` |
| Actual (observed) | **380/380** test PDFs resolved; **0** missing |
| Status | **PASS** |
| Error | — |
| Output path | `data/processed/finqa_pdf_probe.json` |

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 3 — PDF resolvability
