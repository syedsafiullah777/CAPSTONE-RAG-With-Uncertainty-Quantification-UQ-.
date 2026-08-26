# Phase 14 — Benchmark runner and 9-case validation

Prepare the frozen **140 × 3 = 420** case runner. This phase **validates** it on **3 questions × 3 architectures = 9 cases** only.

## Locked threshold

Uses `results/config/threshold.lock.json` **T = 0.65** (Phase 13, FinQA **dev** 40).

- Does **not** recalibrate
- Does **not** modify the lock file
- Does **not** tune T on the frozen 140

## What this phase does not do

- Does **not** launch the full 420-case benchmark
- Does **not** modify `selected_140_questions.csv` or `calibration_questions.csv`
- Does **not** change the three RAG architecture modules
- Does **not** modify V1

## Validation subset

First 3 rows of the Phase 4 frozen CSV (seed-42 order):

`finqa_test_1000`, `finqa_test_1012`, `finqa_test_1017`

Architectures (independent, no chaining): `single_agent`, `multi_agent`, `multi_agent_uq`.

## Commands

```bash
cd V2
# Local 9-case validation (mock LLM; real KB)
PYTHONPATH=. python scripts/run_benchmark.py --backend mock --n-questions 3
# Colab T4 (9 cases, llama_cpp, T=0.65 locked)
# notebooks/colab_phase14_benchmark_validation.ipynb
# PYTHONPATH=. python scripts/run_benchmark.py --backend llama_cpp --n-questions 3
```

If disconnected: `--resume-latest`. Do not start a new run from question 1.

`--allow-full-420` is **refused** by this entrypoint.

## Recovery

- Incremental JSONL: `results/raw/phase14_benchmark/{run_id}/cases.jsonl`
- Checkpoint after each case
- Skip completed `{architecture}:{question_id}`
- Retry failed cases
- Refuse overwrite of an existing raw store
- Optional Drive sync when `V2_DRIVE_ROOT` is set (Colab: `/content/drive/MyDrive/MSc-RAG`)
