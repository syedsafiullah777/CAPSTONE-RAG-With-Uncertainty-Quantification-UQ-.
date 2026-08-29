# Multi-Agent RAG with Uncertainty Quantification

This repository contains the **final V2 MSc AI project**.

**V2 is the canonical implementation.** Work from `V2/` (and `.cursor/rules/` for project constraints). Legacy root-level V1 code has been removed so the repository is not confused with an earlier prototype.

## Research design

The project compares three RAG architectures on the same frozen financial-document questions (T²-RAGBench → FinQA):

| Architecture | Role |
| --- | --- |
| Single-Agent RAG | Retriever → LLM |
| Multi-Agent RAG | Retriever → LLM → verifier |
| Multi-Agent RAG + UQ | Retriever → LLM → verifier → confidence → ANSWER / ABSTAIN |

Controlled constants (where scientifically appropriate): corpus, knowledge base, embeddings, retrieval configuration, top-k, LLM, generation settings, and evaluation configuration. The experimental variable is **RAG architecture**.

### Frozen evaluation set

| Item | Value |
| --- | --- |
| Final TEST set | 140 questions (`V2/data/final/selected_140_questions.csv`) |
| DEV calibration | 40 questions (`V2/data/calibration/calibration_questions.csv`) |
| Benchmark size | 140 questions × 3 architectures = **420** architecture-question cases |
| Locked abstention threshold | **T = 0.65** (`V2/results/config/threshold.lock.json`) |
| LLM | Qwen3-8B, Q4_K_M, `llama_cpp` |
| Official compute | Google Colab Tesla T4 |

The threshold was locked on DEV calibration data. It was not tuned on the frozen 140-question TEST set.

Results must be read from saved V2 artefacts. This README does not claim that Multi-Agent RAG significantly improved accuracy, or that uncertainty quantification universally improves accuracy. Answer-quality scoring uses a **custom, RAGAS-inspired judge**, not official RAGAS.

## Repository layout

```text
.cursor/rules/     project constraints (read-only reference for V2 work)
V2/                canonical project
.gitignore
README.md
```

Authoritative V2 locations:

| Purpose | Path |
| --- | --- |
| Source | `V2/src/` |
| Config / prompts | `V2/config/` |
| Dependencies | `V2/requirements.txt` |
| Streamlit live artefact | `V2/app/streamlit_app.py` |
| Final live-demo notebook | `V2/notebooks/colab_phase21_final_live_demo.ipynb` |
| Project record | `V2/project_record/PROJECT_MASTER_RECORD.md` |
| Frozen results | `V2/results/` (Phase 15–18 artefacts under raw / processed / metrics / analysis) |

## Setup

```bash
cd V2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Local CPU/UI checks can use the mock backend. Official Qwen3-8B inference is intended for a Colab GPU runtime (Tesla T4), not this Mac as the required compute path.

## Live demonstration

From `V2/`:

```bash
PYTHONPATH=. streamlit run app/streamlit_app.py
```

GPU demo notebook: `V2/notebooks/colab_phase21_final_live_demo.ipynb`.

## Reproducibility

Install and run from `V2/`. Do not regenerate frozen datasets, lock files, or Phase 15–18 results unless you are explicitly starting a new experiment. Historical V1 implementations (root `app/`, `evaluation/`, `rag/`, Ollama/qwen3.5, RAGBench sampling) have been removed from this repository.
