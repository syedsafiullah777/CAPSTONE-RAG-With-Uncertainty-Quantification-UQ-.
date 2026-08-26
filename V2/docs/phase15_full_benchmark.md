# Phase 15 — Final 420-case benchmark

Official evaluation: **140 frozen FinQA test questions × 3 architectures = 420 cases**.

The Phase 14 9-case notebook remains **engineering validation evidence**. Do not re-run it as a substitute for this job.

## Locked settings

| Item | Value |
| --- | --- |
| Eval set | Frozen FinQA **test** 140 |
| Architectures | `single_agent`, `multi_agent`, `multi_agent_uq` (independent) |
| Threshold | **T = 0.65** (`results/config/threshold.lock.json`) |
| Model | Qwen3-8B **Q4_K_M** |
| Backend | `llama_cpp` |
| Compute | Google Colab GPU |
| Knowledge base | Shared Phase 6 (230 PDFs / 1239 chunks) |
| Retrieval | Identical (`top_k=4`, `BAAI/bge-small-en-v1.5`) |

Do **not** modify the frozen 140/40, recalibrate T, change RAG modules, change retrieval, or modify V1.

## Colab

Notebook: `notebooks/colab_phase15_full_benchmark.ipynb`

```bash
cd V2
PYTHONPATH=. python scripts/run_full_benchmark.py --backend llama_cpp
# After disconnect:
PYTHONPATH=. python scripts/run_full_benchmark.py --backend llama_cpp --resume-latest
```

Mock backends are refused. Drive incremental sync uses `V2_DRIVE_ROOT=/content/drive/MyDrive/MSc-RAG`.

Raw store: `results/raw/phase15_benchmark/{run_id}/` (separate from Phase 14's `phase14_benchmark/`).

## Recovery

- Incremental JSONL after each case
- Checkpoint to Google Drive during the run
- Resume by `{architecture}:{question_id}`; skip completed; retry genuine failures
- Refuse overwrite of an existing raw store
- Progress logs (completed / failed / pending)
- Preserve raw results and logs
- Completion summary requires phase=15, n_questions=140, n_cases=420, T=0.65, 420 unique keys on PASS

Do **not** start 420 from this documentation. Push to GitHub first, then run the Colab notebook.
