# PROJECT MASTER RECORD — V2

**Authoritative chronological record of the implemented V2 project.**  
Plan intent is secondary to actual code, configuration, artefacts, and test results in this repository.

| Field | Value |
| --- | --- |
| Last updated | 2026-08-24 |
| Current completed phase | **Phase 11** |
| Next phase (not started) | Phase 12+ — pilot / calibration lock / 420-case benchmark |
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
| Knowledge base | **230** source PDFs indexed → **1239** chunks | Colab rebuild: `knowledge_base/index/index_manifest.json` on Colab/Drive (see Phase 8); Mac local manifest is stale |
| Embedding model | `BAAI/bge-small-en-v1.5` | index manifest |
| Chunking | size 900 / overlap 150 | index manifest / `experiment.yaml` |
| Distractors | 50 train PDFs | index manifest `roles.distractor` |

### Model / compute

| Item | Verified value | Evidence |
| --- | --- | --- |
| LLM | Qwen3-8B | Colab smoke |
| Backend (Colab) | `llama_cpp` | `phase7_smoke_test.json` |
| GGUF | `bartowski/Qwen_Qwen3-8B-GGUF` / `Qwen_Qwen3-8B-Q4_K_M.gguf` | fingerprint + smoke |
| Quantisation | Q4_K_M | fingerprint |
| Device | CUDA | fingerprint |
| GPU | Tesla T4 (15360 MB VRAM; driver 580.82.07) | fingerprint |
| Torch | 2.11.0+cu128; CUDA available | fingerprint |
| llama_cpp | 0.3.35 | fingerprint |
| Python (Colab) | 3.13.15 (Linux x86_64) | fingerprint |
| Colab Phase 7 smoke | **PASS** (2026-08-22T16:23:06Z) | `phase7_smoke_test.json` |
| Colab Phase 8 smoke | **PASS** (2026-08-23T12:42:22Z) | `phase8_smoke_test.json` |
| Phase 8 run ID | `phase8_20260823T124009Z_70a29b9f` | `phase8_single_agent_smoke.json` |
| Phase 8 git commit (Colab) | `846c143` | `phase8_runtime_fingerprint.json` |
| Primary compute | Standard Google Colab GPU notebooks | notebook entrypoint |
| Colab entrypoint | `notebooks/colab_phase7_smoke.ipynb` (model); `notebooks/colab_phase8_smoke.ipynb` (single-agent); `notebooks/colab_phase9_smoke.ipynb` (multi-agent); `notebooks/colab_phase10_smoke.ipynb` (multi-agent + UQ) | — |
| Colab Phase 9 smoke | **PASS** (2026-08-23T13:51:40Z) | `phase9_smoke_test.json` |
| Phase 9 run ID | `phase9_20260823T134858Z_6260bf43` | `phase9_multi_agent_smoke.json` |
| Phase 9 git commit (Colab) | `e749fab` | `phase9_runtime_fingerprint.json` |
| Local Mac | Dev/control; optional `ollama_dev` smoke | local Phase 8 PASS (2026-08-22) |
| Paid LLM API | Not used / not required | — |
| Phase 7 artefacts | `phase7_runtime_fingerprint.json`, `phase7_smoke_test.json` | — |
| Phase 8 artefacts | `phase8_runtime_fingerprint.json`, `phase8_smoke_test.json`, `phase8_single_agent_smoke.json` | local copy verified |
| Phase 9 artefacts | `phase9_runtime_fingerprint.json`, `phase9_smoke_test.json`, `phase9_multi_agent_smoke.json` | local copy verified |
| Colab Phase 10 smoke | **PASS** (2026-08-23T14:10:15Z) | `phase10_smoke_test.json` |
| Phase 10 run ID | `phase10_20260823T140737Z_ab9b33d4` | `phase10_multi_agent_uq_smoke.json` |
| Phase 10 git commit (Colab) | `2f3882e` | `phase10_runtime_fingerprint.json` |
| Phase 10 artefacts | `phase10_runtime_fingerprint.json`, `phase10_smoke_test.json`, `phase10_multi_agent_uq_smoke.json` | local copy verified |
| Phase 11 live artefact | `app/streamlit_app.py` via `run_live_comparison()` | local smoke PASS |
| Colab Phase 11 live | **PASS** (user-reported T4 / Qwen3-8B / three architectures); raw UQ 0.7688 / 0.55 / ANSWER | user report 2026-08-24 |
| Phase 11 artefacts | `phase11_runtime_fingerprint.json`, `phase11_smoke_test.json`, `phase11_live_smoke.json` | local copy verified |

### Architectures

1. **Single-Agent RAG** — implemented (Phase 8); local + Colab smoke **PASS** (n=3 each)
2. **Multi-Agent RAG** — implemented (Phase 9); local + Colab smoke **PASS** (n=3 each)
3. **Multi-Agent + UQ / abstention** — implemented (Phase 10); local + Colab smoke **PASS** (n=3 each); architecture `multi_agent_uq`

**NEEDS VERIFICATION / later phases:** confidence method weights; whether Arch3 reuses Arch2 draft/verify; dense vs hybrid retrieval; judge configuration.

### Test suite status (as of last update)

