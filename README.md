# Multi-Agent RAG with Uncertainty Quantification

MSc Artificial Intelligence capstone project by Syed Safiullah.

This repository contains the final V2 implementation and evaluation artefacts for an MSc Artificial Intelligence capstone investigating whether evidence verification and uncertainty-aware abstention can improve the reliability of Retrieval-Augmented Generation (RAG) for financial-document question answering. The study compares a Single-Agent RAG baseline, a Multi-Agent RAG architecture with evidence verification, and a Multi-Agent RAG architecture with uncertainty quantification and confidence-based abstention under a shared retrieval configuration.

## Problem

RAG systems can retrieve relevant information yet still produce incorrect or insufficiently supported answers. This is particularly problematic for knowledge-intensive financial question answering, where numerical reasoning and evidence grounding matter. A system that always produces an answer can expose users to unsupported outputs when retrieved evidence is weak or when the generated reasoning is incorrect.

This project investigates whether adding agent-based evidence verification and an uncertainty-aware abstention mechanism can provide a more reliable response policy than a conventional single-agent RAG pipeline.

## Research Aim

This project aims to develop and test a Multi-Agent Retrieval-Augmented Generation (RAG) model that incorporates uncertainty quantification to enhance the reliability and factual grounding of enterprise knowledge systems, minimize hallucinations, and deliver confidence-based responses.

For the empirical evaluation, the enterprise-oriented problem is operationalised using financial-document question answering from the FinQA subset of T²-RAGBench, with source annual-report PDFs used as the knowledge base.

## Proposed Solution

The implemented pipelines progress as follows:

1. Retrieve evidence from a shared Chroma index (BAAI/bge-small-en-v1.5, cosine distance, top-k = 4).
2. Generate a draft answer with Qwen3-8B.
3. Optionally verify the draft against the retrieved evidence (Multi-Agent and UQ paths).
4. For UQ, combine retrieval and verification signals into a confidence score: the mean of the retrieval score and the verification score.
5. Apply the locked threshold **T = 0.65** to select **ANSWER** or **ABSTAIN**.

Abstention is a reliability mechanism rather than a claim that the model has determined the true probability that an answer is correct.

## Architectures

| Architecture | Pipeline | Purpose |
| --- | --- | --- |
| Single-Agent RAG | Retriever → Qwen3-8B | Baseline RAG system without explicit verification |
| Multi-Agent RAG | Retriever → Qwen3-8B draft → evidence verification | Tests whether explicit verification changes response reliability |
| Multi-Agent RAG + UQ | Retriever → draft → verification → confidence → ANSWER/ABSTAIN | Tests confidence-aware selective answering |

All three architectures use the same knowledge base, embedding model, retrieval configuration and primary generation model so that the architectural comparison is controlled. Official generation used Qwen3-8B (Q4_K_M) with `llama_cpp` on a Google Colab Tesla T4.

## Contribution

The contribution of the project is an implemented and experimentally evaluated RAG framework that integrates evidence verification and a simple uncertainty-based abstention policy within a controlled comparison of three architectures. The study contributes:

- a reproducible frozen TEST/DEV evaluation design;
- a comparison of single-agent, verified multi-agent and uncertainty-aware multi-agent RAG under shared retrieval controls;
- a confidence formulation combining retrieval and verification evidence;
- a DEV-calibrated abstention threshold applied without TEST-set tuning;
- statistical, qualitative and error-based analysis of where the architectures succeed and fail;
- a working Streamlit artefact that executes the implemented pipelines and exposes retrieved evidence, verification, confidence, decision and runtime.

## Evaluation Design

- Dataset family: T²-RAGBench, FinQA subset.
- Frozen TEST set: **140** FinQA test questions (sampling seed 42).
- Separate DEV calibration set: **40** FinQA development questions (seed 42).
- Architectures: **3**, evaluated independently on the same questions (no chaining).
- Official architecture–question evaluations: **140 × 3 = 420**.
- Separate post-hoc LLM-as-judge faithfulness pass: **420** cases (custom / RAGAS-inspired; not the official RAGAS library).
- Threshold **T = 0.65** locked from DEV only (`used_frozen_test_140 = false`).
- Shared retrieval: BGE-small embeddings, Chroma, cosine distance, top-k = 4.

The official quantitative evaluation is Phase 15 (420 architecture-question cases), followed by Phase 16 processing and a separate 420-case post-hoc LLM-as-judge faithfulness evaluation. Phases 17–19 analyse the frozen outputs rather than rerunning the benchmark.

## Key Findings

