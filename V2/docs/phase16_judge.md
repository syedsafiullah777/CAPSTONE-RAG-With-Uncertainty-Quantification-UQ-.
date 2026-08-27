# Phase 16 — Post-hoc LLM-as-judge faithfulness

Separate scoring job over the **frozen Phase 15** 420-case JSONL.

This is **not** a RAG rerun. It does **not** replace Phase 16 CPU metrics.

## Three layers (do not collapse)

1. **Phase 15** generated 140 × 3 = 420 RAG cases (Qwen3-8B, Colab T4).
2. **Phase 16 CPU** scored those saved cases (numeric correctness, context P/R, token-overlap, abstention metrics).
3. **Phase 16 judge** (this job) scores faithfulness of the **same saved claims** against **saved retrieved evidence**.

## Metric label (exact)

`LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)`

**Not official RAGAS Faithfulness.** Not the RAGAS library.

## Input (per saved case)

- `question`
- `retrieved_evidence[].text`
- claim:
  - Single-Agent / Multi-Agent: displayed `answer`
  - UQ: `configuration.draft_answer` (not the abstention template)

Do **not** provide FinQA gold `context` or the gold answer to the judge.

## Judge settings

| Item | Value |
| --- | --- |
| Model | Qwen3-8B Q4_K_M |
| Backend | `llama_cpp` |
| Compute | Colab GPU (one model instance) |
| n_ctx | 4096 |
| temperature | 0.0 |
| max_new_tokens | 32 |
| Cases | **420** |

## Command (official — do not run from this Mac)

```bash
cd V2
PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp
# After disconnect:
PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp --resume-latest
```

Local mock smoke only:

```bash
PYTHONPATH=. python scripts/run_judge.py --backend mock --n-cases 3 --no-drive-sync
```

Mock cannot run n=420.

## Storage

| Artefact | Path |
| --- | --- |
| Judge JSONL | `results/raw/phase16_judge/{run_id}/judge.jsonl` |
| Checkpoint | `results/checkpoints/phase16_judge/{run_id}.json` |
| Summary CSV | `results/metrics/phase16_judge_summary.csv` (written after official 420 PASS) |
| Drive | `MyDrive/MSc-RAG/results/raw/phase16_judge/` |

Phase 15 `cases.jsonl` and Phase 16 `phase16_cases.jsonl` are **not** overwritten.

Notebook: `notebooks/colab_phase16_judge.ipynb`
