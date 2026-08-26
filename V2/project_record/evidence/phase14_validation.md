# Phase 14 validation evidence

| Field | Value |
| --- | --- |
| Phase | 14 — Benchmark runner / 9-case engineering validation |
| Evidence file | `project_record/evidence/phase14_validation.md` |
| Last updated | 2026-08-26 |
| Phase 14 status | **9-case engineering validation complete** (local mock + Colab T4). **Not** a second mandatory smoke stage. **Next execution:** final **140 × 3 = 420** benchmark. **Not launched.** |

## Summary

| # | Test name | Status | Role | Evidence path |
| --- | --- | --- | --- | --- |
| 1 | Phase 14 unit/integration | **PASS** | engineering | `tests/test_phase14_benchmark.py` |
| 2 | Full pytest suite | **PASS** | engineering | 105 passed (2026-08-26) |
| 3 | Local mock 9-case | **PASS** | supporting engineering only | historical run `phase14_20260826T195616Z_f9550cce` |
| 4 | Colab T4 9-case (`llama_cpp` / Qwen3-8B Q4_K_M) | **PASS** | supporting engineering only | `results/config/phase14_smoke_test.json` |
| 5 | Full 420-case benchmark | **not launched** | **next execution** | 140 frozen test × 3 architectures |

Do **not** run another 3-question / 9-case validation. The 9-case results stay as engineering evidence that checkpoint/resume, locked T=0.65, and independent architectures work.

Locked T=0.65 from Phase 13 (DEV 40). Frozen 140/40 unmodified. Three RAG modules unmodified. V1 unmodified. Threshold not recalibrated.

---

## Test records

### 1. Unit/integration tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T19:55:00Z |
| Phase | 14 |
| Test name | `test_phase14_benchmark` |
| Command | `PYTHONPATH=. pytest tests/test_phase14_benchmark.py -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | First 3 frozen IDs; T=0.65; resume/skip/retry; Drive copy when `V2_DRIVE_ROOT` set |
| Actual (observed) | **11 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase14_benchmark.py` |
| Notes | Engineering tests. Not a gate before 420. |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T19:55:20Z |
| Phase | 14 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **105 passed** |
| Status | **PASS** |
| Error | — |
| Output path | — |

### 3. Local mock 9-case (supporting engineering)

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-26T19:56:33Z** |
| Phase | 14 |
| Test name | `phase14_benchmark_validation` (mock) |
| Command | `PYTHONPATH=. python scripts/run_benchmark.py --backend mock --n-questions 3 --no-drive-sync` then `--resume-latest` |
| Environment | Local Mac; mock LLM; real Chroma (1239 chunks); locked T=0.65 |
| Expected | 9 independent cases; checkpoint/resume; retry failed; skip completed; T=0.65 LOCKED |
| Actual (observed) | First attempt **FAIL** (9/9 `ProxyError: 403 Forbidden`). Resume retried failed keys → **PASS** 9/9. Mock UQ 3/3 ABSTAIN. Run_id `phase14_20260826T195616Z_f9550cce`. |
| Status | **PASS** (mock; not official Qwen3-8B) |
| Error | First-pass ProxyError 403 (recovered by retry) |
| Output path | historical mock run (later Colab files were copied into this folder name) |
| Notes | Supporting engineering evidence only. Do not repeat. |

### 4. Colab T4 9-case (supporting engineering)

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-26T20:11:45Z** |
| Phase | 14 |
| Test name | `phase14_benchmark_validation` |
| Command / notebook | `PYTHONPATH=. python scripts/run_benchmark.py --backend llama_cpp --n-questions 3` (`notebooks/colab_phase14_benchmark_validation.ipynb`) |
| Environment | Google Colab; Linux x86_64; Python 3.13.15; Tesla T4; `llama_cpp` 0.3.35; Qwen3-8B Q4_K_M; git `20ee91e1af61f5b44b13a9586d370205c635fd8a` |
| Expected | 9 cases; T=0.65 locked; independent architectures; incremental JSONL; Drive checkpoint |
| Actual (observed) | **PASS** — run_id `phase14_20260826T200828Z_e91e588d`; completed=9; failed=0; IDs `finqa_test_1000`, `1012`, `1017`; 4 evidence chunks each; latency 16.47–43.16 s (sum 196.28 s); T=0.65 `threshold_locked=true`; lock_run_id `phase13_20260826T192003Z_7bcd6ed3`; `used_frozen_test_140_for_lock=false`. UQ: 2 ANSWER + 1 ABSTAIN on `finqa_test_1000` (confidence 0.5032 < 0.65). Colab summary reports Drive sync to `MyDrive/MSc-RAG/results/raw/phase14_benchmark/phase14_20260826T200828Z_e91e588d`. Local copy of `cases.jsonl` is 9 unique T4 lines (files were dropped into the old mock folder name). |
| Status | **PASS** (engineering validation; not the 420-case benchmark) |
| Error | — |
| Output path | `results/config/phase14_smoke_test.json`; `results/config/phase14_benchmark_summary.json`; JSONL under `results/raw/phase14_benchmark/` (Colab run_id `phase14_20260826T200828Z_e91e588d`) |

### 5. Final 420-case benchmark (next execution — not launched)

| Field | Value |
| --- | --- |
| Date/time (UTC) | — |
| Phase | 14 (final benchmark execution) |
| Test name | `phase14_benchmark_420` |
| Command / notebook | Colab GPU; `llama_cpp`; 140 frozen test × 3 architectures |
| Environment | Not started |
| Expected | 420 independent cases; T=0.65; Qwen3-8B Q4_K_M; shared Phase 6 KB; identical retrieval; incremental save; Drive checkpoint/resume; retry failures; no duplicates |
| Actual (observed) | **Not launched.** This documentation update does not start it. |
| Status | **not launched** |
| Error | — |
| Output path | — |

---

## Next execution (locked)

**140 frozen test questions × 3 architectures = 420 cases.**

| Setting | Value |
| --- | --- |
| Questions | Frozen FinQA **test** 140 (`data/final/selected_140_questions.csv`) |
| Architectures | `single_agent`, `multi_agent`, `multi_agent_uq` (independent; no chaining) |
| Threshold | **T = 0.65** from `results/config/threshold.lock.json` (do not recalibrate) |
| LLM | Qwen3-8B Q4_K_M via `llama_cpp` |
| Compute | Google Colab GPU |
| Knowledge base | Shared Phase 6 index (230 PDFs / 1239 chunks) |
| Retrieval | Identical config across architectures (`top_k=4`, `BAAI/bge-small-en-v1.5`) |
| Persistence | Incremental JSONL; checkpoint to Google Drive; resume; retry genuine failures; skip completed; no overwrite of raw results; progress logs |

Do **not** add another 9-case validation stage. Do **not** modify the frozen 140 or calibration 40. Do **not** modify V1.

---

## Constraints checked

| Constraint | Observed |
| --- | --- |
| Frozen 140 unmodified | 9-case used first 3 test IDs only |
| Frozen calibration 40 unmodified | not used as eval set |
| T not recalibrated | lock T=0.65; `modifies_threshold_lock=false` |
| Architectures independent | 9 distinct keys; `chained=false` |
| 9-case not repeated as a new gate | complete; next is 420 |
| 420 not launched | this update is documentation only |
| V1 unmodified | no V1 paths edited |

---

## Master record reference

Validation evidence: `project_record/evidence/phase14_validation.md`
