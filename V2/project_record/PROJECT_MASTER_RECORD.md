# PROJECT MASTER RECORD — V2

**Authoritative chronological record of the implemented V2 project.**  
Plan intent is secondary to actual code, configuration, artefacts, and test results in this repository.

| Field | Value |
| --- | --- |
| Last updated | 2026-08-22 |
| Current completed phase | **Phase 7** |
| Next phase (not started) | Phase 8 — Single-Agent RAG baseline |
| V1 status | Reference-only (never modified by V2 work) |
| Working title | Multi-Agent RAG with Uncertainty Quantification for Financial Document QA |

---

## Project snapshot (verified)

### Research questions (locked)

1. **RQ1:** Does Multi-Agent RAG improve answer accuracy vs Single-Agent RAG on a financial document corpus?
2. **RQ2:** Does uncertainty quantification reduce hallucinated/unsupported responses in Multi-Agent RAG?
3. **RQ3:** Does confidence-based abstention improve reliability when supporting evidence is insufficient?

### Dataset (verified live)

| Item | Verified value | Evidence |
| --- | --- | --- |
| Family / subset | T²-RAGBench / FinQA | `load_dataset("G4KMU/t2-ragbench", "FinQA")` |
| Splits | train 6251, dev 883, test 1147 (total 8281) | `data/processed/finqa_profile.json` |
| PDF path rule | `data/FinQA/{split}/{file_name}` | `data/processed/finqa_pdf_probe.json` |
| Test PDFs in HF repo | 380/380 resolved | same |
| Frozen test set | **140** questions, seed **42** | `data/final/selected_140_questions.csv` |
| Test id SHA-256 | `1a69d93e412097a076e8ec836253b8fff53366aefc5ea5f8998020984f6bbd8a` | `data/final/sampling_manifest.json` |
| Calibration set | **40** DEV questions, seed **42** | `data/calibration/calibration_questions.csv` |
| Calibration id SHA-256 | `b229d45331fc18dd7c784175abd37cee3550775f268c843b2417d3f9d2e3aeca` | `data/calibration/calibration_manifest.json` |
| Threshold lock | **Not created** (`threshold_locked: false`) | calibration manifest |
| Knowledge base | **230** source PDFs indexed → **1239** chunks | `knowledge_base/index/index_manifest.json` |
| Embedding model | `BAAI/bge-small-en-v1.5` | index manifest |
| Chunking | size 900 / overlap 150 | index manifest / `experiment.yaml` |
| Distractors | 50 train PDFs | index manifest `roles.distractor` |

### Model / compute

| Item | Status |
| --- | --- |
| LLM | Qwen3-8B (configured); live smoke via Ollama `qwen3:8b` |
| Backend abstraction | `src/models/` — `llama_cpp` / `transformers` / `ollama_dev` / `mock` |
| Planned Colab GGUF | `bartowski/Qwen_Qwen3-8B-GGUF` + `Qwen_Qwen3-8B-Q4_K_M.gguf` (filename verified on HF) — Colab GPU load **NEEDS VERIFICATION** |
| Primary compute | **Standard Google Colab GPU notebooks** (not Colab CLI / gcloud) |
| Colab entrypoint | `notebooks/colab_phase7_smoke.ipynb` |
| Colab GPU verification | **NEEDS VERIFICATION** (next validation step) |
| Local Mac | Dev/control; Phase 7 generation smoke used optional `ollama_dev` |
| Paid LLM API | Not used / not required |
| Fingerprint artefact | `results/config/phase7_runtime_fingerprint.json` |
| Smoke artefact | `results/config/phase7_smoke_generate.json` (answer `4`) |

### Architectures (not implemented yet)

1. Single-Agent RAG  
2. Multi-Agent RAG  
3. Multi-Agent + UQ / abstention  

**NEEDS VERIFICATION / later phases:** confidence method weights; whether Arch3 reuses Arch2 draft/verify; dense vs hybrid retrieval; judge configuration.

### Test suite status (as of last update)

- Command: `pytest` from `V2/` with `PYTHONPATH=.`
- Result: **36 passed** (Phases 1–7 + storage/backup + GGUF filename test)

### Storage / backup (project infrastructure)