- Command: `pytest` from `V2/` with `PYTHONPATH=.`
- Result: **77 passed** (Phases 1–11 + UQ display + verification rationale + insufficient-evidence question)

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
| Validation evidence | `project_record/evidence/phase1_validation.md` … `phase11_validation.md` |
| Phase 7 smoke JSON | `results/config/phase7_smoke_test.json` |
| Phase 8 smoke JSON | `results/config/phase8_smoke_test.json` (local copy; gitignored by default) |

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
12. **Phase 7 GGUF filename correction (2026-08-22):** `gguf_filename` must be `Qwen_Qwen3-8B-Q4_K_M.gguf` on `bartowski/Qwen_Qwen3-8B-GGUF` (was incorrectly `Qwen3-8B-Q4_K_M.gguf`). Verified on HF Hub API.
13. **Phase 7 Colab GPU smoke verified (2026-08-22):** Tesla T4 + `llama_cpp` + Q4_K_M GGUF → **PASS**. Evidence: `results/config/phase7_smoke_test.json`, `phase7_runtime_fingerprint.json`.
14. **Phase 8 Single-Agent RAG (2026-08-22):** Retrieve from Phase 6 KB + generate via Qwen3-8B backend; common `RAGCaseResult` schema; no multi-agent/UQ. Local smoke n=3 **PASS** (`ollama_dev` + real retrieval).
15. **Phase 8 Colab retrieval fix (2026-08-23):** Option B — rebuild Chroma on Colab via `build_index.py` (HF PDF download); index preflight (`validate_index_preflight`); `notebooks/colab_phase8_smoke.ipynb`. Mac Chroma DB not copied.
16. **Phase 8 Colab Single-Agent smoke verified (2026-08-23):** Tesla T4 + `llama_cpp` + Qwen3-8B Q4_K_M → **PASS**; run_id `phase8_20260823T124009Z_70a29b9f`; git `846c143`; 3/3 questions, 4 evidence chunks each; retrieval + generation succeeded. Evidence: `phase8_smoke_test.json`, `phase8_single_agent_smoke.json`, `phase8_runtime_fingerprint.json`. Colab KB manifest at `knowledge_base/index/index_manifest.json` on Colab/Drive — **not** stale `results/config/phase6_index_manifest.json` (Mac paths).
17. **Phase 9 Multi-Agent RAG (2026-08-23):** Retrieve → draft → verify (lexical + LLM support score). Architecture `multi_agent`; reuses Phase 6 KB + Qwen3 backend factory; `verification_result` populated; `decision=ANSWER`; no abstention/UQ. Local smoke n=3 **PASS** (mock); Colab T4 `llama_cpp` smoke n=3 **PASS**; run_id `phase9_20260823T134858Z_6260bf43`; git `e749fab`.
18. **Phase 10 Multi-Agent + UQ / abstention (2026-08-23):** Extends Phase 9 with combined confidence = mean(retrieval_score, verification_score); binary gate `ANSWER | ABSTAIN`; no self-consistency. Architecture `multi_agent_uq`. Smoke threshold 0.55 (not locked). Colab T4 `llama_cpp` smoke n=3 **PASS**; run_id `phase10_20260823T140737Z_ab9b33d4`; git `2f3882e`; 3/3 ANSWER at smoke threshold.
19. **Phase 11 Streamlit live artefact (2026-08-23):** One app runs the three completed pipelines independently on a fresh question or a frozen test case. Shared Phase 6 KB + one backend instance; not a benchmark lookup. Local smoke (mock + real retrieval) **PASS**; run_id `phase11_20260823T222633Z_90aab3d6`; Streamlit HTTP 200. Original plan item “result schema + logging” was already delivered in Phases 8–10 via `RAGCaseResult`.
20. **Phase 11 live failure display (2026-08-23):** Live artefact must not show ANSWER when retrieval or generation fails (empty evidence, empty generation, or exception such as ProxyError 403). Live layer sets ERROR/UNAVAILABLE, shows the actual error, clears fabricated answers and confidence. Mock remains UI/testing only. Phase 8–10 architecture modules unchanged.
21. **Phase 11 Colab live-demo connection (2026-08-24):** The reported live demo (`backend=mock`, `device=mps_capable_host`, `ProxyError: 403 Forbidden`) was the local Mac Streamlit process, not Colab T4/`llama_cpp`. The live-demo notebook now verifies CUDA/T4, GGUF, and a non-empty Chroma index, starts Streamlit **inside Colab** with `V2_LIVE_BACKEND=llama_cpp` + `V2_FORBID_MOCK=1`, and refuses Darwin/mock fallback. A Colab T4 URL + fresh-question smoke result is still **NEEDS VERIFICATION**.
22. **Phase 11 Colab live-demo launch (2026-08-24):** A later UI still showed `backend=llama_cpp` with `device=mps_capable_host`, `gpu=null`, ~0.01s latency, and `127.0.0.1:8501`. That is Mac Streamlit with `llama_cpp` selected, not Colab. Launch now uses Colab `proxyPort` + iframe (no cloudflared). Streamlit refuses `llama_cpp` on Darwin. Section 5 runs frozen `finqa_test_1000` on the Colab GPU. Subsequent Colab T4 live execution was **user-reported PASS**.
23. **Phase 11 prompt / verification / UQ display (2026-08-24):** Generation prompts tightened (concise final answer, no instruction echo). Verification status + rationale are derived from the same scores. UQ zeros in Streamlit were a display/mapping issue (`st.metric` + schema not reading `uncertainty_result`); calculated values were 0.7688 / 0.55 / ANSWER. Display now shows the calculated confidence and `0.55 (smoke/demo — NOT LOCKED)`. Insufficient-evidence live question (SpaceX FY2025) identified; local mock smoke produced genuine UQ **ABSTAIN** at confidence 0.5351 < 0.55. Methodology unchanged. Threshold lock / 420-case benchmark not started.

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

- **Date:** 2026-08-21 (implementation); Colab GPU smoke verified **2026-08-22**
- **Objective:** Model backend abstraction + runtime fingerprint + one successful generation (without building RAG architectures).
- **Why required:** Later RAG phases need a stable generate API and reproducible device/model logging; Mac must not be required for final inference.
- **Work completed:**
  - `src/models/` backends: `llama_cpp` (GGUF), `transformers` (4-bit when CUDA), `ollama_dev`, `mock`
  - Factory (`create_backend`) with `auto` preference order
  - Fingerprint collector (platform, GPU/nvidia-smi, torch, package versions, model config, git commit)
  - Smoke script `scripts/smoke_generate.py`; Colab notebook `notebooks/colab_phase7_smoke.ipynb` + notes `notebooks/colab_runtime.md`
  - Local smoke (Mac): Ollama `qwen3:8b` → answer `4`
  - **Colab GPU smoke (verified):** `llama_cpp` + Q4_K_M GGUF on Tesla T4 → **PASS**
