# Phase 16 — Evaluation metrics (CPU)

Score the **saved** Phase 15 420-case JSONL. No RAG rerun. No Qwen3-8B generation. No GPU.

## Input (sole)

| Item | Value |
| --- | --- |
| Raw JSONL | `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` |
| SHA-256 | `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` |
| Cases | **420** unique keys (140 × 3) |
| Threshold | **T = 0.65** (read-only lock; not retuned) |
| Gold | Frozen FinQA **test** 140 `program_answer` |

## Why CPU

Official RAGAS LLM-as-judge would need Qwen/GPU. `experiment.yaml` keeps `judge_model: null`. Phase 16 uses:

- numeric match (`rel_tol=0.01`) for answer correctness
- `token_overlap` for faithfulness (CPU proxy; **not** official RAGAS)
- gold `file_name` / `context_id` for context precision and recall
- saved `verification_score` where Phase 15 already computed it (not recomputed)

## Metrics

| Metric | Definition |
| --- | --- |
| `answer_correctness` | Numeric match of the **displayed** answer to `program_answer` |
| `answer_correctness_claim` | Same match on the UQ **draft** (or displayed answer) |
| `faithfulness` | Token-overlap of the claim vs concatenated retrieved chunk text |
| `context_precision` | Fraction of top-k chunks matching gold file or `context_id` |
| `context_recall` | 1 if any chunk matches gold file or `context_id` |
| `context_recall_numeric` | 1 if the gold number appears in the evidence text |
| `selective_accuracy` | Displayed numeric accuracy among **ANSWER** only |
| `coverage` / `abstention_rate` | From `decision` |
| `unsupported_emitted_rate` | ANSWER **and** failed displayed numeric match (not a hallucination label) |

UQ ABSTAIN replaces the displayed answer with the abstention template. Use `answer_correctness_claim` for the draft that would have been emitted.

## Command

```bash
cd V2
PYTHONPATH=. python scripts/run_evaluation.py
```

Refuses to overwrite `results/processed/phase16_cases.jsonl` unless `--force`. Does not import architecture runners or `llama_cpp`.

## Outputs

| Artefact | Path |
| --- | --- |
| Processed cases | `results/processed/phase16_cases.jsonl` |
| By-architecture JSON | `results/metrics/phase16_by_architecture.json` |
| Summary CSV | `results/metrics/phase16_summary.csv` |
| Summary markdown | `results/metrics/phase16_summary.md` |
| Evaluation summary | `results/config/phase16_evaluation_summary.json` |

## What this phase does not do

- Does **not** rerun Single-Agent, Multi-Agent, or Multi-Agent + UQ
- Does **not** call Qwen3-8B or load GGUF
- Does **not** modify the frozen 140/40 CSVs or `threshold.lock.json`
- Does **not** run Phase 17 statistical tests
- Does **not** claim official RAGAS LLM metrics

Observed numbers: `project_record/evidence/phase16_validation.md`.

## Post-hoc LLM-as-judge (separate job; 420 Colab not launched from docs)

See `docs/phase16_judge.md`.

- Entrypoint: `scripts/run_judge.py`
- Notebook: `notebooks/colab_phase16_judge.ipynb`
- Label: **LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)** — not official RAGAS
- Token-overlap remains the secondary lexical metric
- Numeric answer correctness and context P/R stay CPU-only
- Official command (Colab GPU only): `PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp`