| Item | Status |
| --- | --- |
| Storage model documented | GitHub / Colab / Drive / Local Mac |
| Cursor rule | `.cursor/rules/06-storage-backup-recovery.mdc` |
| Implementation plan | `docs/IMPLEMENTATION_PLAN.md` |
| Config | `config/experiment.yaml` → `storage` |
| Drive root | `Google Drive/MSc-RAG/` — **NEEDS VERIFICATION** (not yet confirmed on user's Drive) |
| Benchmark recovery spec | 420 cases; incremental checkpoint/resume defined in config |
| Phase backup template | `project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md` |
| Validation evidence | `project_record/evidence/phase1_validation.md` … `phase7_validation.md` |
| Phase 7 smoke JSON | `results/config/phase7_smoke_test.json` |

## Decisions log (corrections and standing rules)

Append-only. Historical phase sections below are not rewritten when assumptions change.

1. **V1 is reference-only.** All implementation under `V2/` (and Cursor rules under `.cursor/rules/`).
2. **FinQA test** = frozen evaluation 140; **FinQA dev** = calibration only; never tune threshold on test.
3. **Gold `context` is evaluation-only**, not the retrieval corpus. KB must use source PDFs.
4. **Sampling seeds frozen:** test seed 42; calibration seed 42. Do not change freezes for result-driven reasons.
5. **Threshold not locked in Phase 5.** Lock before final test evaluation (later phase).
6. **Master record rule added 2026-08-21:** `.cursor/rules/05-project-master-record.mdc` — update this file after every completed phase.
7. **Phase 6 KB:** Source PDFs only (not gold context); Chroma + bge-small-en-v1.5; 230 docs / 1239 chunks verified.
8. **Phase 7 backends:** Final 420-case benchmark must use Colab GPU (`llama_cpp` or `transformers`). `ollama_dev` is optional local smoke only and is not the official benchmark path.
9. **Phase 7 remote strategy (2026-08-21 correction):** Use **standard Google Colab GPU notebooks** (`notebooks/colab_phase7_smoke.ipynb`). Do **not** use Colab CLI / `gcloud`. Architecture (Qwen3-8B, model abstraction, fingerprinting, checkpoint/resume design) unchanged. Next validation: Colab GPU verification.
10. **Storage model (2026-08-22):** GitHub = source; Colab = compute; Drive `MSc-RAG/` = persistent archive; Mac = dev + secondary backup. Incremental checkpoint/resume mandatory for 420-case benchmark. Never claim backup without verified paths.
11. **Validation evidence (2026-08-22):** `project_record/evidence/phaseN_validation.md` after every major phase; actual PASS/FAIL/NEEDS VERIFICATION only; `phase7_smoke_test.json` for machine-readable smoke evidence.
12. **Phase 7 GGUF filename correction (2026-08-22):** `gguf_filename` must be `Qwen_Qwen3-8B-Q4_K_M.gguf` on `bartowski/Qwen_Qwen3-8B-GGUF` (was incorrectly `Qwen3-8B-Q4_K_M.gguf`). Verified on HF Hub API; Colab `llama_cpp` run still **NEEDS VERIFICATION**.

---

## Phase 1 — Project foundation

- **Date:** 2026-08-21
- **Objective:** Create a clean V2 skeleton so later phases can proceed safely.
- **Why required:** Separate rebuilt artefact from V1; establish config, logging, paths, and tests without RAG/model work.
- **Work completed:**
  - V2 directory tree (`src/`, `config/`, `data/`, `results/`, `tests/`, stubs for later modules)
  - YAML experiment + prompt placeholders
  - Config loader, run IDs, structured logging hooks
  - Minimal `requirements.txt` (`PyYAML`, `pytest`)
  - `README.md`, `PROJECT_CONTEXT.md`, `DECISIONS.md`
  - Health check script and config-load tests
- **Technical decisions:**
  - Lightweight Phase 1 deps only (no torch/streamlit/chroma yet)
  - Placeholders/`null` for unverified scientific settings (threshold, quant, etc.)
- **Files created/modified (representative):**
  - `V2/README.md`, `V2/PROJECT_CONTEXT.md`, `V2/DECISIONS.md`, `V2/.gitignore`, `V2/requirements.txt`, `V2/pytest.ini`
  - `V2/config/experiment.yaml`, `V2/config/prompts.yaml`
  - `V2/src/config/loader.py`, `V2/src/utils/logging_utils.py`, `V2/src/utils/run_id.py`
  - `V2/scripts/health_check.py`, `V2/tests/test_config_loads.py`
- **Tests/validation:** Phase 1 config/path/logging tests passed (later subsumed into full suite).
- **Actual outcome:** Importable V2 package; config loads; V1 untouched.
- **Problems encountered:** Local `.venv` creation required unrestricted permissions in the sandbox.
- **Problems resolved:** Created `V2/.venv` outside sandbox restrictions for installs/tests.
- **Remaining issues:** No RAG/model/dataset freeze yet (by design).
- **Dissertation relevance:** Establishes reproducible project layout and configuration discipline.
- **Evidence:** `V2/src/config/loader.py`, `V2/config/experiment.yaml`, `V2/tests/test_config_loads.py`

---

## Phase 2 — V1 audit + FinQA live profile

- **Date:** 2026-08-21
- **Objective:** Capture V1 lessons and live-load FinQA schema/quality signals without selecting the 140.
- **Why required:** Avoid repeating V1 methodological flaws; ground V2 in the actual FinQA dataset.
- **Work completed:**
  - V1 audit notes (`docs/v1_audit.md`)
  - `datasets` dependency; `src/data/profile_finqa.py`; `scripts/inspect_dataset.py`
  - Profile outputs: `docs/dataset_profile.md`, `data/processed/finqa_profile.json`
- **Technical decisions:**
  - Treat gold `context` as oracle evaluation material, not KB content
  - Document absence of unsupported / insufficient-evidence labels for RQ2/RQ3
- **Files created/modified:**
  - `V2/docs/v1_audit.md`, `V2/docs/dataset_profile.md`
  - `V2/src/data/profile_finqa.py`, `V2/scripts/inspect_dataset.py`
  - `V2/data/processed/finqa_profile.json`
  - `V2/tests/test_phase2_profile.py`
  - `V2/requirements.txt` (+ `datasets`)
- **Tests/validation:** Profile artefact tests; live load confirmed splits train/dev/test = 6251/883/1147.
- **Actual outcome:** Schema and split sizes verified; 140 **not** selected in this phase’s original boundary (selection deferred to Phase 4).
- **Problems encountered:** Initial RQ-implications key typo (`severity` vs `rq`) broke markdown render test.
- **Problems resolved:** Fixed key; re-ran inspect + tests.
- **Remaining issues:** PDF path mapping not fully proven until Phase 3 probe.
- **Dissertation relevance:** Dataset justification; V1 limitations; RQ operational risks.
- **Evidence:** `V2/docs/dataset_profile.md`, `V2/data/processed/finqa_profile.json`, `V2/docs/v1_audit.md`

---

## Phase 3 — Dataset verification (PDF resolvability)

- **Date:** 2026-08-21
- **Objective:** Close FinQA verification, including source-PDF availability in the HF dataset repo.
- **Why required:** A real KB cannot be planned without confirming PDFs exist and how `file_name` maps to repo paths.
- **Work completed:**
  - HF repo listing via `huggingface_hub`
  - PDF probe JSON + Phase 3 checkpoint doc
  - Confirmed mapping and 100% test PDF resolution
- **Technical decisions:**
  - `repo_path = data/FinQA/{split}/{file_name}`
  - Do not download full PDF corpus yet (Phase 6)
- **Files created/modified:**
  - `V2/docs/phase3_dataset_verification.md`
  - `V2/data/processed/finqa_pdf_probe.json`
  - `V2/tests/test_phase3_verification.py`
  - Updates to `docs/dataset_profile.md`, `config/experiment.yaml`, `requirements.txt` (+ `huggingface_hub`)
- **Tests/validation:** Probe asserts 380 matched, 0 missing; profile split counts unchanged.
- **Actual outcome:** Test source documents are resolvable; KB path is clear for Phase 6.
- **Problems encountered:** None blocking after Phase 2 profile existed.
- **Problems resolved:** N/A
- **Remaining issues:** PDFs not downloaded locally; embed/index not built.
- **Dissertation relevance:** Provenance and corpus construction methodology.
- **Evidence:** `V2/docs/phase3_dataset_verification.md`, `V2/data/processed/finqa_pdf_probe.json`

---

## Phase 4 — Freeze 140 FinQA test questions

- **Date:** 2026-08-21
- **Objective:** Reproducibly select and freeze the final evaluation set of 140 unique test questions.
- **Why required:** Experimental integrity requires a frozen test set before benchmarking; no result-driven resampling later.
- **Work completed:**
  - Filter: non-empty `id`, `question`, `program_answer`, `context_id`, `file_name`, `context`
  - Deduplicate normalized questions (keep lowest `id`)
  - Seeded greedy diversity sample: seed **42**, max **3**/company, max **1**/file
  - Freeze CSV + manifest + results/config snapshot
- **Technical decisions:**
  - Primary answer field for eligibility: `program_answer`
  - Existing freeze is not overwritten unless `--force`
- **Files created/modified:**
  - `V2/src/data/select_140.py`, `V2/scripts/select_140.py`
  - `V2/data/final/selected_140_questions.csv`
  - `V2/data/final/sampling_manifest.json`
  - `V2/results/config/phase4_sampling_manifest.json`
  - `V2/docs/phase4_sampling.md`, `V2/tests/test_phase4_select_140.py`
- **Tests/validation:**
  - Unit tests for filter/dedupe/sample
  - Integration: n=140, unique ids/questions, SHA matches CSV
  - Seed replay identical
  - Filter stats: 1147 → drop 1 essential + 2 duplicate questions → 1144 eligible → select 140
  - Outcome diversity: **77** companies, **140** files
- **Actual outcome:** Frozen evaluation set ready; calibration not yet selected.
- **Problems encountered:** Older Phase 2/3 tests asserted absence of the 140 file; stratification unit test used n that forced cap relaxation.
- **Problems resolved:** Updated phase tests; tightened unit test to n=15 under strict caps.
- **Remaining issues:** No KB/RAG yet; threshold not applicable until calibration + UQ exist.
- **Dissertation relevance:** Sampling methodology, reproducibility, controlled evaluation design.
- **Evidence:** `V2/data/final/selected_140_questions.csv`, `V2/data/final/sampling_manifest.json`, `V2/docs/phase4_sampling.md`

---

## Phase 5 — Freeze FinQA DEV calibration set

- **Date:** 2026-08-21
- **Objective:** Freeze a separate DEV calibration sample for future confidence/threshold work.
- **Why required:** RQ3 threshold must not be tuned on the frozen test 140.
- **Work completed:**
  - Load DEV; same essential filter + dedupe as Phase 4
  - Exclude id/question overlap with frozen test 140
  - Sample **40** with seed **42**, max **2**/company, max **1**/file
  - Manifest explicitly sets `threshold_locked: false`
- **Technical decisions:**
  - Calibration size 40 (within planned 30–50)
  - No `threshold.lock.json` in this phase
- **Files created/modified:**
  - `V2/src/data/select_calibration.py`, `V2/scripts/select_calibration.py`
  - `V2/data/calibration/calibration_questions.csv`
  - `V2/data/calibration/calibration_manifest.json`
  - `V2/results/config/phase5_calibration_manifest.json`
  - `V2/docs/phase5_calibration.md`, `V2/tests/test_phase5_calibration.py`
- **Tests/validation:**
  - No id/question overlap with test 140
  - n=40; seed replay OK
  - Full suite: **21 passed**
  - Confirmed `results/config/threshold.lock.json` absent
- **Actual outcome:** Calibration freeze complete; threshold selection deferred.
- **Problems encountered:** Phase 4 integration test still forbade calibration file existence.
- **Problems resolved:** Removed that assertion after Phase 5 freeze.
- **Remaining issues:** Confidence method and locked threshold **NEEDS VERIFICATION** / later phases; PDFs not downloaded; RAG not built.
- **Dissertation relevance:** Calibration/test separation; experimental validity for RQ3.
- **Evidence:** `V2/data/calibration/calibration_questions.csv`, `V2/data/calibration/calibration_manifest.json`, `V2/docs/phase5_calibration.md`

---

## Phase 6 — Knowledge base (source PDFs)

- **Date:** 2026-08-21
- **Objective:** Build a persistent vector knowledge base from FinQA source page PDFs for retrieval (not gold context).
- **Why required:** Live RAG and the 420-case benchmark need a real shared corpus with provenance; V1’s gold-context-as-document approach is invalid.
- **Work completed:**
  - Download 230 PDFs (test 140 + calibration 40 + 50 train distractors) via Hugging Face
  - Extract text (PyMuPDF), chunk (900/150), embed (`BAAI/bge-small-en-v1.5`), persist Chroma
  - Retrieval demo on a frozen test question with provenance metadata
- **Technical decisions:**
  - Corpus = frozen evaluation/calibration PDFs + 50 distractors (seed 42)
  - Collection `finqa_source_pdfs`, cosine space
  - Explicitly exclude gold `context` ingestion
- **Files created/modified:**
  - `V2/src/retrieval/*.py`, `V2/scripts/build_index.py`
  - `V2/knowledge_base/documents/**`, `V2/knowledge_base/index/**`
  - `V2/knowledge_base/index/index_manifest.json`, `retrieval_demo.json`
  - `V2/docs/phase6_knowledge_base.md`, `V2/tests/test_phase6_knowledge_base.py`
  - `V2/requirements.txt` (+ pymupdf, sentence-transformers, chromadb)
- **Tests/validation:**
  - Unit: chunking provenance
  - Integration: manifest + demo hits with `source_type=pdf`
  - Guardrail: no V1-style gold `.txt` KB dumps
  - Build: docs_indexed=230, chunks=1239, download_failed=0
- **Actual outcome:** Retrieval works from source PDFs; demo top hit matched the gold file for the smoke question (`pdf/SNA/2013/page_34.pdf`).
- **Problems encountered:** None blocking; local embed took ~minutes on CPU.
- **Problems resolved:** N/A
- **Remaining issues:** Embedding model revision pin **NEEDS VERIFICATION** if required for paper; Qwen backend and RAG arches not started; top-k/chunk settings may be revisited after pilot (**NEEDS VERIFICATION** against latency/quality).
- **Dissertation relevance:** Corpus construction, anti-leakage design, provenance for examiner demo.
- **Evidence:** `V2/knowledge_base/index/index_manifest.json`, `V2/knowledge_base/index/retrieval_demo.json`, `V2/docs/phase6_knowledge_base.md`

---

## Phase 7 — Qwen3-8B backend

- **Date:** 2026-08-21
- **Objective:** Model backend abstraction + runtime fingerprint + one successful generation (without building RAG architectures).
- **Why required:** Later RAG phases need a stable generate API and reproducible device/model logging; Mac must not be required for final inference.
- **Work completed:**
  - `src/models/` backends: `llama_cpp` (GGUF), `transformers` (4-bit when CUDA), `ollama_dev`, `mock`
  - Factory (`create_backend`) with `auto` preference order
  - Fingerprint collector (platform, GPU/nvidia-smi, torch, package versions, model config, git commit)
  - Smoke script `scripts/smoke_generate.py`; Colab notebook `notebooks/colab_phase7_smoke.ipynb` + notes `notebooks/colab_runtime.md`
  - Live smoke on Mac via Ollama `qwen3:8b` → answer `4`
- **Technical decisions:**
  - Default GGUF: `bartowski/Qwen_Qwen3-8B-GGUF` / `Qwen_Qwen3-8B-Q4_K_M.gguf`
  - `backend: auto` in `experiment.yaml`; Colab primary = llama_cpp or transformers
  - Ollama allowed for local smoke only
  - Remote execution = standard Colab GPU notebooks (not Colab CLI) — confirmed in strategy update
- **Files created/modified:**
  - `V2/src/models/*.py`, `V2/scripts/smoke_generate.py`
  - `V2/notebooks/colab_phase7_smoke.ipynb`, `V2/notebooks/colab_runtime.md`, `V2/docs/phase7_qwen_backend.md`
  - `V2/tests/test_phase7_model_backend.py`, `V2/config/experiment.yaml`, `V2/requirements.txt`
  - `V2/results/config/phase7_runtime_fingerprint.json`, `phase7_smoke_generate.json`
- **Tests/validation:**
  - Unit: fingerprint fields + mock generate + factory
  - Integration: smoke artefacts present with non-empty text
  - Live: `ollama_dev` generation latency ~4.9s
  - Full suite: **29 passed**
- **Actual outcome:** Abstraction works; one logged successful generate (local `ollama_dev`). Colab GGUF path implemented for notebook execution; live Colab GPU smoke not run in this session.
- **Problems encountered:** Newer `ollama` Python client returns pydantic `ChatResponse` (no `.keys()`); first smoke crashed after generation. Mac has no `gcloud` / Colab CLI (not required under notebook strategy).
- **Problems resolved:** Parse both dict and ChatResponse message content. Remote strategy documented as Colab notebooks (not CLI).
- **Remaining issues:** **Next validation step — Colab GPU verification** (GGUF/transformers VRAM fit via `notebooks/colab_phase7_smoke.ipynb`) recorded as **NEEDS VERIFICATION** in `project_record/evidence/phase7_validation.md`; RAG arches not started.
- **Dissertation relevance:** Reproducible model logging; controlled compute story (Colab notebook primary).
- **Evidence:** `V2/results/config/phase7_smoke_test.json`, `V2/results/config/phase7_runtime_fingerprint.json`, `V2/docs/phase7_qwen_backend.md`, `V2/notebooks/colab_phase7_smoke.ipynb`
- **Validation evidence:** `V2/project_record/evidence/phase7_validation.md` (GGUF filename fix verified on HF; Colab GPU smoke **NEEDS VERIFICATION**)
- **GGUF filename fix (2026-08-22):** `Qwen_Qwen3-8B-Q4_K_M.gguf` in `experiment.yaml`, `llama_cpp_backend.py`, `factory.py`

---

## Project infrastructure — Storage, backup & recovery

- **Date:** 2026-08-22
- **Objective:** Establish project-wide storage, backup, recovery, progress-tracking rules and integrate into the approved V2 plan (no new RAG functionality).
- **Why required:** 420-case Colab benchmark must survive interruption; dissertation needs verified artefact trails; prevent data loss from ephemeral Colab storage.
- **Work completed:**
  - Cursor rule `.cursor/rules/06-storage-backup-recovery.mdc`
  - `docs/storage_backup_recovery.md`, `docs/IMPLEMENTATION_PLAN.md` (with dedicated Storage section)
  - `config/experiment.yaml` → `storage` (Drive layout, benchmark recovery, raw fields, live artefact rules)
  - `project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md`
  - Updated master-record rule (05) with backup-status requirement
  - Tests: `tests/test_storage_backup_recovery.py`
- **Technical decisions:**
  - Four-layer model: GitHub / Colab / Drive / Local Mac
  - Drive logical root `Google Drive/MSc-RAG/` with results/checkpoints/logs/configs/artifacts
  - No full V2 repo mirror on Drive; no Colab CLI/gcloud
  - Same RAG pipelines for benchmark and live Streamlit (when built)
- **Files created/modified:**
  - `.cursor/rules/06-storage-backup-recovery.mdc`, `.cursor/rules/05-project-master-record.mdc`
  - `V2/docs/storage_backup_recovery.md`, `V2/docs/IMPLEMENTATION_PLAN.md`
  - `V2/project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md`
  - `V2/config/experiment.yaml`, `V2/DECISIONS.md`, `V2/PROJECT_CONTEXT.md`
  - `V2/tests/test_storage_backup_recovery.py`
- **Tests/validation:** Storage config + doc/rule presence tests added.
- **Actual outcome:** Rules and plan integrated; benchmark recovery contract specified in config; no RAG code added.
- **Problems encountered:** None.
- **Problems resolved:** N/A
- **Remaining issues:** Google Drive folder layout **NEEDS VERIFICATION**; benchmark runner not yet implemented (later phases); Colab GPU smoke **NEEDS VERIFICATION**.
- **Dissertation relevance:** Reproducibility, artefact provenance, honest reporting of backup status.
- **Evidence:** `V2/docs/storage_backup_recovery.md`, `V2/docs/IMPLEMENTATION_PLAN.md`, `V2/config/experiment.yaml`
- **Validation evidence:** `V2/project_record/evidence/` (phases 1–7 backfilled; template for future phases)
- **Backup status (this task):**
  - Colab: N/A (documentation only)
  - Google Drive: **NEEDS VERIFICATION** — user must create `MSc-RAG/` layout
  - Local: files in local V2 repo (verified by implementation)
  - GitHub: recommended commit for this infrastructure task
- **Local backup recommendation:** Optional — copy nothing new beyond existing local repo until Drive is set up.
- **GitHub commit recommendation:** Commit rules, docs, config, tests, evidence files; exclude large/raw results.

---

## Not started (explicit)

| Phase | Name | Status |
| --- | --- | --- |
| 8–10 | Baseline / Multi-Agent / UQ RAG | Not started |
| 11+ | Schema logging, Streamlit, pilot, calibration lock, 420 benchmark, stats | Not started |

---

## How to update this record

After each completed phase, append a new `## Phase X — ...` section with the required fields, update the **Project snapshot** table with newly verified facts, and append any assumption changes to the **Decisions log** without rewriting prior phase sections.
