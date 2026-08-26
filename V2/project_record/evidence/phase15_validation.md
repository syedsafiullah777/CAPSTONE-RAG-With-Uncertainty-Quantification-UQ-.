# Phase 15 validation evidence

| Field | Value |
| --- | --- |
| Phase | 15 — Final 420-case benchmark |
| Evidence file | `project_record/evidence/phase15_validation.md` |
| Last updated | 2026-08-27 |
| Phase 15 status | Colab T4 420/420 locally verified at canonical run-id path. Drive archive **NEEDS VERIFICATION**. Evaluation/metrics not started. |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 15 notebook / entrypoint structure | **PASS** | `tests/test_phase15_benchmark.py` |
| 2 | Official Colab T4 420-case execution | **PASS** (local JSONL/summary/log) | `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/` |
| 3 | Backup / sync checklist | **local verified; Drive NEEDS VERIFICATION** | `evidence/phase15_backup_manifest.md` |

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
| Expected | Notebook is 140×3=420; uses `run_full_benchmark.py`; T=0.65; Drive/resume; Phase 14 9-case notebook unchanged; mock refused; empty `results/raw/phase15_benchmark/` exists |
| Actual (observed) | **6 passed** (2026-08-27). Empty `results/raw/phase15_benchmark/` and `results/checkpoints/phase15_benchmark/` exist. Frozen 140/40 and T not modified. 420-case job **not** run. |
| Status | **PASS** (structure only) |
| Error | — |
| Output path | `notebooks/colab_phase15_full_benchmark.ipynb`; `scripts/run_full_benchmark.py` |

### 1b. Local raw path correction (2026-08-27)

User-copied Colab files were in `results/raw/phase15_benchmark/` (missing run-id folder). They were moved, content unchanged (SHA-256 match), to:

`results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/`

(`cases.jsonl` 420 unique keys; SHA-256 of the moved files matched the misplaced copies.)

Checkpoint copy: `results/checkpoints/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4.json`.

### 2. Official 420-case Colab run (local archive inspected 2026-08-27)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T23:11:58Z (run end); inspected 2026-08-26T23:38:22Z |
| Phase | 15 |
| Test name | `phase15_full_benchmark` |
| Command / notebook | `notebooks/colab_phase15_full_benchmark.ipynb` / `scripts/run_full_benchmark.py --backend llama_cpp` |
| Environment | Colab Tesla T4; `llama_cpp`; Qwen3-8B Q4_K_M; git `e3c6094` |
| Expected | 140 frozen test × 3 architectures = 420 unique keys; T=0.65 LOCKED; no duplicates |
| Actual (observed) | JSONL **420** lines, **420** unique keys, **0** duplicates, **0** missing, **0** errors, **0** pending. Architectures 140/140/140. Question IDs = frozen 140 set. T=0.65. Summary/smoke **PASS**. |
| Status | **PASS** (local artefacts). Drive copy **NEEDS VERIFICATION**. |
| Error | — |
| Output path | `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` |

### 3. Backup checklist

See `project_record/evidence/phase15_backup_manifest.md` and `project_record/evidence/artifacts/phase15_backup_manifest.json`.

---

## Constraints checked

| Constraint | Observed |
| --- | --- |
| Frozen 140 unmodified this inspection | not written |
| Frozen calibration 40 unmodified | not written |
| T not recalibrated | lock still 0.65; `used_frozen_test_140=false` |
| Phase 14 9-case notebook unchanged | still `--n-questions 3` |
| V1 unmodified | no V1 paths edited |
| 420 cases locally complete | 420 unique keys; JSONL not rewritten this inspection |

---

## Master record reference

Validation evidence: `project_record/evidence/phase15_validation.md`