| Finding | Result |
| --- | --- |
| Single-Agent displayed correctness | 32/140 (22.86%) |
| Multi-Agent displayed correctness | 29/140 (20.71%) |
| UQ displayed correctness | 32/140 (22.86%) |
| UQ claim correctness | 34/140 (24.29%) |
| UQ coverage | 78/140 (55.71%) |
| UQ selective accuracy | 32/78 (41.03%) |
| SA vs MA displayed correctness | p = 0.6776, not significant |
| MA vs UQ unsupported-emitted | p = 9.21572e-19 |
| Confidence vs judge faithfulness | rho = 0.6988, Holm p = 2.40335e-21 |
| MA vs UQ full-set faithfulness | p = 0.4032, not significant |

The principal empirical finding is not a universal accuracy improvement. Instead, the UQ architecture substantially changes the response policy by abstaining on low-confidence cases and reducing unsupported emissions, while overall displayed accuracy remains similar to the baseline and Multi-Agent systems. The strong confidence–faithfulness association provides evidence of useful internal discrimination, but it should not be interpreted as proof of calibrated probabilities or universal performance improvement.

Unsupported-emitted is an operational reliability metric (an answer was emitted that does not match the gold numeric target). It is not a ground-truth hallucination rate. The repository does not claim that Multi-Agent RAG significantly improved numeric accuracy, that UQ universally improves accuracy, or that UQ confidence is a calibrated probability.

## Live Artefact and Google Colab GPU

The final live artefact is implemented in Streamlit and executes the three implemented RAG pipelines rather than serving as a static benchmark-results viewer.

### What the Streamlit app exposes

Pages:

- **Live RAG Demo** — one question through all three architectures independently; retrieved evidence and scores; generated answer; Multi-Agent verification; UQ confidence; locked **T = 0.65**; ANSWER/ABSTAIN; runtime/backend/GPU.
- **Benchmark Results** — read-only view of frozen Phase 16/17 metric tables.
- **Benchmark Questions** — read-only catalogue of the frozen 140 TEST questions.

The 0.66 UI band, where shown, is a display-only warning. It is not a research threshold and was not used to lock **T**.

### Local

```bash
cd V2
PYTHONPATH=. streamlit run app/streamlit_app.py
```

Install dependencies first (`python -m venv .venv`, then `pip install -r requirements.txt` from `V2/`). A local mock backend can exercise the UI. Official Qwen3-8B answers require a CUDA GPU runtime and the GGUF weights; those weights are not stored in this repository.

### Google Colab GPU (Phase 21)

For the official live demonstration on Colab Tesla T4 + Qwen3-8B + `llama_cpp`, use the canonical Phase 21 notebook:

`V2/notebooks/colab_phase21_final_live_demo.ipynb`

That notebook:

1. Clones this repository (`main`) on a Colab **GPU** runtime.
2. Restores the Phase 6 knowledge base from Google Drive (`MyDrive/MSc-RAG/artifacts/knowledge_base/`).
3. Verifies CUDA / Tesla T4 / Qwen3-8B Q4_K_M / `llama_cpp` and refuses mock or Ollama.
4. Starts `app/streamlit_app.py` on the Colab VM (port 8501).
5. Prints the Colab `proxyPort(8501)` browser URL. Open that URL, not `127.0.0.1` on a local Mac.

Phase 21 does **not** rerun the 420-case benchmark, the judge, calibration, or statistics. `colab_phase11_live.ipynb` is retained as historical live-artefact development evidence; Phase 21 is the canonical viva launcher.

## Repository Structure

```text
V2/
  app/                 Streamlit live artefact
  src/                 RAG, retrieval, evaluation, statistics
  config/              Experiment and prompt configuration
  scripts/             CLI entrypoints
  data/                Frozen 140 TEST and 40 DEV question files
  results/             Canonical evaluation artefacts (Phases 15–19)
  notebooks/           Colab notebooks (see below)
  project_record/      Project record and validation evidence
  tests/               Unit and static checks
  requirements.txt
README.md
.gitignore
```

## Development and Evaluation Phases

| Phase | Purpose | Status | Main output / evidence |
|------|---------|--------|-------------------------|
| 1 | V2 project foundation: repository structure, configuration and tests | Complete | V2 tree, configuration and tests |
| 2 | V1 audit and FinQA dataset profiling | Complete | FinQA profile and V1 audit |
| 3 | Source-PDF verification | Complete | PDF verification, 380/380 verified |
| 4 | Freeze final 140-question TEST set | Complete | Frozen TEST CSV, manifest, seed 42 |
| 5 | Freeze 40-question DEV calibration set | Complete | Frozen DEV calibration CSV, manifest, seed 42 |
| 6 | Build final knowledge base | Complete | 230 source documents / 1239 chunks |
| 7 | Establish Qwen backend and runtime | Complete | Qwen3-8B / llama.cpp runtime and fingerprints |
| 8 | Implement and smoke-test Single-Agent RAG | Complete | Single-Agent implementation and smoke evidence |
| 9 | Implement and smoke-test Multi-Agent RAG verification | Complete | Multi-Agent implementation and smoke evidence |
| 10 | Implement and smoke-test Multi-Agent RAG with UQ and abstention | Complete | UQ implementation and smoke evidence |
| 11 | Develop live application interface | Complete | Streamlit live UI |
| 12 | Controlled pilot evaluation | Complete | 18-case pilot evidence |
| 13 | Confidence-threshold calibration and lock | Complete | threshold.lock.json, T = 0.65 |
| 14 | Engineering validation before official benchmark | Complete | 9-case validation; engineering evidence only |
| 15 | Official 420-case architecture benchmark | Complete | 420/420 official benchmark; 140 per architecture |
| 16 | CPU processing and separate post-hoc LLM judge | Complete | 420 evaluation rows + 420 judge rows |
| 17 | Statistical analysis and final figures | Complete | Tests, assumptions, effect sizes and six canonical figures |
| 18 | Qualitative error analysis | Complete | Error taxonomy and qualitative analysis |
| 19 | Reproducibility and artefact audit | Complete | Audit, manifest and integrity checks |
| 20 | Final live Streamlit artefact | Complete | Three live pipeline pages with evidence, verification, confidence and decision |
| 21 | Canonical final live-demo launcher and final audit | Complete | Final live-demo notebook and static validation |

