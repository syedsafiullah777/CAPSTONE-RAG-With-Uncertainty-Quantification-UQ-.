# Phase 14 validation evidence

| Field | Value |
| --- | --- |
| Phase | 14 — Benchmark runner / 9-case validation |
| Evidence file | `project_record/evidence/phase14_validation.md` |
| Last updated | 2026-08-26 |
| Phase 14 status | **Local 9-case validation complete (mock PASS).** Official Colab T4 9-case is **NEEDS VERIFICATION**. Full 420-case benchmark **not launched**. |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 14 unit/integration (lock T=0.65, subset, resume, retry, Drive sync, refuse 420) | **PASS** | `tests/test_phase14_benchmark.py` |
| 2 | Full pytest suite | **PASS** | 105 passed (2026-08-26) |
| 3 | Local mock 9-case validation (3 frozen test × 3 architectures, T=0.65) | **PASS** | `results/config/phase14_smoke_test.json` |
| 4 | Colab T4 9-case (`llama_cpp` / Qwen3-8B) | **NEEDS VERIFICATION** | `notebooks/colab_phase14_benchmark_validation.ipynb` |
| 5 | Full 420-case benchmark | **not launched** | CLI refuses `--allow-full-420` |

Locked T=0.65 from Phase 13. Frozen 140/40 CSVs unmodified. Three RAG modules unmodified. V1 unmodified.

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
| Expected | First 3 frozen IDs; T=0.65; resume/skip/retry; Drive copy when `V2_DRIVE_ROOT` set; n>3 refused without full flag |
| Actual (observed) | **11 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase14_benchmark.py` |

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

### 3. Local mock 9-case validation

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-26T19:56:33Z** |
| Phase | 14 |
| Test name | `phase14_benchmark_validation` |
| Command | `PYTHONPATH=. python scripts/run_benchmark.py --backend mock --n-questions 3 --no-drive-sync` then `--resume-latest` |
| Environment | Local Mac; mock LLM; real Chroma (1239 chunks); locked T=0.65 |
| Expected | 9 independent cases; checkpoint/resume; retry failed; skip completed; T=0.65 LOCKED; not 420 |
| Actual (observed) | First attempt **FAIL** (9/9 `ProxyError: 403 Forbidden` on retrieval in the sandbox). `--resume-latest` retried failed keys → **PASS** 9/9 unique completed; 4 chunks each; UQ 3/3 **ABSTAIN** (mock confidence 0.5886–0.6185 < 0.65). Third resume skipped 9 duplicates. `--allow-full-420` refused (exit 1). JSONL has 18 lines (9 failed + 9 successful retries); unique keys = 9. Run_id `phase14_20260826T195616Z_f9550cce`. |
| Status | **PASS** (local mock; not Colab T4 / Qwen3-8B) |
| Error | First-pass ProxyError 403 (recovered by retry) |
| Output path | `results/raw/phase14_benchmark/phase14_20260826T195616Z_f9550cce/cases.jsonl` |

### 4. Colab T4 9-case

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26 |
| Phase | 14 |
| Test name | `phase14_colab_validation` |
| Command / notebook | `notebooks/colab_phase14_benchmark_validation.ipynb` |
| Environment | Not run in this session |
| Expected | `llama_cpp` + CUDA T4; 9 cases; T=0.65 locked; Drive sync |
| Actual (observed) | Notebook and runner implemented. Official 9-case T4 requires Colab after push. |
| Status | **NEEDS VERIFICATION** |
| Error | — |
| Output path | — |

---

## Constraints checked

| Constraint | Observed |
| --- | --- |
| Frozen 140 unmodified | input only; IDs `finqa_test_1000/1012/1017` |
| Frozen calibration 40 unmodified | not used as eval set |
| T not recalibrated | lock T=0.65; lock file not rewritten by the runner |
| Architectures independent | 9 distinct `{architecture}:{question_id}` keys; no chaining |
| 420 not launched | `--n-questions 3`; `--allow-full-420` refused |
| V1 unmodified | no V1 paths edited |

---

## Master record reference

Validation evidence: `project_record/evidence/phase14_validation.md`
