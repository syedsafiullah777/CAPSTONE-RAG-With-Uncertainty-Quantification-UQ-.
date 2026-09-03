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
  notebooks/           Final V2 Colab notebooks (see below)
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
4. Final notebooks and CPU scripts are listed under **Final V2 notebooks and analysis**.
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
| Judge summary (JSON) | `V2/results/config/phase16_judge_summary.json` |

Frozen TEST metrics (n = 140 per architecture; not a claim of Multi-Agent or universal UQ accuracy improvement): Single-Agent displayed correctness 32/140; Multi-Agent 29/140; UQ displayed 32/140; UQ claim 34/140; UQ coverage 78/140 (55.71%); UQ selective accuracy 32/78 (41.03%). RQ1 McNemar SA vs MA displayed correctness p = 0.6776 (not significant). RQ3 McNemar MA vs UQ unsupported-emitted p = 9.21572e-19. UQ confidence vs judge faithfulness Spearman ρ = 0.6988 (Holm p = 2.40335e-21). MA vs UQ full-set faithfulness Wilcoxon p = 0.4032 (not significant).

## Development and Evaluation Phases

| Phase | Purpose | Status | Main output / evidence |
|------|---------|--------|-------------------------|
| 1 | V2 project foundation: repository structure, configuration and tests | Complete | V2 tree, YAML/configuration, tests |
| 2 | V1 audit and FinQA dataset profiling | Complete | FinQA profile and V1 audit |
| 3 | Source-PDF verification | Complete | PDF verification/probe, 380/380 verified |
| 4 | Freeze final 140-question TEST set | Complete | Frozen TEST CSV, sampling manifest, seed 42 |
| 5 | Freeze 40-question DEV calibration set | Complete | Frozen DEV calibration CSV and manifest, seed 42 |
| 6 | Build the final knowledge base | Complete | 230 source documents / 1239 chunks |
| 7 | Establish Qwen backend and runtime configuration | Complete | Qwen3-8B / llama_cpp runtime and fingerprints |
| 8 | Implement and smoke-test Single-Agent RAG baseline | Complete | Single-Agent implementation and smoke evidence |
| 9 | Implement and smoke-test Multi-Agent RAG with verification | Complete | Multi-Agent implementation and smoke evidence |
| 10 | Implement and smoke-test Multi-Agent RAG with UQ and abstention | Complete | UQ implementation and smoke evidence |
| 11 | Develop the live application interface | Complete | Streamlit application plumbing / live UI development |
| 12 | Run controlled pilot evaluation | Complete | 18-case pilot evidence |
| 13 | Calibrate and lock the research confidence threshold | Complete | threshold.lock.json, T = 0.65 |
| 14 | Perform engineering validation before the official benchmark | Complete | 9-case validation; engineering evidence only |
| 15 | Run the official 420-case architecture benchmark | Complete | 420/420 official benchmark; 140 cases per architecture |
| 16 | Process benchmark results and run the separate post-hoc judge | Complete | 420 CPU evaluation rows and 420 judge rows |
| 17 | Perform statistical analysis and generate final figures | Complete | Statistical tests, assumptions, effect sizes and six canonical figures |
| 18 | Perform qualitative error analysis | Complete | Error taxonomy, 420-case population analysis and 81-case qualitative sample |
| 19 | Perform reproducibility and artefact audit | Complete | Reproducibility audit, artefact manifest and integrity checks |
| 20 | Validate the final live Streamlit artefact | Complete | Three live pipeline pages with evidence, verification, confidence, decision and runtime |
| 21 | Provide the canonical final live-demo launcher and final static audit | Complete | Final live-demo notebook and static validation |

Phases 15–16 constitute the official quantitative evaluation: Phase 15 contains the 420 architecture evaluations and Phase 16 contains the corresponding CPU processing and separate 420-case post-hoc LLM-as-judge evaluation. Phases 17–19 are implemented as scripts and result artefacts rather than notebooks. Phase 20 is the final Streamlit artefact, while Phase 21 provides the canonical final live-demo launcher and final static validation. Earlier Phase 7–10, 12 and 14 notebooks are retained as historical engineering, smoke, pilot or validation evidence and are not the official 420-case evaluation.

## Final V2 notebooks and analysis

Notebooks are stored in `V2/notebooks/` under their original phase names. Phases 17–19 were implemented as CPU scripts over frozen artefacts; they were never Colab notebooks, and none have been invented here.

Official final evaluation:

- **Phase 15** = official 420-case RAG benchmark
- **Phase 16** = official 420-case post-hoc LLM-as-judge

Earlier notebooks (`colab_phase7–10_smoke.ipynb`, `colab_phase12_pilot.ipynb`, `colab_phase14_benchmark_validation.ipynb`) are **historical engineering**: smoke tests, a 6-question pilot, and a 9-case runner validation. They are retained as development evidence and are **not** the official 420-case evaluation.

Large raw JSONL dumps, Qwen GGUF weights, and the built Chroma index are intentionally not tracked on GitHub. Inspect official summaries and scored tables instead of regenerating Phase 15–16.

| Phase | Role | Location |
| --- | --- | --- |
| 15 | Official 420-case RAG benchmark (Colab T4) | `V2/notebooks/colab_phase15_full_benchmark.ipynb` |
| 16 | Official 420-case post-hoc LLM-as-judge | `V2/notebooks/colab_phase16_judge.ipynb` |
| 17 | Final statistics and canonical figures | `V2/scripts/run_statistics.py`, `V2/scripts/render_phase17_figures.py`, `V2/results/metrics/phase17_*` |
| 18 | Final error analysis | `V2/scripts/run_error_analysis.py`, `V2/results/final/phase18_error_analysis.md` |
| 19 | Final reproducibility audit | `V2/scripts/run_reproducibility_audit.py`, `V2/results/final/phase19_artefact_manifest.md` |
| 20 | Live Streamlit artefact validation | `V2/app/streamlit_app.py`; GPU demo notebook `V2/notebooks/colab_phase11_live.ipynb` |
| 21 | Canonical live-demo launcher | `V2/notebooks/colab_phase21_final_live_demo.ipynb` |

The Phase 15 and 16 notebooks launched the official GPU jobs and do not replace the frozen result files. The Phase 21 notebook starts the Streamlit app on Colab; it does not rerun the benchmark, judge, or statistics. Inspection of Phases 17–19 uses the saved tables and reports, not a new experiment.

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
