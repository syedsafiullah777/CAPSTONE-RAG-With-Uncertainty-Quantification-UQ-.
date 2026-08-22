# Phase 7 validation evidence

| Field | Value |
| --- | --- |
| Phase | 7 — Qwen3-8B backend |
| Evidence file | `project_record/evidence/phase7_validation.md` |
| Last updated | 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | GGUF filename on Hugging Face | **PASS** | HF `bartowski/Qwen_Qwen3-8B-GGUF` / `Qwen_Qwen3-8B-Q4_K_M.gguf` (~5.03 GB) |
| 2 | Config + factory filename | **PASS** | `config/experiment.yaml`, `tests/test_phase7_model_backend.py` |
| 3 | Full pytest suite | **PASS** | `project_record/evidence/artifacts/phase7_pytest_20260822T161500Z.txt` (36 passed) |
| 4 | Local LLM smoke (`ollama_dev`) | **PASS** | `results/config/phase7_smoke_test.json` |
| 5 | Colab GPU smoke (`llama_cpp`) | **NEEDS VERIFICATION** | `notebooks/colab_phase7_smoke.ipynb` |

---

## Test records

### 1. GGUF filename fix (llama_cpp)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:14:37 |
| Phase | 7 |
| Test name | `hf_gguf_filename_resolution` |
| Command | `huggingface_hub.get_hf_file_metadata` for repo/file |
| Environment | Local Mac (HF Hub API) |
| Expected | File `Qwen_Qwen3-8B-Q4_K_M.gguf` resolves on `bartowski/Qwen_Qwen3-8B-GGUF` |
| Actual (observed) | **PASS** — size **5027784224** bytes |
| Status | **PASS** |
| Error | — |
| Output path | `config/experiment.yaml` → `model.gguf_filename` |

**Fix applied:** was `Qwen3-8B-Q4_K_M.gguf` (wrong) → now `Qwen_Qwen3-8B-Q4_K_M.gguf` (correct).

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:15:00 |
| Phase | 7 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -v --tb=short` |
| Environment | Local Mac; `.venv`; Python 3.13 |
| Expected | All V2 tests pass including `test_gguf_filename_matches_hf_repo` |
| Actual (observed) | **36 passed in 4.94s** |
| Status | **PASS** |
| Error | — |
| Output path | `project_record/evidence/artifacts/phase7_pytest_20260822T161500Z.txt` |

### 3. Local LLM generation smoke (post-fix)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:14:59 |
| Phase | 7 |
| Test name | `phase7_llm_generation_smoke` |
| Command | `PYTHONPATH=. python scripts/smoke_generate.py --backend ollama_dev` |
| Environment | Local Mac; Ollama `qwen3:8b`; fingerprint shows `gguf_filename: Qwen_Qwen3-8B-Q4_K_M.gguf` |
| Expected | Non-empty generation; config records corrected GGUF filename |
| Actual (observed) | Text **`4`**; latency ~11s; `gguf_filename` in fingerprint **Qwen_Qwen3-8B-Q4_K_M.gguf** |
| Status | **PASS** (local dev smoke — not Colab `llama_cpp` path) |
| Error | — |
| Output path | `results/config/phase7_smoke_test.json` |

### 4. Colab GPU smoke (`llama_cpp`)

| Field | Value |
| --- | --- |
| Date/time (UTC) | — |
| Phase | 7 |
| Test name | `phase7_colab_gpu_smoke` |
| Command / notebook | `notebooks/colab_phase7_smoke.ipynb` → `--backend llama_cpp` |
| Environment | Google Colab GPU — **not run in this session** |
| Expected | GGUF loads with corrected filename and generates non-empty text |
| Actual (observed) | **Not run** |
| Status | **NEEDS VERIFICATION** |
| Error | — |
| Output path | (pending Colab run) |

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 7 — Qwen3-8B backend