- **Technical decisions:**
  - Default GGUF: `bartowski/Qwen_Qwen3-8B-GGUF` / `Qwen_Qwen3-8B-Q4_K_M.gguf`
  - `backend: auto` in `experiment.yaml`; Colab primary = llama_cpp or transformers
  - Ollama allowed for local smoke only
  - Remote execution = standard Colab GPU notebooks (not Colab CLI) — confirmed in strategy update
- **Files created/modified:**
  - `V2/src/models/*.py`, `V2/scripts/smoke_generate.py`
  - `V2/notebooks/colab_phase7_smoke.ipynb`, `V2/notebooks/colab_runtime.md`, `V2/docs/phase7_qwen_backend.md`
  - `V2/tests/test_phase7_model_backend.py`, `V2/config/experiment.yaml`, `V2/requirements.txt`
  - `V2/results/config/phase7_runtime_fingerprint.json`, `phase7_smoke_test.json`
- **Tests/validation:**
  - Unit: fingerprint fields + mock generate + factory + GGUF filename
  - Local: `ollama_dev` smoke PASS
  - **Colab (2026-08-22T16:23:06Z):** status **PASS**; run_id `phase7_20260822T162122Z_cee1f3d4`
  - Full suite (local): **36 passed**
- **Colab runtime (verified from fingerprint):**
  - Device: **cuda**
  - GPU: **Tesla T4** (15360 MB total VRAM; 14913 MB free at capture; driver 580.82.07)
  - Torch: **2.11.0+cu128**; CUDA available; 1 device
  - llama_cpp: **0.3.35**
  - Platform: Linux 6.6.122+ x86_64; Python **3.13.15**
  - Model: **Qwen3-8B**; backend **llama_cpp**; quant **Q4_K_M**; file `Qwen_Qwen3-8B-Q4_K_M.gguf`
  - Notebook: `notebooks/colab_phase7_smoke.ipynb`
- **Colab generation (verified from smoke JSON):**
  - Prompt: smoke arithmetic (`2 + 2` → number only)
  - Status: **PASS** (non-empty text; error null)
  - Observed output begins with **`4`**; continued generation until max tokens (`finish_reason: length`; 512 completion tokens; latency **15.37s**)
- **Actual outcome:** Backend abstraction works on Colab GPU. Primary remote path (`llama_cpp` GGUF Q4_K_M on Tesla T4) verified with successful smoke generation.
- **Problems encountered:** Initial GGUF filename mismatch (`Qwen3-8B-Q4_K_M.gguf` vs actual `Qwen_Qwen3-8B-Q4_K_M.gguf`); Ollama ChatResponse parsing on Mac; Colab Drive auth issues (resolved via GitHub clone workflow).
- **Problems resolved:** Correct GGUF filename; Ollama response parsing; Colab clone-from-GitHub notebook path.
- **Remaining issues:** RAG architectures not started (Phase 8+); smoke `finish_reason: length` / verbose continuation is a known generation-control detail for later prompt/token tuning if needed — does not invalidate Phase 7 PASS.
- **Dissertation relevance:** Reproducible model/GPU logging; Colab-primary compute story verified.
- **Evidence:** `V2/results/config/phase7_smoke_test.json`, `V2/results/config/phase7_runtime_fingerprint.json`, `V2/docs/phase7_qwen_backend.md`, `V2/notebooks/colab_phase7_smoke.ipynb`
- **Validation evidence:** `V2/project_record/evidence/phase7_validation.md`
- **GGUF filename fix (2026-08-22):** `Qwen_Qwen3-8B-Q4_K_M.gguf` in `experiment.yaml`, `llama_cpp_backend.py`, `factory.py`
- **Backup status (Phase 7 Colab verification):**
  - Colab: verified run artefacts in local V2 copy of `results/config/phase7_*.json`
  - Google Drive: **NEEDS VERIFICATION** (optional copy to `MSc-RAG/configs/phase7/`)
  - Local: verified — smoke + fingerprint files present under `V2/results/config/`
  - GitHub: recommended commit of updated master record + evidence after this verification

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
- **Remaining issues:** Google Drive folder layout **NEEDS VERIFICATION**; benchmark runner not yet implemented (later phases). Colab GPU smoke verified **PASS** (Phase 7).
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

## Phase 8 — Single-Agent RAG baseline

- **Date:** 2026-08-22 (implementation); Colab validation verified **2026-08-23**
- **Objective:** Implement and validate Single-Agent RAG using the Phase 6 KB/retriever and Qwen3-8B backend (common raw-result schema; no multi-agent / UQ).
- **Why required:** RQ1 baseline architecture; shared retrieve+generate path for later architectures and the live artefact.
- **Work completed:**
  - `RAGCaseResult` schema aligned with `storage.raw_result_fields`
  - Baseline prompts in `config/prompts.yaml`
  - `run_single_agent()`: retrieve (Chroma/bge) → prompt → generate
  - Smoke script `scripts/smoke_single_agent.py` (small-N frozen questions)
  - Local smoke **n=3** with real retrieval + Qwen3 generation (`ollama_dev`) → **PASS** (2026-08-22)
  - Ollama `think=False` to avoid empty Qwen3 responses on local smoke
  - **Colab retrieval fix (2026-08-23):** `src/retrieval/preflight.py`, `scripts/validate_kb_index.py`, `notebooks/colab_phase8_smoke.ipynb`; preflight in `smoke_single_agent.py` and `build_index.py`; Drive save cell for KB + results
  - **Colab smoke **n=3** (`llama_cpp`, Tesla T4) → **PASS** (2026-08-23T12:42:22Z)
