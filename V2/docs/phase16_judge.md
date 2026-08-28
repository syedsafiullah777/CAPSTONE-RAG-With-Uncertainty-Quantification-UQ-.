# Phase 16 — Post-hoc LLM-as-judge faithfulness

Separate scoring job over the **frozen Phase 15** 420-case JSONL.

This is **not** a RAG rerun. It does **not** replace Phase 16 CPU metrics.

**Official 420-case status (verified 2026-08-28):** **PASS**. Earlier docs (2026-08-27) recorded this job as **not launched** / **NEEDS VERIFICATION**. That implementation state is superseded by the Colab run below. Do not rerun.

## Three layers (do not collapse)

1. **Phase 15** generated 140 × 3 = 420 RAG cases (Qwen3-8B, Colab T4).
2. **Phase 16 CPU** scored those saved cases (numeric correctness, context P/R, token-overlap, abstention metrics).
3. **Phase 16 judge** (this job) scores faithfulness of the **same saved claims** against **saved retrieved evidence**.

## Metric label (exact)

`LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)`

**Not official RAGAS Faithfulness.** Not the RAGAS library.

## Official run (locally verified)

| Item | Value |
| --- | --- |
| Run ID | `phase16_judge_20260828T152623Z_06661255` |
| Status | **PASS** (Colab ended 2026-08-28T15:39:49Z) |
| Completeness | 420/420 unique keys; 140 per architecture; 0 duplicates; 0 missing; 0 errors; 0 parse failures; all COMPLETED |
| Backend / model | `llama_cpp`; Qwen3-8B Q4_K_M; Tesla T4 |
| Source Phase 15 SHA-256 | `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` (unchanged) |
| `used_rag_rerun` | `false` |
| Gold context / gold answer | not supplied |
| UQ claim | `configuration.draft_answer` (140 rows); UQ 78 ANSWER / 62 ABSTAIN |
| `judge.jsonl` SHA-256 | `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3` |

Observed means (4 d.p.; from official JSONL / `results/metrics/phase16_judge_summary.csv`):

| Architecture | All 140 | ANSWER only |
| --- | ---: | ---: |
| `single_agent` | 0.3241 | 0.3241 |
| `multi_agent` | 0.3484 | 0.3484 |
| `multi_agent_uq` | 0.3749 | **0.6548** (78 cases) |

## Input (per saved case)

- `question`
- `retrieved_evidence[].text`
- claim:
  - Single-Agent / Multi-Agent: displayed `answer`
  - UQ: `configuration.draft_answer` (not the abstention template)

Do **not** provide FinQA gold `context` or the gold answer to the judge.

## Judge-call settings (JSONL is source of truth)

Every official JSONL row records:

| Item | Value |
| --- | --- |
| Model | Qwen3-8B Q4_K_M |
| Backend | `llama_cpp` |
| Compute | Colab GPU (one model instance); Tesla T4 |
| n_ctx | 4096 |
| temperature | **0.0** |
| max_new_tokens | **32** |
| Cases | **420** |

Do **not** use `results/config/phase16_judge_runtime_fingerprint.json` `model_config` (`temperature=0.1`, `max_new_tokens=512`) as the judge-call settings. Those are experiment.yaml defaults captured in the fingerprint, not the post-hoc judge job.

## Command (official — do not re-run)

The official job has already **PASS**ed. Do not rerun from this Mac or Colab unless explicitly instructed.

```bash
cd V2
PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp
# After disconnect:
PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp --resume-latest
```

Local mock smoke only (not the official 420):

```bash
PYTHONPATH=. python scripts/run_judge.py --backend mock --n-cases 3 --no-drive-sync
```

Mock cannot run n=420.

## Storage

| Artefact | Path |
| --- | --- |
| Official judge JSONL | `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl` |
| Run-folder checkpoint / summary | same folder: `checkpoint.json`, `summary.json` |
| Checkpoint copy | `results/checkpoints/phase16_judge/phase16_judge_20260828T152623Z_06661255.json` |
| Summary CSV | `results/metrics/phase16_judge_summary.csv` |
| Log | `results/logs/phase16_judge_20260828T152554Z.log` |
| Drive (self-reported; **NEEDS VERIFICATION**) | `MyDrive/MSc-RAG/results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/` |

Phase 15 `cases.jsonl` and Phase 16 `phase16_cases.jsonl` are **not** overwritten.

Notebook: `notebooks/colab_phase16_judge.ipynb`

Phase 17 statistics (complete): `docs/phase17_statistics.md`. Do not rerun this judge job.
