# Phase 7 — Qwen3-8B backend

## Objective

Provide a backend abstraction so RAG code is not tied to a single inference stack, log a runtime fingerprint, and prove one successful generation.

## Primary vs optional paths

| Path | Role |
| --- | --- |
| `llama_cpp` (GGUF Q4_K_M) | **Primary** for Colab GPU benchmark |
| `transformers` (4-bit when CUDA) | Colab fallback |
| `ollama_dev` | Optional **local smoke only** — not required for the final 420-case run |
| `mock` | Unit tests |

Default config `model.backend: auto` prefers llama-cpp if importable, else transformers+CUDA, else ollama_dev if present.

## Smoke command

```bash
cd V2
source .venv/bin/activate
PYTHONPATH=. python scripts/smoke_generate.py --backend ollama_dev   # local smoke
# On Colab GPU:
# PYTHONPATH=. python scripts/smoke_generate.py --backend llama_cpp
```

Colab notes: `notebooks/colab_runtime.md`

## Verified artefacts (this machine)

| Artefact | Path |
| --- | --- |
| Fingerprint | `results/config/phase7_runtime_fingerprint.json` |
| Smoke generation | `results/config/phase7_smoke_generate.json` |

Live smoke (2026-08-21): backend `ollama_dev`, model `qwen3:8b`, answer `4`, latency ~4.9s.  
**NEEDS VERIFICATION on Colab GPU:** GGUF load + VRAM fit for `Q4_K_M` / transformers 4-bit.

## What this phase does *not* include

RAG architectures (Phases 8–10), Streamlit, or the 420-case benchmark.
