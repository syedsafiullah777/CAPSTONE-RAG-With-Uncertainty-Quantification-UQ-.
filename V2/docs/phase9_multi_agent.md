# Phase 9 — Multi-Agent RAG

**Status:** complete (smoke validated)

## Architecture

Retrieve (Phase 6 KB) → **draft** (generation agent) → **verify** (support scoring agent).

- Architecture id: `multi_agent`
- Reuses: same retriever, embeddings, top_k, Qwen3-8B backend as Phase 8
- `verification_result`: lexical overlap + LLM support score (average)
- `confidence`: verification score (not combined UQ — Phase 10)
- `decision`: always `ANSWER` (no abstention in Phase 9)
- `threshold`: null until Phase 10 calibration

## Smoke

```bash
cd V2
PYTHONPATH=. python scripts/smoke_multi_agent.py --backend mock --limit 3
```

Colab: reuse Phase 8 KB setup, then run with `--backend llama_cpp`.

## Out of scope (Phase 10)

- Self-consistency
- Combined confidence / abstention
- Threshold locking
