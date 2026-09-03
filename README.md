# Multi-Agent RAG with Uncertainty Quantification

MSc Artificial Intelligence capstone project by Syed Safiullah.

This repository is the final V2 implementation. It compares three retrieval-augmented generation (RAG) architectures on frozen FinQA questions from T²-RAGBench, with uncertainty quantification and confidence-based abstention.

## Architecture overview

Shared retrieval (BAAI/bge-small-en-v1.5, Chroma, cosine distance, top-k = 4) feeds one of:

| Architecture | Pipeline |
| --- | --- |
| Single-Agent RAG | Retriever → Qwen3-8B |
| Multi-Agent RAG | Retriever → Qwen3-8B draft → verification |
| Multi-Agent RAG + UQ | Retriever → draft → verification → confidence → ANSWER or ABSTAIN |

UQ confidence is the mean of the retrieval score and the verification score. The locked abstention threshold is **T = 0.65**, selected on 40 separate DEV questions and not tuned on the frozen TEST set.

Official generation used Qwen3-8B (Q4_K_M) with `llama_cpp` on a Google Colab Tesla T4. The Streamlit app runs the same three pipelines; it does not look up frozen benchmark answers for new questions.

## Repository structure

```text
V2/
  app/                 Streamlit live artefact
  src/                 RAG, retrieval, evaluation, statistics
  config/              Experiment and prompt configuration
  scripts/             CLI entrypoints
  data/                Frozen 140 TEST and 40 DEV question files
  results/             Canonical evaluation artefacts (Phases 15–18)
  notebooks/           Colab launchers, including the final live demo
  project_record/      Project record and validation evidence
  tests/               Unit and static checks
  requirements.txt
README.md
.gitignore
```

## Technologies

Python, Streamlit, Chroma, sentence-transformers (BAAI/bge-small-en-v1.5), Qwen3-8B via `llama_cpp` (official GPU path), pytest.

## Launch the live artefact

```bash
cd V2
PYTHONPATH=. streamlit run app/streamlit_app.py
```

Install dependencies first (`python -m venv .venv`, then `pip install -r requirements.txt` from `V2/`). A local mock backend can exercise the UI. Official Qwen3-8B answers require a CUDA GPU runtime and the GGUF weights; those weights are not stored in this repository.

## Reproducibility

1. Frozen TEST set: `V2/data/final/selected_140_questions.csv` (140 questions).
2. DEV calibration set: `V2/data/calibration/calibration_questions.csv` (40 questions).
3. Locked threshold: `V2/results/config/threshold.lock.json` (T = 0.65).
4. Official Colab notebooks live under `V2/notebooks/` (full benchmark: `colab_phase15_full_benchmark.ipynb`; judge: `colab_phase16_judge.ipynb`; live demo: `colab_phase21_final_live_demo.ipynb`).
5. Source PDFs and the Chroma index are large generated artefacts and are not committed. Rebuild locally with `V2/scripts/build_index.py` if reproducing retrieval from documents.

Do not regenerate the frozen Phase 15–18 result files for inspection of the submitted experiment.

## Canonical evaluation artefacts

The official TEST evaluation is **140 questions × 3 architectures = 420** architecture–question cases, plus a separate **420-case** post-hoc LLM-as-judge faithfulness pass (custom / RAGAS-inspired; not the official RAGAS library).

| Artefact | Path |
| --- | --- |
| Benchmark summary | `V2/results/config/phase15_benchmark_summary.json` |
| CPU-scored cases | `V2/results/processed/phase16_cases.jsonl` |
| Judge summary | `V2/results/metrics/phase16_judge_summary.csv` |
| Statistics | `V2/results/metrics/phase17_tests.csv` |
| Error analysis | `V2/results/final/phase18_error_analysis.md` |
| Dissertation mapping | `V2/project_record/PROJECT_MASTER_RECORD.md` |

## Mapping to the dissertation

| Topic | Location |
| --- | --- |
| Single-Agent RAG | `V2/src/rag/single_agent.py` |
| Multi-Agent RAG | `V2/src/rag/multi_agent.py`, `V2/src/rag/verification.py` |
| Multi-Agent + UQ | `V2/src/rag/multi_agent_uq.py`, `V2/src/rag/uncertainty.py` |
| Retrieval | `V2/src/retrieval/` |
| Prompts | `V2/config/prompts.yaml`, `V2/src/rag/prompts.py` |
| Streamlit artefact | `V2/app/streamlit_app.py` |
| Evaluation / judge | `V2/src/evaluation/` |
| Statistics | `V2/src/statistics/` |

## Notes

This repository contains the author’s submitted MSc project code and frozen evaluation artefacts.

Model weights (Qwen GGUF), Hugging Face caches, and the built Chroma document index are not included. The custom judge is not official RAGAS. The repository does not claim that Multi-Agent RAG significantly improved numeric accuracy, that UQ universally improves accuracy, or that UQ confidence is a calibrated probability.