- **Technical decisions:**
  - Architecture id: `single_agent`; case key `{architecture}:{question_id}`
  - Baseline always `decision=ANSWER`; `confidence`/`verification_result`/`threshold` left null
  - Reuse Phase 6 index (`finqa_source_pdfs`, top_k=4) and Phase 7 backend factory
  - Empty-generation one-shot retry in `run_single_agent`
  - Colab: Option B KB rebuild (`build_index.py`) before smoke; do not copy Mac Chroma DB
- **Files created/modified:**
  - `V2/src/rag/schema.py`, `prompts.py`, `single_agent.py`, `__init__.py`
  - `V2/src/retrieval/preflight.py`, `scripts/validate_kb_index.py`
  - `V2/scripts/smoke_single_agent.py`, `V2/tests/test_phase8_single_agent.py`, `V2/tests/test_index_preflight.py`
  - `V2/config/prompts.yaml`, `V2/config/experiment.yaml` (`rag` section)
  - `V2/docs/phase8_single_agent.md`, `V2/notebooks/colab_phase8_smoke.ipynb`
  - `V2/results/config/phase8_*.json`, `phase8_single_agent_smoke.jsonl` (local copies; gitignored)
- **Tests/validation:**
  - Unit: schema fields, prompt formatting, mock retrieve+generate; index preflight tests
  - Local Mac smoke (2026-08-22): 3/3 PASS, 4 evidence chunks each (`ollama_dev`)
  - Colab smoke (2026-08-23): 3/3 PASS, 4 evidence chunks each (`llama_cpp`, Tesla T4)
  - Full suite: **43 passed**
- **Colab validation (verified 2026-08-23T12:42:22Z):**
  - Status: **PASS** (`phase8_smoke_test.json`)
  - Run ID: `phase8_20260823T124009Z_70a29b9f`
  - Git commit at run: `846c143`
  - GPU: Tesla T4; backend: `llama_cpp`; model: Qwen3-8B Q4_K_M
  - KB: rebuilt on Colab at `/content/capstone-rag/V2/knowledge_base/index` (Option B); 230 docs / 1239 chunks (manifest on Colab/Drive — not stale Mac `results/config/phase6_index_manifest.json`)
  - Per-case (`phase8_single_agent_smoke.json`): all 3 questions — 4 evidence chunks, non-empty answers, no errors; retrieval + generation succeeded
  - Example: `finqa_test_1000` top hit `pdf/SNA/2013/page_34.pdf` (score ~0.872)
- **Actual outcome:** Single-Agent RAG works end-to-end locally and on Colab GPU with real retrieval from rebuilt Chroma index. Frozen sets unchanged. No multi-agent/UQ.
- **Problems encountered:** Local Ollama Qwen3 sometimes returned empty `content` when thinking mode was enabled; initial Colab clone had empty Chroma index (`n_evidence=0`).
- **Problems resolved:** Ollama `think=False` + empty-answer retry; Colab Option B KB rebuild + preflight guardrail.
- **Remaining issues:** Multi-Agent / UQ not started (Phase 9–10); full 420-case runner not started; generation verbosity / `max_new_tokens` tuning optional for later.
- **Dissertation relevance:** Controlled baseline for RQ1; provenance-bearing retrieval + logged generation; Colab-primary compute path verified for RAG (not just model smoke).
- **Evidence:**
  - PASS status: `V2/results/config/phase8_smoke_test.json`
  - Per-case: `V2/results/config/phase8_single_agent_smoke.json`
  - Runtime: `V2/results/config/phase8_runtime_fingerprint.json`
  - Colab KB manifest: `knowledge_base/index/index_manifest.json` on Colab/Drive (rebuilt 2026-08-23 session)
  - Diagnosis: `V2/project_record/evidence/phase8_colab_retrieval_diagnosis.md`
- **Validation evidence:** `V2/project_record/evidence/phase8_validation.md`
- **Backup status (Phase 8 Colab verification):**
  - Colab: verified run — user confirmed successful notebook execution; ephemeral `/content` index unless Drive cell run
  - Google Drive: user-reported save of KB + JSONs via notebook section 7 → `MyDrive/MSc-RAG/artifacts/knowledge_base/` and `MyDrive/MSc-RAG/configs/phase8/` — **NEEDS VERIFICATION** of exact paths on Drive
  - Local: verified — `V2/results/config/phase8_*.json` present; `V2/project_record/` updated
  - GitHub: source + evidence committed separately; `results/config/phase8_*.json` gitignored by default; recommend commit master record + `phase8_validation.md` + notebook; HEAD local `a5f8530`, Colab run at `846c143`

---

## Phase 9 — Multi-Agent RAG

- **Date:** 2026-08-23
- **Objective:** Implement Multi-Agent RAG (retrieve → draft → verify) using shared KB, retriever, Qwen3-8B backend, and `RAGCaseResult` schema. No UQ/abstention.
- **Why required:** RQ1 second architecture; adds verification agent over Phase 8 baseline.
- **Work completed:**
  - `run_multi_agent()`: retrieve → draft prompt → generate → verification score
  - `compute_verification_result()`: lexical overlap + LLM support score (average)
  - Multi-agent prompts in `config/prompts.yaml`
  - Smoke script `scripts/smoke_multi_agent.py` with index preflight (no KB rebuild)
  - Colab notebook `notebooks/colab_phase9_smoke.ipynb` (clone → KB restore → `llama_cpp` smoke → Drive save)
  - Local smoke **n=3** → **PASS** (mock LLM + real Phase 6 retrieval)
  - **Colab validation (verified 2026-08-23T13:51:40Z):**
    - Status: **PASS** (`phase9_smoke_test.json`)
    - Run ID: `phase9_20260823T134858Z_6260bf43`
    - Git commit at run: `e749fab`
    - GPU: Tesla T4; backend: `llama_cpp`; model: Qwen3-8B Q4_K_M
    - KB: restored from Drive (Phase 8 artefact); index at `/content/capstone-rag/V2/knowledge_base/index`
    - Per-case: all 3 questions — 4 evidence chunks, non-empty draft answers, verification_result present, status `VERIFIED`, no errors
    - Example: `finqa_test_1000` top hit `pdf/SNA/2013/page_34.pdf` (score ~0.872); verify score 0.637
