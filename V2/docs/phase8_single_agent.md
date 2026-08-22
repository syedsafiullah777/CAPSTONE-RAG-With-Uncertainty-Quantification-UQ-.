# Phase 8 — Single-Agent RAG baseline

## Objective

Baseline RAG: retrieve from the Phase 6 source-PDF knowledge base, generate with Qwen3-8B backend, return evidence + answer using the common raw-result schema.

## What is included

- `src/rag/schema.py` — `RAGCaseResult` aligned with `storage.raw_result_fields`
- `src/rag/prompts.py` — baseline prompt from `config/prompts.yaml`
- `src/rag/single_agent.py` — retrieve → prompt → generate
- `scripts/smoke_single_agent.py` — small-N validation on frozen questions

## What is not included

- Multi-Agent RAG (Phase 9)
- Uncertainty / abstention (Phase 10)
- Full 420-case benchmark
- Changes to frozen 140 / calibration 40

## Smoke command

```bash
cd V2
source .venv/bin/activate
# Local smoke (optional):
PYTHONPATH=. python scripts/smoke_single_agent.py --backend ollama_dev --limit 3
# Colab GPU (primary):
PYTHONPATH=. python scripts/smoke_single_agent.py --backend llama_cpp --limit 3
```

## Artefacts

| File | Role |
| --- | --- |
| `results/config/phase8_single_agent_smoke.json` | Case results |
| `results/config/phase8_smoke_test.json` | Validation record |
| `results/config/phase8_runtime_fingerprint.json` | Runtime fingerprint |
| `project_record/evidence/phase8_validation.md` | Evidence summary |
