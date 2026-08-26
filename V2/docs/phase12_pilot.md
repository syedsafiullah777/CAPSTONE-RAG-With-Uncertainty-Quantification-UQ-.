# Phase 12 — Pilot (18 cases)

Small reproducible subset of the frozen 140-question test set, run independently through all three RAG architectures.

**6 questions × 3 architectures = 18 cases.**

## Purpose

Validate end-to-end experimental stability before calibration lock and the 420-case benchmark:

- Colab T4 / Qwen3-8B (`llama_cpp`)
- retrieval, generation, verification, confidence, ANSWER/ABSTAIN
- common `RAGCaseResult` schema
- raw JSONL persistence
- checkpoint / resume / duplicate prevention
- per-case error handling and latency logging

## What this phase does not do

- Does **not** modify `data/final/selected_140_questions.csv`
- Does **not** modify `data/calibration/calibration_questions.csv`
- Does **not** lock the confidence threshold
- Does **not** run the 140 × 3 = 420 benchmark
- Does **not** change the three RAG architectures

## Subset

First 6 rows of the Phase 4 frozen CSV (seed-42 order). Manifest: `data/final/pilot_subset_manifest.json`.

## Threshold

`uncertainty.smoke_threshold` **0.55** for UQ diagnostics only — **smoke/demo — NOT LOCKED**.

## Commands

```bash
cd V2
PYTHONPATH=. python scripts/run_pilot.py --backend mock
# Colab GPU:
PYTHONPATH=. python scripts/run_pilot.py --backend llama_cpp
# After disconnect:
PYTHONPATH=. python scripts/run_pilot.py --backend llama_cpp --resume-latest --retry-failed
```

`--n-questions` is capped at 6. The 420-case runner is a later phase.

## Outputs

| Artefact | Path |
| --- | --- |
| Raw cases | `results/raw/phase12_pilot/{run_id}/cases.jsonl` |
| Checkpoint | `results/raw/phase12_pilot/{run_id}/checkpoint.json` |
| Checkpoint copy | `results/checkpoints/phase12_pilot/{run_id}.json` |
| Summary | `results/config/phase12_pilot_summary.json` |

Colab notebook: `notebooks/colab_phase12_pilot.ipynb`
