# Phase 21 — Canonical final live-demo launcher (Colab)

**Not a new research experiment.** This notebook only launches the already-completed Streamlit live artefact for the MSc viva.

Canonical notebook: `notebooks/colab_phase21_final_live_demo.ipynb`

Historical live notebooks (`notebooks/colab_phase11_live.ipynb` and earlier) remain development/validation evidence. Do not use them as the viva launcher.

## What this notebook does

1. Clone or pull V2 from GitHub (`main`; historical Colab clones used a previous development workspace).
2. Mount Google Drive and restore `MyDrive/MSc-RAG/artifacts/knowledge_base/` into `V2/knowledge_base/`.
3. Verify the Chroma collection is non-empty and matches the Phase 6 manifest chunk count.
4. Verify CUDA, Tesla T4, Qwen3-8B Q4_K_M, and `llama_cpp`. Refuse Darwin/CPU/mock/Ollama.
5. Start `app/streamlit_app.py` on the Colab VM (port 8501).
6. Print and embed the Colab `proxyPort(8501)` browser URL.
7. Keep Streamlit alive for manual viva use.

## What this notebook does not do

- Rerun the 420-case benchmark, calibration, LLM-as-judge, or statistics
- Call `scripts/run_live_demo.py`, `run_full_benchmark.py`, `run_calibration.py`, `run_judge.py`, or `run_statistics.py`
- Modify frozen 140/40, **T = 0.65**, Phase 15–18 results, V1, or RAG architectures
- Fall back to mock or Ollama
- Ask the examiner to open `127.0.0.1:8501` on the Mac
- Rebuild the knowledge base with `build_index.py`

## Launch command (Colab VM, from `V2/`)

```bash
PYTHONPATH=. python -m streamlit run app/streamlit_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true
```

Environment: `V2_LIVE_BACKEND=llama_cpp`, `V2_FORBID_MOCK=1`, `V2_REQUIRE_CUDA=1`.

## Browser URL

`google.colab.kernel.proxyPort(8501)` via `eval_js`. The notebook also embeds an iframe with `output.serve_kernel_port_as_iframe(8501)`. Open **only** that Colab proxy URL.

## Streamlit pages (existing app)

- **Live RAG Demo** — fresh question; three architectures; evidence/scores; answer; verification; UQ; locked T=0.65; ANSWER/ABSTAIN; UI-only near-threshold warning; runtime/GPU; ERROR/UNAVAILABLE
- **Benchmark Results** — read-only saved Phase 16/17 tables
- **Benchmark Questions** — read-only frozen 140 catalogue. **Use this question in Live Demo** copies question text only and navigates via a pending-page callback applied before the sidebar `app_page` radio (does not assign `st.session_state["app_page"]` after that widget exists).

## Research lock (unchanged)

Research decision: confidence < 0.65 → ABSTAIN; confidence ≥ 0.65 → ANSWER. Locked **T = 0.65**.
