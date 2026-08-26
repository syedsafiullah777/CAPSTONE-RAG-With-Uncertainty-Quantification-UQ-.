# Phase 13 — DEV calibration and threshold lock

Lock the UQ abstention threshold **T** on the frozen FinQA **dev** 40-question set only.

## Pre-registered rule

Maximise **selective accuracy** (numeric match of the UQ **draft** to `program_answer`) among thresholds with **coverage ≥ 0.50**. Tie-break: **lowest T**.

T is **not** tuned on the frozen 140 or the Phase 12 pilot.

## Official lock (Colab T4, 2026-08-26)

| Field | Observed value |
| --- | --- |
| Run ID | `phase13_20260826T192003Z_7bcd6ed3` |
| Backend / GPU | `llama_cpp` / Tesla T4 |
| n | 40 FinQA **dev** (`used_frozen_test_140: false`) |
| Locked T | **0.65** |
| Coverage | 0.55 (22 ANSWER / 18 ABSTAIN) |
| Selective accuracy | 12/22 ≈ 0.5455 |
| Lock file | `results/config/threshold.lock.json` |

## What this phase does not do

- Does **not** modify `selected_140_questions.csv` or `calibration_questions.csv`
- Does **not** run the 140 × 3 = 420 benchmark
- Does **not** lock T from a mock backend
- Does **not** change the three RAG architecture modules

## Commands

```bash
cd V2
# Local smoke (writes candidate only — NOT LOCKED)
PYTHONPATH=. python scripts/run_calibration.py --backend mock --n-questions 3
# Colab T4 (40 DEV UQ cases, then official lock if CUDA + llama_cpp)
PYTHONPATH=. python scripts/run_calibration.py --backend llama_cpp
```

If disconnected: `--resume-latest`.

## Outputs

| Artefact | Path |
| --- | --- |
| Raw cases | `results/raw/phase13_calibration/{run_id}/cases.jsonl` |
| Candidate T | `results/config/threshold.candidate.json` |
| Official lock | `results/config/threshold.lock.json` (llama_cpp + CUDA + n=40 only) |

Colab: `notebooks/colab_phase13_calibration.ipynb`
