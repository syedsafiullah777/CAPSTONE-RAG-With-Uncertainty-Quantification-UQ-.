# Phase 11 — Streamlit live artefact

Single live application that runs the three completed RAG architectures on the same original question.

## Entrypoint

```bash
cd V2
PYTHONPATH=. streamlit run app/streamlit_app.py
```

Backend options in the sidebar: `mock` (local UI check), `ollama_dev` (local Qwen smoke), `llama_cpp` (Colab T4).

## Behaviour

- Fresh user question **or** a frozen FinQA test case (read-only)
- Independent runs: Single-Agent, Multi-Agent, Uncertainty/Abstention
- Shared Phase 6 knowledge base and one loaded LLM backend
- **Not** a precomputed benchmark lookup
- Does **not** rebuild the knowledge base
- Does **not** modify the frozen 140 / calibration 40 sets

Failed retrieval or generation is shown as **ERROR** / **UNAVAILABLE** (not ANSWER). The live layer clears fabricated answers and confidence. Mock is for UI/testing only.

## Displayed per architecture

- retrieved evidence, scores, and metadata
- generated answer
- verification (n/a for Single-Agent)
- confidence, threshold, ANSWER/ABSTAIN decision
- latency / backend / device

## Smoke

```bash
PYTHONPATH=. python scripts/smoke_live_artefact.py --backend mock
```

Runs one frozen question (`finqa_test_1000`) and one fresh question through all three pipelines.

**Phase 20 (final examiner demo):** the Streamlit app now always uses **locked T=0.65**. Sidebar pages: Live RAG Demo, Benchmark Results, Benchmark Questions. See `docs/phase20_live_artefact.md`. Do not treat Phase 11 smoke 0.55 runs as the final live artefact.
