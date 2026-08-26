# Phase 14 — 9-case engineering validation (complete) and next 420-case execution

The 9-case run is **finished**. Keep it as **supporting engineering evidence**. Do **not** run another 3-question / 9-case validation.

## Completed 9-case engineering validation

| Item | Local mock | Colab T4 |
| --- | --- | --- |
| Status | PASS (after retry) | **PASS** |
| Run ID | `phase14_20260826T195616Z_f9550cce` | `phase14_20260826T200828Z_e91e588d` |
| Backend | mock | `llama_cpp` |
| GPU | — | Tesla T4 |
| Model | mock | Qwen3-8B Q4_K_M |
| Cases | 9 | 9 |
| T | 0.65 LOCKED | 0.65 LOCKED |

Colab subset: `finqa_test_1000`, `1012`, `1017` × three independent architectures. UQ: 2 ANSWER + 1 ABSTAIN (`finqa_test_1000`, confidence 0.5032 < 0.65).

## Next execution — final 420-case benchmark (not launched)

**140 frozen test questions × 3 architectures = 420 cases.**

| Item | Value |
| --- | --- |
| Eval set | Frozen FinQA **test** 140 (`data/final/selected_140_questions.csv`) |
| Architectures | `single_agent`, `multi_agent`, `multi_agent_uq` (independent; no chaining) |
| Threshold | **T = 0.65** from `results/config/threshold.lock.json` |
| Model | Qwen3-8B **Q4_K_M** |
| Backend | `llama_cpp` |
| Compute | Google Colab GPU |
| Knowledge base | Shared Phase 6 (230 PDFs / 1239 chunks) |
| Retrieval | Identical across architectures (`top_k=4`, `BAAI/bge-small-en-v1.5`) |

### Required run behaviour

- Incremental raw JSONL after each case
- Checkpoint to Google Drive during the run
- Resume after Colab disconnect (`--resume-latest`); never restart from question 1
- Retry genuine failures; skip completed `{architecture}:{question_id}`
- Duplicate prevention; refuse silent overwrite of raw results
- Progress monitoring (completed / failed / pending)
- Preserve raw results and logs

### Must not

- Modify the frozen 140-question test set
- Modify the 40-question calibration set
- Recalibrate or change T
- Modify V1
- Add another mandatory 9-case validation
- Start the 420-case run automatically from documentation updates

This file does **not** launch 420.
