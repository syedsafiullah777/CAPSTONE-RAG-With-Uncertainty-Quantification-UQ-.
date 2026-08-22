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
```

## Colab GPU smoke (required next validation)

1. Open `notebooks/colab_phase7_smoke.ipynb` in Google Colab
2. Runtime → GPU
3. Run the setup cell: it auto-finds V2, or mounts Drive, or prompts for `V2.zip` (Colab does **not** ship with `/content/V2`)
4. Run remaining cells (primary `--backend llama_cpp`)

## Verified artefacts (Mac local smoke)

| Artefact | Path |
| --- | --- |
| Fingerprint | `results/config/phase7_runtime_fingerprint.json` |
| Smoke generation | `results/config/phase7_smoke_generate.json` |

Live smoke (2026-08-21): backend `ollama_dev`, model `qwen3:8b`, answer `4`, latency ~4.9s.  
**NEEDS VERIFICATION on Colab GPU:** GGUF load + VRAM fit for `Q4_K_M` / transformers 4-bit via the Colab notebook.

## What this phase does *not* include

RAG architectures (Phases 8–10), Streamlit, or the 420-case benchmark.
