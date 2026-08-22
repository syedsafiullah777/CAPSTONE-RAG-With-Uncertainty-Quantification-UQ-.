# Phase 7 validation evidence

| Field | Value |
| --- | --- |
| Phase | 7 — Qwen3-8B backend |
| Evidence file | `project_record/evidence/phase7_validation.md` |
| Last updated | 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 7 unit/integration tests | PASS | `tests/test_phase7_model_backend.py` |
| 2 | Full pytest suite | PASS | `project_record/evidence/artifacts/phase7_pytest_20260822T145200Z.txt` |
| 3 | Local LLM smoke (`ollama_dev`) | PASS | `results/config/phase7_smoke_test.json` |
| 4 | Runtime fingerprint | PASS | `results/config/phase7_runtime_fingerprint.json` |
| 5 | Colab GPU smoke (`llama_cpp`) | **NEEDS VERIFICATION** | `notebooks/colab_phase7_smoke.ipynb` |

---

## Test records

### 1. Phase 7 pytest module

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T14:52:07 |
| Phase | 7 |
| Test name | `test_phase7_model_backend` |
| Command | `PYTHONPATH=. pytest tests/test_phase7_model_backend.py -v` |
| Environment | Local Mac; Python 3.9.6; `.venv` |
| Expected | Fingerprint fields; mock generate; smoke validation artefact present |
| Actual (observed) | 4 tests pass (included in 34-test full suite) |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase7_model_backend.py` |

### 2. Full suite regression

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T14:52:07 |
| Phase | 7 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -v --tb=short` |
| Environment | Local Mac; `.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **34 passed in 5.42s** |
| Status | **PASS** |
| Error | — |
| Output path | `project_record/evidence/artifacts/phase7_pytest_20260822T145200Z.txt` |

### 3. Local LLM generation smoke

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T14:52:22 |
| Phase | 7 |
| Test name | `phase7_llm_generation_smoke` |
| Command | `PYTHONPATH=. python scripts/smoke_generate.py --backend ollama_dev` |
| Environment | Local Mac; device `mps_capable_host`; GPU nvidia-smi **unavailable**; Ollama `qwen3:8b` |
| Expected | Non-empty generation for smoke prompt (`2+2` → number) |
| Actual (observed) | Text **`4`**; latency **9.94s**; backend `ollama_dev` |
| Status | **PASS** (local dev smoke only — not the Colab benchmark path) |
| Error | — |
| Output path | `results/config/phase7_smoke_test.json` |

### 4. Colab GPU smoke (primary remote validation)

| Field | Value |
| --- | --- |
| Date/time (UTC) | — |
| Phase | 7 |
| Test name | `phase7_colab_gpu_smoke` |
| Command / notebook | `notebooks/colab_phase7_smoke.ipynb` → `scripts/smoke_generate.py --backend llama_cpp` |
| Environment | Google Colab GPU — **not executed in recorded session** |
| Expected | GGUF or transformers backend loads on Colab GPU and generates non-empty text |
| Actual (observed) | **Not run** |
| Status | **NEEDS VERIFICATION** |
| Error | — |
| Output path | (pending) `results/config/phase7_smoke_test.json` from Colab run |

**Note:** Phase 7 code abstraction is complete; Colab GPU verification remains the next validation step before treating the Colab runtime path as verified.

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 7 — Qwen3-8B backend
