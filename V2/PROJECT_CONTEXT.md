# PROJECT_CONTEXT

Concise persistent context for V2 Cursor sessions. Update when major decisions change.

## Title

Design and Evaluation of a Multi-Agent Retrieval-Augmented Generation Framework with Uncertainty Quantification for Financial Document Question Answering

(Working title; may be refined later without changing the three RQs.)

## Research questions (final — do not add a fourth)

- **RQ1:** Multi-Agent RAG vs Single-Agent RAG — answer accuracy on a financial document corpus.
- **RQ2:** Does uncertainty quantification reduce hallucinated/unsupported responses in Multi-Agent RAG?
- **RQ3:** Does confidence-based abstention improve reliability when supporting evidence is insufficient?

## Architectures (independent; same question; no chaining)

1. Single-Agent / baseline RAG
2. Multi-Agent RAG (generation + verification)
3. Multi-Agent + uncertainty / confidence-based abstention (ANSWER | ABSTAIN)

## Dataset / benchmark

- Family: T²-RAGBench (`G4KMU/t2-ragbench`)
- Subset: FinQA
- **Verified splits (Phase 2):** train **6251**, dev **883**, test **1147** (total **8281**)
- Target: **140** frozen test questions × **3** architectures = **420** cases (not selected yet)
- Calibration/threshold selection: FinQA **dev** only (never the frozen test set)
- Profile: `V2/docs/dataset_profile.md`, `V2/data/processed/finqa_profile.json`

## Model / compute

- LLM: Qwen3-8B (quantisation NEEDS_VERIFICATION)
- Primary execution: Google Colab GPU / Colab CLI
- Local Mac: development/control only (not required for final inference)
- No paid inference API

## Live artefact

Streamlit app that runs live pipelines on a new question through all three architectures (not precomputed benchmark lookup). Implemented in a later phase.

## Examiner requirements (summary)

- Measurable RQs, controlled comparison, documented methods/prompts/settings
- Live artefact with real retrieval, generation, verification, confidence, abstention
- Resumable experiments; raw results preserved; honest statistics
- Calibration/test separation; frozen 140; no result-driven retuning of the sample or threshold

## Phase status

**Phase 5 complete — FinQA DEV calibration set frozen (40 questions; threshold not locked).**  
Next approved step: Phase 6 (knowledge base from source PDFs).

## Key paths

- Config: `V2/config/experiment.yaml`
- Package: `V2/src/`
- Results: `V2/results/`
- Decisions log: `V2/DECISIONS.md`
- V1 audit: `V2/docs/v1_audit.md`
- Dataset profile: `V2/docs/dataset_profile.md`
- Phase 3 checkpoint: `V2/docs/phase3_dataset_verification.md`
- Phase 4 freeze: `V2/data/final/selected_140_questions.csv`
- Phase 4 manifest: `V2/data/final/sampling_manifest.json`
- Phase 4 notes: `V2/docs/phase4_sampling.md`
- Phase 5 calibration: `V2/data/calibration/calibration_questions.csv`
- Phase 5 manifest: `V2/data/calibration/calibration_manifest.json`
- Phase 5 notes: `V2/docs/phase5_calibration.md`
- **Master record (authoritative chronology):** `V2/project_record/PROJECT_MASTER_RECORD.md`
