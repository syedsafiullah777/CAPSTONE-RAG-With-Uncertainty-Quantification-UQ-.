# Phase 7 — Qwen3-8B backend

## Objective

Provide a backend abstraction so RAG code is not tied to a single inference stack, log a runtime fingerprint, and prove one successful generation.

## Remote execution strategy (locked for V2)

| Item | Value |
| --- | --- |
| Strategy | **Standard Google Colab GPU notebooks** |
| Primary entrypoint | `notebooks/colab_phase7_smoke.ipynb` |
| Companion notes | `notebooks/colab_runtime.md` |
| Colab CLI / `gcloud` | **Not used** |
| Next validation step | **Colab GPU verification** (`remote_execution.colab_gpu_verification: NEEDS_VERIFICATION`) |

Unchanged by this strategy update:

- Qwen3-8B as the primary LLM
- `src/models` backend abstraction
- Runtime fingerprinting
- Checkpointing / resumable benchmark design (later runner phases)

## Primary vs optional inference backends

| Path | Role |
| --- | --- |
| `llama_cpp` (GGUF Q4_K_M) | **Primary** for Colab GPU notebook runs |
| `transformers` (4-bit when CUDA) | Colab notebook fallback |
| `ollama_dev` | Optional **local smoke only** — not required for the final 420-case run |
| `mock` | Unit tests |

Default config `model.backend: auto` prefers llama-cpp if importable, else transformers+CUDA, else ollama_dev if present.

## Local smoke (optional)

```bash
cd V2
source .venv/bin/activate
PYTHONPATH=. python scripts/smoke_generate.py --backend ollama_dev
# Writes results/config/phase7_smoke_test.json (PASS/FAIL + observed output)
```

## Colab GPU smoke (required next validation)

1. **Push latest V2 to GitHub**
2. Open `notebooks/colab_phase7_smoke.ipynb` in Google Colab → **Runtime → GPU**
3. Check `REPO_URL` / `BRANCH` in setup cell → run all cells (clones repo; no Drive upload for code)
4. Optional: section 5 copies results to Drive for backup

Instructions: `notebooks/colab_runtime.md`

## Verified artefacts (Mac local smoke)

| Artefact | Path |
| --- | --- |
| Validation evidence | `project_record/evidence/phase7_validation.md` |
| Smoke test JSON | `results/config/phase7_smoke_test.json` |
| Fingerprint | `results/config/phase7_runtime_fingerprint.json` |

Live smoke (2026-08-22): backend `ollama_dev`, model `qwen3:8b`, answer `4`, latency ~9.9s — **PASS** (local dev only).  
Colab GPU smoke — **NEEDS VERIFICATION** (see evidence file).

## What this phase does *not* include

RAG architectures (Phases 8–10), Streamlit, or the 420-case benchmark.
