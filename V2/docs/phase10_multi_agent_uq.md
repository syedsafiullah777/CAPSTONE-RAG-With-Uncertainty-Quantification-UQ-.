# Phase 10 — Multi-Agent RAG + UQ / abstention

Architecture id: **`multi_agent_uq`** (third independent pipeline for RQ2/RQ3).

## Pipeline

1. **Retrieve** — shared Phase 6 KB (same top_k, embeddings, collection)
2. **Draft** — Qwen3-8B generation from evidence
3. **Verify** — lexical overlap + LLM support score (Phase 9)
4. **UQ** — combined confidence = mean(retrieval_score, verification_score)
5. **Gate** — `ANSWER` if confidence ≥ threshold else `ABSTAIN`

## Confidence

| Signal | Source |
| --- | --- |
| Retrieval | Mean of top-k similarity scores |
| Verification | Phase 9 `verification_score` |
| Combined | `mean_retrieval_verification` (no self-consistency) |

## Abstention

- **ANSWER:** return draft answer
- **ABSTAIN:** return configured abstention message; draft preserved in `configuration.draft_answer`

## Threshold

- **Smoke / notebook:** `uncertainty.smoke_threshold` (default **0.55**) — **not** the locked benchmark threshold
- **Final benchmark:** locked on FinQA **dev** calibration set only (Phase 14); never tuned on the frozen 140 test set

## Smoke

```bash
PYTHONPATH=. python scripts/smoke_multi_agent_uq.py --backend mock --limit 3
PYTHONPATH=. python scripts/smoke_multi_agent_uq.py --backend llama_cpp --limit 3
```

Colab: `notebooks/colab_phase10_smoke.ipynb`

## Out of scope

- Self-consistency sampling (V1 lesson: high cost, low variance)
- Warning tier (V2 uses binary ANSWER | ABSTAIN)
- Threshold calibration on test set
