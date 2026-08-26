# V2 — New Development Implementation

Clean development area for the revised MSc AI capstone artefact.

**Phase status:** Phase 13 calibration runner complete (official T lock NEEDS VERIFICATION). See `project_record/PROJECT_MASTER_RECORD.md`.

## Storage / backup

GitHub = source · Colab = compute · Drive `MSc-RAG/` = persistent results · Mac = dev/backup  

Details: `docs/storage_backup_recovery.md` · Plan: `docs/IMPLEMENTATION_PLAN.md`

## What this folder is

A controlled research prototype comparing three RAG architectures over a financial document corpus (T²-RAGBench FinQA), with uncertainty quantification and confidence-based abstention.

V1 (everything outside `V2/`) is **reference-only** and must not be modified as part of V2 work.

## Research questions

1. Does Multi-Agent RAG improve answer accuracy vs Single-Agent RAG on a financial corpus?
2. Does uncertainty quantification reduce hallucinated/unsupported responses in Multi-Agent RAG?
3. Does confidence-based abstention improve reliability when supporting evidence is insufficient?

## Layout

```text
V2/
├── config/           experiment + prompt YAML
├── src/              Python package (foundation in Phase 1)
├── app/              Streamlit live artefact (`streamlit_app.py`)
├── scripts/          CLI entrypoints (later)
├── data/             raw / processed / calibration / final
├── knowledge_base/   documents + vector index (later)
├── results/          raw / processed / final / checkpoints / logs / config
├── tests/
├── docs/
├── PROJECT_CONTEXT.md
├── DECISIONS.md
└── requirements.txt
```

## Setup (Phase 1)

From the `V2/` directory:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

## Live artefact (Phase 11)

```bash
PYTHONPATH=. streamlit run app/streamlit_app.py
```

Uses the existing Phase 6 knowledge base and the three V2 RAG pipelines. Sidebar backend: `mock` (UI check), `ollama_dev` (local Qwen), `llama_cpp` (Colab GPU).

## Pilot (Phase 12)

```bash
PYTHONPATH=. python scripts/run_pilot.py --backend mock
# Colab T4:
# notebooks/colab_phase12_pilot.ipynb
# PYTHONPATH=. python scripts/run_pilot.py --backend llama_cpp
# After disconnect:
# PYTHONPATH=. python scripts/run_pilot.py --backend llama_cpp --resume-latest
```

6 frozen questions × 3 architectures = 18 cases. Threshold `0.55` smoke/demo — **NOT LOCKED**. Does not run the 420-case benchmark.

## Calibration (Phase 13)

```bash
PYTHONPATH=. python scripts/run_calibration.py --backend mock --n-questions 3
# Colab T4 (official lock):
# notebooks/colab_phase13_calibration.ipynb
```

Uses the frozen FinQA **dev** 40 only. Mock cannot write `threshold.lock.json`.

Import check:

```bash
PYTHONPATH=. python -c "from src.config import load_experiment_config; print(load_experiment_config().get('project', 'name'))"
```

## Compute note

Final Qwen3-8B inference and the 420-case benchmark target **standard Google Colab GPU notebooks** (not Colab CLI / gcloud). Primary Phase 7 entrypoint: `notebooks/colab_phase7_smoke.ipynb`. The local Mac is for development and control only. No paid LLM API is required.

## Not in Phase 1

Dataset sampling, knowledge base, retrieval, Qwen inference, RAG architectures, Streamlit, benchmark runner, evaluation, and statistics are implemented in later approved phases.