- **Technical decisions:**
  - Architecture id: `multi_agent`; case key `multi_agent:{question_id}`
  - Reuse Phase 6 index/retriever/embeddings/top_k unchanged
  - `verification_result`: `{verification_score, lexical_score, llm_score, verification_threshold, status}`
  - `status`: `VERIFIED` or `WEAK_EVIDENCE` at threshold 0.5 (informational only in Phase 9)
  - `confidence`: verification score (not combined UQ — Phase 10)
  - `decision`: always `ANSWER`; `threshold`: null
  - No self-consistency, no abstention
- **Files created/modified:**
  - `V2/src/rag/multi_agent.py`, `verification.py`, `text_utils.py`
  - `V2/src/rag/prompts.py`, `schema.py`, `__init__.py`
  - `V2/scripts/smoke_multi_agent.py`, `V2/tests/test_phase9_multi_agent.py`
  - `V2/config/prompts.yaml`, `V2/config/experiment.yaml`
  - `V2/docs/phase9_multi_agent.md`, `V2/notebooks/colab_phase9_smoke.ipynb`, `V2/notebooks/colab_runtime.md`
  - `V2/results/config/phase9_*.json`, `phase9_multi_agent_smoke.jsonl`
- **Tests/validation:**
  - Unit: prompts, verification scoring, mock pipeline, schema fields
  - Live smoke: 3/3 PASS; 4 evidence chunks each; verification_result present
  - Full suite: **49 passed**
- **Actual outcome:** Multi-Agent pipeline works end-to-end locally and on Colab GPU with real retrieval. Draft + verification (two LLM calls per case) succeeded on T4. All 3 smoke cases `VERIFIED`. Frozen sets unchanged. No architecture changes required.
- **Problems encountered:** Qwen3 draft verbosity/repetition at `max_new_tokens=512` (observed in Colab answers; not a smoke failure).
- **Problems resolved:** N/A for Colab run (executed successfully via `colab_phase9_smoke.ipynb`).
- **Remaining issues:** Phase 10 UQ/abstention not started; full 420-case runner not started; optional draft `max_new_tokens` / prompt tuning for later.
- **Dissertation relevance:** Second controlled architecture for RQ1; verification provenance in raw results.
- **Evidence:** `V2/results/config/phase9_smoke_test.json`, `phase9_multi_agent_smoke.json`, `phase9_runtime_fingerprint.json`, `docs/phase9_multi_agent.md`
- **Validation evidence:** `V2/project_record/evidence/phase9_validation.md`
- **Backup status (Phase 9 Colab verification):**
  - Colab: verified run — user executed `notebooks/colab_phase9_smoke.ipynb`; ephemeral `/content` unless Drive cell run
  - Google Drive: user-reported save via notebook cell 7 → `MyDrive/MSc-RAG/configs/phase9/` — **NEEDS VERIFICATION** of exact paths on Drive
  - Local: verified — `V2/results/config/phase9_*.json` present (user copied from Colab); `V2/project_record/` updated 2026-08-23
  - GitHub: source + notebook at `a9d6b0a`; Colab run at `e749fab`; `results/config/phase9_*.json` gitignored; recommend commit master record + `phase9_validation.md`

---

## Phase 10 — Multi-Agent RAG + UQ / abstention

- **Date:** 2026-08-23
- **Objective:** Third architecture: Multi-Agent pipeline plus combined UQ and confidence-based abstention (`ANSWER | ABSTAIN`) for RQ2/RQ3.
- **Why required:** Completes the three independent RAG architectures for the 420-case benchmark; enables abstention when combined confidence is below threshold.
- **Work completed:**
  - `run_multi_agent_uq()`: retrieve → draft → verify → combined confidence → abstention gate
  - `compute_combined_confidence()`: mean(retrieval_score, verification_score) — no self-consistency
  - `apply_abstention_decision()`: ANSWER returns draft; ABSTAIN returns abstention message (draft preserved in `configuration.draft_answer`)
  - Smoke script `scripts/smoke_multi_agent_uq.py`; Colab notebook `notebooks/colab_phase10_smoke.ipynb`
  - Local smoke **n=3** → **PASS** (mock)
  - **Colab validation (verified 2026-08-23T14:10:15Z):**
    - Status: **PASS** (`phase10_smoke_test.json`)
    - Run ID: `phase10_20260823T140737Z_ab9b33d4`
    - Git commit at run: `2f3882e`
    - GPU: Tesla T4; backend: `llama_cpp`; threshold: 0.55 (smoke only)
    - Per-case: 3/3 — 4 evidence chunks each; uncertainty_result populated; all `ANSWER` (confidence 0.715–0.813 ≥ 0.55)
- **Technical decisions:**
  - Architecture id: `multi_agent_uq`; case key `multi_agent_uq:{question_id}`
  - Reuse Phase 6 index/retriever/embeddings/top_k and Phase 9 draft/verify unchanged
  - UQ method: `mean_retrieval_verification`
  - Threshold priority: CLI override → locked `confidence_threshold` → `smoke_threshold` (0.55)
  - No self-consistency (V1 cost/variance issue); no Warning tier (binary ANSWER | ABSTAIN)
  - Final benchmark threshold must be locked on dev calibration (Phase 14), never on frozen test 140
