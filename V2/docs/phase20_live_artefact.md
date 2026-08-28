# Phase 20 — Final live artefact and reproducibility validation

Official live demonstration of the three V2 RAG architectures on Colab T4 with Qwen3-8B (`llama_cpp`). **Does not rerun the 420-case benchmark, calibration, judge, or statistics. Does not modify T=0.65 or the frozen 140/40.**

## Entrypoint

```bash
cd V2
PYTHONPATH=. streamlit run app/streamlit_app.py
```

Official GPU demo: `notebooks/colab_phase11_live.ipynb` (same Streamlit app; locked T=0.65). Do not open `127.0.0.1:8501` on the Mac for the examiner demo.

## Locked threshold

The live artefact always applies **T = 0.65** from `results/config/threshold.lock.json` (FinQA DEV 40 only). The sidebar smoke 0.55 control has been removed.

## Required live checks

1. Known-good frozen FinQA question `finqa_test_1000`
2. Fresh knowledge-base question (Snap-on 2013 own TSR — not in the frozen 140)
3. Insufficient-evidence question (SpaceX FY2025) — UQ must be able to **ABSTAIN** under the locked rule
4. All three architectures independently on the same original question

## Smoke / demo CLI

```bash
PYTHONPATH=. python scripts/run_live_demo.py --backend mock          # plumbing only
PYTHONPATH=. python scripts/run_live_demo.py --backend llama_cpp     # Colab T4
```

Writes `results/config/phase20_live_demo_summary.json`. Official PASS requires Colab CUDA + llama_cpp.

## App pages

Sidebar navigation:

1. **Live RAG Demo** — three architectures, locked T=0.65, shared Phase 6 KB (unchanged).
2. **Benchmark Results** — read-only frozen Phase 16/17 metric tables. Does not rerun experiments or load per-question system answers.
3. **Benchmark Questions** — read-only catalogue of the frozen 140 FinQA test questions (`data/final/selected_140_questions.csv` only). Search, company filter, pagination (20 per page). **Use this question in Live Demo** copies question text only; it does not copy FinQA gold or Phase 15 answers.

The Benchmark Questions page does not run RAG or call Qwen3-8B.

## UQ confidence warning (UI-only)

The research decision rule is unchanged: **confidence < 0.65 → ABSTAIN**; **confidence ≥ 0.65 → ANSWER**.

The Multi-Agent + UQ live panel may show extra captions:

- ABSTAIN → `ABSTAIN — Low confidence`
- ANSWER with confidence still in the same 0.65 hundredths band as the lock → `Moderate confidence — verify supporting evidence.`
- ANSWER clearly above that band → ANSWER with no extra warning
- missing confidence → `n/a`, no warning

This is a **user-facing indicator**. It is **not** a second calibrated research threshold, is **not** stored in `threshold.lock.json`, and does **not** change stored decisions, confidence, Phase 15–18 results, or statistics.
