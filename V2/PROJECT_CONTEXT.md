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
- Target: **140** frozen test questions × **3** architectures = **420** cases (Phase 4 freeze; Phase 15 Colab executed; Phase 16 CPU metrics complete)
- Calibration/threshold selection: FinQA **dev** only (never the frozen test set)
- Profile: `V2/docs/dataset_profile.md`, `V2/data/processed/finqa_profile.json`

## Model / compute

- LLM: Qwen3-8B (quantisation NEEDS_VERIFICATION on Colab GPU)
- Primary execution: **standard Google Colab GPU notebooks** (not Colab CLI / gcloud)
- Entrypoint: `V2/notebooks/colab_phase7_smoke.ipynb`
- Next validation step: Colab GPU verification (GGUF / transformers smoke) — **NEEDS VERIFICATION**
- Local Mac: development/control only (not required for final inference)
- No paid inference API

## Live artefact

Streamlit app that runs live pipelines on a new question through all three architectures (not precomputed benchmark lookup).

Entrypoint: `PYTHONPATH=. streamlit run app/streamlit_app.py`  
Locked threshold: **T=0.65** from `results/config/threshold.lock.json` (not the Phase 11 smoke 0.55).  
Pages: Live RAG Demo · Benchmark Results (read-only frozen metrics) · Benchmark Questions (read-only frozen 140).  
Notes: `V2/docs/phase20_live_artefact.md`. Evidence: `V2/project_record/evidence/phase20_live_artefact_validation.md`.

## Examiner requirements (summary)

- Measurable RQs, controlled comparison, documented methods/prompts/settings
- Live artefact with real retrieval, generation, verification, confidence, abstention
- Resumable experiments; raw results preserved; honest statistics
- Calibration/test separation; frozen 140; no result-driven retuning of the sample or threshold

## Phase status

**Phase 20 live-artefact validation complete** (local plumbing **PASS**; official Colab T4 + Qwen3-8B + `llama_cpp` **NEEDS VERIFICATION**). Phases 15–19 remain **PASS** on their recorded criteria. **No Phase 21 started.**

## Storage / backup / recovery

- Spec: `V2/docs/storage_backup_recovery.md`
- Plan section: `V2/docs/IMPLEMENTATION_PLAN.md` → Storage, Backup, Recovery and Monitoring
- Config: `V2/config/experiment.yaml` → `storage`
- Cursor rule: `.cursor/rules/06-storage-backup-recovery.mdc`
- Phase backup template: `V2/project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md`
- Validation evidence: `V2/project_record/evidence/phaseN_validation.md`
- Phase 8 notes: `V2/docs/phase8_single_agent.md`
- Phase 8 smoke: `V2/results/config/phase8_single_agent_smoke.json`
- Phase 8 evidence: `V2/project_record/evidence/phase8_validation.md`

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
- Phase 6 KB docs: `V2/knowledge_base/documents/`
- Phase 6 index: `V2/knowledge_base/index/`
- Phase 6 notes: `V2/docs/phase6_knowledge_base.md`
- Phase 7 notes: `V2/docs/phase7_qwen_backend.md`
- Phase 7 smoke: `V2/results/config/phase7_smoke_generate.json`
- Phase 7 fingerprint: `V2/results/config/phase7_runtime_fingerprint.json`
- Phase 11 live app: `V2/app/streamlit_app.py`
- Phase 11 notes: `V2/docs/phase11_live_artefact.md`
- Phase 11 evidence: `V2/project_record/evidence/phase11_validation.md`
- Phase 12 notes: `V2/docs/phase12_pilot.md`
- Phase 12 evidence: `V2/project_record/evidence/phase12_validation.md`
- Phase 12 Colab: `V2/notebooks/colab_phase12_pilot.ipynb`
- Phase 13 notes: `V2/docs/phase13_calibration_lock.md`
- Phase 13 evidence: `V2/project_record/evidence/phase13_validation.md`
- Phase 13 Colab: `V2/notebooks/colab_phase13_calibration.ipynb`
- Phase 14 notes: `V2/docs/phase14_benchmark.md`
- Phase 14 evidence: `V2/project_record/evidence/phase14_validation.md`
- Phase 14 Colab: `V2/notebooks/colab_phase14_benchmark_validation.ipynb`
- Phase 15 notes: `V2/docs/phase15_full_benchmark.md`
- Phase 15 evidence: `V2/project_record/evidence/phase15_validation.md`
- Phase 15 Colab: `V2/notebooks/colab_phase15_full_benchmark.ipynb`
- Phase 16 notes: `V2/docs/phase16_evaluation.md`
- Phase 16 evidence: `V2/project_record/evidence/phase16_validation.md`
- Phase 16 metrics: `V2/results/metrics/phase16_summary.csv`
- Phase 16 judge notes: `V2/docs/phase16_judge.md`
- Phase 16 judge notebook: `V2/notebooks/colab_phase16_judge.ipynb`
- Phase 17 notes: `V2/docs/phase17_statistics.md`
- Phase 17 evidence: `V2/project_record/evidence/phase17_validation.md`
- Phase 17 metrics: `V2/results/metrics/phase17_tests.csv`
- Phase 18 notes: `V2/docs/phase18_error_analysis.md`
- Phase 18 evidence: `V2/project_record/evidence/phase18_validation.md`
- Phase 19 notes: `V2/docs/phase19_reproducibility.md`
- Phase 19 evidence: `V2/project_record/evidence/phase19_reproducibility_audit.md`
- Phase 19 manifest: `V2/results/final/phase19_artefact_manifest.md`
- Phase 20 notes: `V2/docs/phase20_live_artefact.md`
- Phase 20 evidence: `V2/project_record/evidence/phase20_live_artefact_validation.md`
- Phase 20 summary: `V2/results/config/phase20_live_demo_summary.json`
- **Master record (authoritative chronology):** `V2/project_record/PROJECT_MASTER_RECORD.md`