- **Files created/modified:**
  - `V2/src/rag/uncertainty.py`, `multi_agent_uq.py`, `schema.py`, `__init__.py`
  - `V2/scripts/smoke_multi_agent_uq.py`, `V2/tests/test_phase10_multi_agent_uq.py`
  - `V2/config/experiment.yaml`, `V2/config/prompts.yaml`
  - `V2/docs/phase10_multi_agent_uq.md`, `V2/notebooks/colab_phase10_smoke.ipynb`, `V2/notebooks/colab_runtime.md`
  - `V2/results/config/phase10_*.json`, `phase10_multi_agent_uq_smoke.jsonl`
- **Tests/validation:**
  - Unit: UQ scoring, abstention gate, mock pipeline, schema fields
  - Live smoke: 3/3 PASS locally and Colab
  - Full suite: **55 passed**
- **Actual outcome:** All three architectures implemented and Colab-verified on T4. UQ gate populates confidence, threshold, and decision on every case. Abstention not triggered on n=3 smoke subset (high confidence); gate behaviour verified in unit tests. Frozen sets unchanged.
- **Problems encountered:** Qwen3 draft verbosity (carried from Phase 9); no ABSTAIN cases in n=3 smoke (confidence above smoke threshold).
- **Problems resolved:** N/A — Colab smoke executed successfully.
- **Remaining issues:** Locked threshold not created (Phase 14 calibration); full 420-case runner not started; optional prompt/`max_new_tokens` tuning.
- **Dissertation relevance:** Third architecture for controlled RQ1/RQ2/RQ3 comparison; abstention provenance in raw results.
- **Evidence:** `V2/results/config/phase10_smoke_test.json`, `phase10_multi_agent_uq_smoke.json`, `phase10_runtime_fingerprint.json`, `docs/phase10_multi_agent_uq.md`
- **Validation evidence:** `V2/project_record/evidence/phase10_validation.md`
- **Backup status (Phase 10 Colab verification):**
  - Colab: verified run — user executed `notebooks/colab_phase10_smoke.ipynb`
  - Google Drive: user-reported save via notebook cell 7 → `MyDrive/MSc-RAG/configs/phase10/` — **NEEDS VERIFICATION** of exact paths on Drive
  - Local: verified — `V2/results/config/phase10_*.json` present (user copied from Colab); project record + evidence updated 2026-08-23
  - GitHub: Colab run at git `2f3882e`; `results/config/phase10_*.json` gitignored; recommend commit master record + `phase10_validation.md` + Phase 10 source

---

## Phase 11 — Streamlit live artefact

- **Date:** 2026-08-23
- **Objective:** Integrate the three completed RAG architectures into a single Streamlit live artefact that executes real pipelines on a fresh user question (or a frozen test case).
- **Why required:** Examiner live demonstration; same V2 code path as benchmark mode; show evidence, verification, confidence, threshold, and ANSWER/ABSTAIN.
- **Work completed:**
  - `run_live_comparison()` runs `single_agent`, `multi_agent`, and `multi_agent_uq` independently on the same original question
  - Shared Phase 6 KB + one loaded backend instance; no KB rebuild
  - Streamlit app `app/streamlit_app.py` with frozen-case picker and fresh-question input
  - Per-architecture display: evidence, scores/metadata, answer, verification, confidence, threshold, decision, latency/runtime
  - Smoke: 1 frozen (`finqa_test_1000`) + 1 fresh question
  - Local smoke **PASS**; Streamlit HTTP **200**
- **Technical decisions:**
  - No architecture chaining; each pipeline retrieves and generates from the original question
  - Not a precomputed lookup
  - UQ threshold in the UI is the smoke/demo value only (not the locked benchmark threshold)
  - Original plan Phase 11 (schema/logging) already exists as `RAGCaseResult` / raw-result fields from Phases 8–10; this phase implements the live artefact originally listed as Phase 12
- **Files created/modified:**
  - `V2/src/rag/live.py`, `V2/src/rag/__init__.py`
  - `V2/app/streamlit_app.py`, `V2/app/__init__.py`
  - `V2/scripts/smoke_live_artefact.py`, `V2/tests/test_phase11_live_artefact.py`
  - `V2/docs/phase11_live_artefact.md`
  - `V2/config/experiment.yaml`, `V2/requirements.txt`, `V2/.gitignore`
  - `V2/results/config/phase11_*.json`
- **Tests/validation:**
  - Unit: independence, frozen loader, fresh IDs, schema fields, failure display — **10 passed**
  - Live smoke: 2 comparisons × 3 architectures — **PASS**; run_id `phase11_20260823T222633Z_90aab3d6`
  - Full suite: **65 passed**
  - Streamlit start: HTTP 200 at `http://127.0.0.1:8501`
- **Actual outcome:** Live artefact uses the real V2 RAG modules and existing KB. Frozen 140 / calibration 40 unchanged. V1 unchanged.
- **Problems encountered:** Failed live runs (empty evidence / ProxyError 403) still showed Decision=ANSWER and could display a mock answer. Browser click-through of the Run button was not executed in this agent environment (HTTP start verified only).
- **Problems resolved:** Live-only `normalize_live_case()` maps failed retrieval/generation to ERROR/UNAVAILABLE, shows the actual error, clears fabricated answers and confidence. Mock labelled UI/testing only; default backend is `auto`. Phase 8–10 architecture modules not changed.
- **Remaining issues:** Locked threshold not created (calibration); 420-case runner not started. **Observed live-demo connection FAIL (2026-08-24):** `backend=mock`, `device=mps_capable_host`, `ProxyError: 403 Forbidden` — Mac Streamlit, not Colab T4. Connection fix is implemented; Colab T4 `llama_cpp` live URL + fresh-question smoke is still **NEEDS VERIFICATION**.
- **Dissertation relevance:** Live artefact evidence for examiner demonstration of all three architectures.
- **Evidence:** `V2/results/config/phase11_smoke_test.json`, `phase11_live_smoke.json`, `docs/phase11_live_artefact.md`
- **Validation evidence:** `V2/project_record/evidence/phase11_validation.md`
- **Backup status (Phase 11):**
  - Colab: N/A for this local live-artefact phase
  - Google Drive: **NEEDS VERIFICATION** — live session JSONL would go to `results/raw/live_sessions.jsonl` then Drive if a Colab/demo session is archived
  - Local: verified — `V2/app/streamlit_app.py`; `V2/results/config/phase11_*.json`; project record + evidence updated 2026-08-23
  - GitHub: Phase 11 source **uncommitted**; recommend commit app + runner + tests + evidence; `results/raw/` gitignored

