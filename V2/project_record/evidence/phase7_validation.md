# Phase 7 validation evidence

| Field | Value |
| --- | --- |
| Phase | 7 — Qwen3-8B backend |
| Evidence file | `project_record/evidence/phase7_validation.md` |
| Last updated | 2026-08-22 (Colab GPU smoke recorded) |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | GGUF filename on Hugging Face | **PASS** | HF `bartowski/Qwen_Qwen3-8B-GGUF` / `Qwen_Qwen3-8B-Q4_K_M.gguf` |
| 2 | Config + factory filename | **PASS** | `config/experiment.yaml`, `tests/test_phase7_model_backend.py` |
| 3 | Full pytest suite (local) | **PASS** | `project_record/evidence/artifacts/phase7_pytest_20260822T161500Z.txt` (36 passed) |
| 4 | Local LLM smoke (`ollama_dev`) | **PASS** | earlier local run |
| 5 | Colab GPU smoke (`llama_cpp`) | **PASS** | `results/config/phase7_smoke_test.json` + fingerprint |

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

### 2. Full pytest suite (local)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:15:00 |
| Phase | 7 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -v --tb=short` |
| Environment | Local Mac; `.venv` |
| Expected | All V2 tests pass including `test_gguf_filename_matches_hf_repo` |
| Actual (observed) | **36 passed in 4.94s** |
| Status | **PASS** |
| Error | — |
| Output path | `project_record/evidence/artifacts/phase7_pytest_20260822T161500Z.txt` |

### 3. Local LLM generation smoke (`ollama_dev`)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:14:59 |
| Phase | 7 |
| Test name | `phase7_llm_generation_smoke` (local) |
| Command | `PYTHONPATH=. python scripts/smoke_generate.py --backend ollama_dev` |
| Environment | Local Mac; Ollama `qwen3:8b` |
| Expected | Non-empty generation |
| Actual (observed) | Text **`4`** |
| Status | **PASS** (local dev only) |
| Error | — |
| Output path | superseded by Colab artefact below |

### 4. Colab GPU smoke (`llama_cpp`) — verified

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:23:06 |
| Phase | 7 |
| Test name | `phase7_llm_generation_smoke` / `phase7_colab_gpu_smoke` |
| Command / notebook | `notebooks/colab_phase7_smoke.ipynb` → `PYTHONPATH=. python scripts/smoke_generate.py --backend llama_cpp` |
| Environment | Google Colab; **Tesla T4**; CUDA; Linux; Python 3.13.15; torch 2.11.0+cu128; llama_cpp 0.3.35 |
| Expected | Configured backend produces non-empty text for the smoke prompt |
| Actual (observed) | **PASS**; backend `llama_cpp`; model `Qwen3-8B`; quant `Q4_K_M`; GGUF `Qwen_Qwen3-8B-Q4_K_M.gguf`; output begins with **`4`**; latency **15.37s**; `finish_reason: length` (512 completion tokens); run_id `phase7_20260822T162122Z_cee1f3d4`; error null |
| Status | **PASS** |
| Error | — |
| Output path | `results/config/phase7_smoke_test.json` |
| Fingerprint path | `results/config/phase7_runtime_fingerprint.json` |

**GPU (fingerprint):** Tesla T4; VRAM total 15360 MB; free at capture 14913 MB; driver 580.82.07.

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 7 — Qwen3-8B backend