- Phase 15 is the official 420-case architecture benchmark.
- Phase 16 is the separate 420-case post-hoc judge evaluation.
- Phases 17–19 are script/result phases and do not require notebooks.
- Phase 20 is the final Streamlit artefact.
- Phase 21 is the final live-demo launcher/static audit.
- Phase 7–10, 12 and 14 notebooks are historical engineering/smoke/pilot/validation artefacts and are NOT the official 420-case benchmark.

## Notebooks and analysis artefacts

| Phase | Role | Location |
| --- | --- | --- |
| 15 | Official 420-case RAG benchmark (Colab T4) | `V2/notebooks/colab_phase15_full_benchmark.ipynb` |
| 16 | Official 420-case post-hoc LLM-as-judge | `V2/notebooks/colab_phase16_judge.ipynb` |
| 17 | Final statistics and canonical figures | `V2/scripts/run_statistics.py`, `V2/scripts/render_phase17_figures.py`, `V2/results/metrics/phase17_*` |
| 18 | Final error analysis | `V2/scripts/run_error_analysis.py`, `V2/results/final/phase18_error_analysis.md` |
| 19 | Final reproducibility audit | `V2/scripts/run_reproducibility_audit.py`, `V2/results/final/phase19_artefact_manifest.md` |
| 20 | Live Streamlit artefact | `V2/app/streamlit_app.py`; historical GPU notebook `V2/notebooks/colab_phase11_live.ipynb` |
| 21 | Canonical live-demo launcher | `V2/notebooks/colab_phase21_final_live_demo.ipynb` |

Phases 17–19 were implemented as CPU scripts over frozen artefacts; they were never Colab notebooks, and none have been invented here. The Phase 15 and 16 notebooks launched the official GPU jobs and do not replace the frozen result files.

## Reproducibility

Inspect submitted results from saved artefacts. Do not regenerate the frozen Phase 15–18 result files for inspection of the submitted experiment.

1. Frozen TEST set: `V2/data/final/selected_140_questions.csv` (140 questions).
2. DEV calibration set: `V2/data/calibration/calibration_questions.csv` (40 questions).
3. Locked threshold: `V2/results/config/threshold.lock.json` (T = 0.65).
4. Benchmark summary: `V2/results/config/phase15_benchmark_summary.json`.
5. CPU-scored cases: `V2/results/processed/phase16_cases.jsonl`.
6. Judge summary: `V2/results/metrics/phase16_judge_summary.csv`.
7. Statistics: `V2/results/metrics/phase17_tests.csv`.
8. Error analysis: `V2/results/final/phase18_error_analysis.md`.
9. Reproducibility audit: `V2/results/final/phase19_artefact_manifest.md`.
10. Chronology: `V2/project_record/PROJECT_MASTER_RECORD.md`.

Intentionally **not** stored on GitHub:

- Qwen GGUF model weights and Hugging Face caches;
- the built Chroma PDF index (rebuild with `V2/scripts/build_index.py` if reproducing retrieval from documents);
- large raw Phase 15 `cases.jsonl` and Phase 16 `judge.jsonl` dumps (summaries and scored tables are tracked).

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
| Official 420-case benchmark | `V2/notebooks/colab_phase15_full_benchmark.ipynb`, `V2/results/config/phase15_benchmark_summary.json` |
| Official 420-case judge | `V2/notebooks/colab_phase16_judge.ipynb`, `V2/results/metrics/phase16_judge_summary.csv` |
| Live Colab launcher | `V2/notebooks/colab_phase21_final_live_demo.ipynb` |

## Notes

This repository contains the author’s submitted MSc project code and frozen evaluation artefacts. It is a research prototype, not a production system. No user study was conducted. The custom judge is not official RAGAS.