---

## Phase 11 — Colab live-demo runtime connection

- **Date:** 2026-08-24
- **Objective:** Make the Phase 11 Streamlit live demo use the Colab T4 / Qwen3-8B `llama_cpp` runtime instead of the local Mac mock process.
- **Why the phase was required:** The live demo still reported `backend=mock`, `device=mps_capable_host`, and `ProxyError: 403 Forbidden`. That fingerprint is the Mac host, so Streamlit was not attached to Colab.
- **Work completed:**
  - `src/models/runtime_guard.py` — refuse Darwin/macOS; require CUDA, `llama_cpp`, Qwen3-8B GGUF, and a non-empty Chroma index; never select mock
  - Factory and Streamlit lock `llama_cpp` when `V2_FORBID_MOCK=1` or `V2_LIVE_BACKEND=llama_cpp`
  - Live runner refuses a MockBackend instance when mock is forbidden
  - Smoke script verifies the same lock and refuses `--backend mock` under that env
  - `notebooks/colab_phase11_live.ipynb` section 8: abort if not Colab; verify GPU/GGUF/index; start existing `app/streamlit_app.py` in the Colab process; cloudflared tunnel; print URL; one `llama_cpp --fresh-only` smoke
- **Technical decisions:**
  - Do not change the three RAG architectures
  - Do not start the 420-case benchmark
  - Do not silently fall back to mock
  - Local Mac Streamlit remains available only when the forbid-mock env is unset (unit tests / UI testing)
- **Files created/modified:**
  - `V2/src/models/runtime_guard.py`
  - `V2/src/models/factory.py`
  - `V2/src/rag/live.py`
  - `V2/app/streamlit_app.py`
  - `V2/scripts/smoke_live_artefact.py`
  - `V2/tests/test_runtime_guard.py`
  - `V2/notebooks/colab_phase11_live.ipynb`
  - `V2/project_record/evidence/phase11_validation.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
- **Tests/validation:**
  - `tests/test_runtime_guard.py` + related Phase 7/11 tests — **21 passed**
  - Full suite — **71 passed**
  - Colab T4 Streamlit URL + fresh-question smoke — **NEEDS VERIFICATION** (cannot be executed from this Mac)
- **Actual outcome:** Code now refuses the Mac mock path for the Colab live-demo notebook. The only observed live-demo result remains the user-reported Mac failure (`mock` / `mps_capable_host` / ProxyError 403). No Colab T4 PASS is claimed.
- **Problems encountered:** Streamlit was being started on the Mac (`mps_capable_host`) with mock; ProxyError 403 appeared on that host.
- **Problems resolved:** Live-demo notebook and runtime guard abort on Darwin/non-Colab and lock `llama_cpp`. RAG pipelines unchanged.
- **Remaining issues:** Re-run `notebooks/colab_phase11_live.ipynb` on Colab GPU after the fix is on the clone branch; record the printed URL, backend, GPU, and smoke result. Frozen 140/40 unchanged. Benchmark not started.
- **Dissertation relevance:** Examiner live demo must show the real Qwen3-8B / T4 path, not a local mock.
- **Evidence/source file paths:** `V2/src/models/runtime_guard.py`, `V2/notebooks/colab_phase11_live.ipynb`
- **Validation evidence:** `V2/project_record/evidence/phase11_validation.md`
- **Backup status (Phase 11 connection fix):**
  - Colab: **not re-run** after this fix — previous observed result was Mac mock/MPS
  - Google Drive: **NEEDS VERIFICATION** — no new Colab `phase11_*.json` from a T4 live demo
  - Local: verified — guard, notebook, tests, evidence, master record updated 2026-08-24
  - GitHub: connection-fix files **uncommitted** at the time of this record; Colab clone will not see the fix until they are pushed to `cursor/empty-v2-workspace`

---

## Phase 11 — Colab live-demo launch (proxy URL)

- **Date:** 2026-08-24
- **Objective:** Start Streamlit inside the Colab T4 runtime and expose it with Colab's built-in port proxy so the browser cannot land on the Mac `127.0.0.1:8501` process.
- **Why the phase was required:** After the first connection fix, the UI still showed `backend=llama_cpp`, `device=mps_capable_host`, `gpu=null`, ~0.01s latency, and `127.0.0.1:8501`. That is local Streamlit with `llama_cpp` selected, not Colab CUDA.
- **Work completed:**
  - Notebook section 5 runs frozen `finqa_test_1000` through all three architectures on Colab GPU and writes `phase11_colab_live_demo.json`
  - Notebook section 8 starts `app/streamlit_app.py` on the Colab VM with CORS/XSRF disabled for the Colab proxy
  - Tunnel: `google.colab.kernel.proxyPort(8501)` + `serve_kernel_port_as_iframe` (no cloudflared)
  - Streamlit refuses `llama_cpp` on Darwin; Colab runtime always locks `llama_cpp` (no mock/Ollama)
  - Selecting `mps_capable_host` results after a run stops the page
- **Technical decisions:**
  - Simplest Colab-native proxy; do not add extra tunnel binaries
  - Do not change RAG architectures; do not start the benchmark; do not modify V1 or frozen 140/40
- **Files created/modified:**
  - `V2/notebooks/colab_phase11_live.ipynb`
  - `V2/app/streamlit_app.py`
  - `V2/src/models/runtime_guard.py`
  - `V2/src/models/factory.py`
  - `V2/tests/test_runtime_guard.py`
  - `V2/project_record/evidence/phase11_validation.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
- **Tests/validation:**
  - Full suite **73 passed**
  - Known-good FinQA question `finqa_test_1000` on Colab T4 — **NEEDS VERIFICATION** (cannot be executed from this Mac)
  - Observed user UI — **FAIL** (Mac `127.0.0.1:8501`)
- **Actual outcome:** Launch path no longer prints a Mac localhost URL as the demo link. No Colab T4 PASS is claimed. `finqa_test_1000` was not run on T4 from this environment.
- **Problems encountered:** User opened Streamlit's local bind address on the Mac; cloudflared was easy to skip in favour of `127.0.0.1:8501`.
- **Problems resolved:** Colab `proxyPort` + iframe; Darwin `llama_cpp` refused in the app.
- **Remaining issues:** Push this fix, re-run the notebook on Colab GPU, save `phase11_colab_live_demo.json` with actual CUDA/GPU fields.
- **Dissertation relevance:** Live demo must display the real Colab GPU, not `mps_capable_host`.
- **Evidence/source file paths:** `V2/notebooks/colab_phase11_live.ipynb`, `V2/app/streamlit_app.py`
- **Validation evidence:** `V2/project_record/evidence/phase11_validation.md`
- **Backup status (Phase 11 launch fix):**
  - Colab: **not re-run** after this launch fix
  - Google Drive: **NEEDS VERIFICATION** — no T4 `phase11_colab_live_demo.json`
  - Local: verified — notebook, Streamlit lock, tests, evidence, master record updated 2026-08-24
  - GitHub: launch-fix files **uncommitted**; Colab clone will not see them until push to `cursor/empty-v2-workspace`

---

## Phase 11 — Prompt, verification, and UQ display refinements

- **Date:** 2026-08-24
- **Objective:** Tighten live answers and verification consistency; fix UQ confidence/threshold showing as 0; add an insufficient-evidence live question for a genuine ABSTAIN demonstration.
- **Why required:** Colab T4 live succeeded, but answers were verbose/self-referential, verification text could contradict status, and Streamlit showed confidence=0 / threshold=0 while raw UQ was 0.7688 / 0.55 / ANSWER.
- **Work completed:**
  - Generation prompts now ask for one concise final answer and forbid instruction echo
  - `clean_generated_answer()` strips `<think>` blocks and instruction echo
  - Verification `status` + `rationale` are derived from the same scores
  - `parse_unit_score` ignores “between 0 and 1” instruction echoes
  - Live layer copies `uncertainty_result.confidence` onto `RAGCaseResult.confidence`; missing confidence → `n/a` / UNAVAILABLE, never 0
  - Streamlit displays confidence/threshold as text (not `st.metric`); smoke threshold labelled **NOT LOCKED**
  - Live insufficient-evidence question: SpaceX FY2025 GAAP / Starship cadence (not in frozen 140/40)
- **Technical decisions:**
  - UQ method unchanged: mean(retrieval_score, verification_score); gate unchanged
  - Do not force ABSTAIN; do not lock the threshold; do not start the 420-case benchmark
- **Files created/modified:**
  - `V2/config/prompts.yaml`, `V2/src/rag/prompts.py`, `V2/src/rag/text_utils.py`, `V2/src/rag/verification.py`
  - `V2/src/rag/single_agent.py`, `V2/src/rag/multi_agent.py`, `V2/src/rag/multi_agent_uq.py` (cleanup only)
  - `V2/src/rag/live.py`, `V2/app/streamlit_app.py`, `V2/scripts/smoke_live_artefact.py`
  - `V2/tests/test_phase9_multi_agent.py`, `V2/tests/test_phase11_live_artefact.py`
  - `V2/project_record/evidence/phase11_validation.md`, `V2/project_record/PROJECT_MASTER_RECORD.md`
- **Tests/validation:**
  - Full suite **77 passed**
  - Mock live smoke (real KB) **PASS** — run_id `phase11_20260823T235810Z_134d0128`
  - Known-good `finqa_test_1000` UQ **ANSWER** at confidence 0.6185 ≥ 0.55
  - Insufficient SpaceX/2025 UQ **ABSTAIN** at confidence 0.5351 < 0.55 (not forced)
- **Actual outcome:** Display now shows calculated UQ values. Smoke/demo threshold is labelled NOT LOCKED. Frozen sets and V1 unchanged.
- **Problems encountered:** `st.metric` rendered 0–1 UQ scores as 0; mock smoke failed once under a sandboxed ProxyError 403 (retried with network).
- **Problems resolved:** Schema exposure + markdown display; verification rationale tied to status.
- **Remaining issues:** Re-run the refined prompts/display on Colab T4/Qwen3-8B is **NEEDS VERIFICATION**. Calibration / threshold lock / 420-case benchmark not started.
- **Dissertation relevance:** RQ2/RQ3 live demo must show the real confidence, an honest NOT LOCKED threshold, and a genuine ABSTAIN example.
- **Evidence/source file paths:** `V2/results/config/phase11_live_smoke.json`, `V2/src/rag/live.py`
- **Validation evidence:** `V2/project_record/evidence/phase11_validation.md`
- **Backup status:**
  - Colab: user-reported T4 live PASS (pre-refinement); refined run **NEEDS VERIFICATION**
  - Google Drive: **NEEDS VERIFICATION**
  - Local: verified — smoke JSON, tests, evidence, master record updated 2026-08-24
  - GitHub: these refinement files **uncommitted**

---

## Not started (explicit)

| Phase | Name | Status |
| --- | --- | --- |
| 12+ | Pilot, calibration / threshold lock, 420-case benchmark, metrics, statistics | Not started |

---

## How to update this record

After each completed phase, append a new `## Phase X — ...` section with the required fields, update the **Project snapshot** table with newly verified facts, and append any assumption changes to the **Decisions log** without rewriting prior phase sections.
