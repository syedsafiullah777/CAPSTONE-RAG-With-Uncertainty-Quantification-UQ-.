# DECISIONS

Record important V2 decisions and rationale. Append; do not rewrite history silently.

## 2026-08-21 — Phase 1 foundation

**Decision:** Create a clean V2 package with YAML configuration, structured logging hooks, run IDs, standard paths, minimal dependencies (`PyYAML`, `pytest`), and package stubs for later phases.

**Rationale:** Keep Phase 1 lightweight; avoid installing ML stacks before dataset and Colab paths are verified.

**Not decided yet (NEEDS_VERIFICATION / later phases):**

- Exact FinQA train/dev/test row counts after live `load_dataset`
- Final 140 sampling strata and eligibility filters
- Quantisation / GGUF vs transformers-4bit on the actual Colab GPU
- Dense-only vs hybrid BM25 retrieval
- Confidence method weights and locked threshold
- Whether Arch3 reuses Arch2 draft/verify outputs in-process (recommended in plan; flag TBD)

## Standing rules

- V1 (repo content outside `V2/`) is reference-only — never edit as part of V2 work.
- Never tune the confidence threshold on the frozen test set.
- Never silently overwrite raw experimental results.
- Primary experimental variable is RAG architecture; shared components stay constant where scientifically appropriate.

## 2026-08-21 — Phase 2 V1 audit + FinQA profile

**Decision:** Document V1 lessons in `docs/v1_audit.md`. Live-load `G4KMU/t2-ragbench` FinQA and freeze a Phase 2 profile (not a 140 sample).

**Verified:**
- Splits: train 6251, dev 883, test 1147 (total 8281)
- Schema matches expected 21 columns
- Test essential-eligible ≈ 1146 (≥ 140)
- Unique `file_name` across splits: 2789 (matches card document count)
- PDFs are **not** in Arrow rows; require HF repo clone / separate download for real KB
- No insufficient-evidence label (RQ3); no unsupported label (RQ2)
- Do not feed gold `context` as retrieval

**Still deferred:**
- Final 140 selection (Phase 4)
- PDF acquisition and KB build (Phase 6)
- Quantisation / confidence method / Arch3 reuse flag

## 2026-08-21 — Phase 3 dataset verification closed

**Decision:** Treat FinQA schema/splits as verified. Confirm source PDFs resolve in the HF dataset repo before Phase 4 sampling.

**Verified:**
- Path rule: `data/FinQA/{split}/{file_name}`
- Test PDFs: **380/380** present in repo
- Checkpoint: `docs/phase3_dataset_verification.md`
- No 140 freeze in Phase 3

## 2026-08-21 — Phase 4 freeze 140 test questions

**Decision:** Freeze a reproducible FinQA **test** sample of 140 unique questions with seed 42, company cap 3, file cap 1.

**Outputs:**
- `data/final/selected_140_questions.csv`
- `data/final/sampling_manifest.json`
- `selected_ids_sha256 = 1a69d93e412097a076e8ec836253b8fff53366aefc5ea5f8998020984f6bbd8a`
- 77 companies, 140 distinct source files

**Rule:** Do not alter the freeze based on later experimental results. Calibration is Phase 5 (dev only).

## 2026-08-21 — Phase 5 freeze DEV calibration set

**Decision:** Freeze **40** FinQA **dev** questions (seed 42; company cap 2; file cap 1), excluding any id/question overlap with the frozen test 140.

**Outputs:**
- `data/calibration/calibration_questions.csv`
- `data/calibration/calibration_manifest.json`
- `selected_ids_sha256 = b229d45331fc18dd7c784175abd37cee3550775f268c843b2417d3f9d2e3aeca`
- 32 companies, 40 files
- `threshold_locked = false` (lock later, before test evaluation)

**Rule:** Never tune the confidence threshold on the frozen test 140.

## 2026-08-21 — Project master record instituted

**Decision:** Add Cursor rule `.cursor/rules/05-project-master-record.mdc` and authoritative chronology at `V2/project_record/PROJECT_MASTER_RECORD.md`.

**Rule:** After every completed phase, update the master record before declaring the phase complete. Do not overwrite historical phase summaries.

## 2026-08-21 — Phase 6 knowledge base

**Decision:** Index FinQA source page PDFs (test 140 + calibration 40 + 50 train distractors) with `BAAI/bge-small-en-v1.5` into Chroma; never ingest gold `context` as KB documents.

**Verified build:** 230 docs indexed, 1239 chunks, 0 download failures. Manifest: `knowledge_base/index/index_manifest.json`.

## 2026-08-21 — Phase 7 Qwen backend

**Decision:** RAG code talks only to `create_backend()` / `LLMBackend`. Primary Colab path is `llama_cpp` GGUF (`bartowski/Qwen_Qwen3-8B-GGUF`, `Qwen3-8B-Q4_K_M.gguf`) with `transformers` 4-bit fallback. `ollama_dev` is optional local smoke only and must not be required for the final 420-case benchmark.

**Verified smoke (Mac):** `scripts/smoke_generate.py --backend ollama_dev` → answer `4`; artefacts under `results/config/phase7_*.json`.

## 2026-08-21 — Phase 7 remote strategy: Colab notebooks (not CLI)

**Decision:** Primary remote execution uses **standard Google Colab GPU notebooks** (`notebooks/colab_phase7_smoke.ipynb`). Colab CLI / `gcloud` is not part of the V2 execution path.

**Unchanged:** Qwen3-8B, `src/models` abstraction, runtime fingerprinting, checkpointing/resumable benchmark design.

**Next validation step:** Colab GPU verification — run the Phase 7 notebook on a real Colab GPU (`remote_execution.colab_gpu_verification: NEEDS_VERIFICATION`).

## 2026-08-22 — Storage, backup, recovery and monitoring

**Decision:** Adopt four-layer storage model:

- GitHub = source/version control
- Google Colab = computation only
- Google Drive (`Google Drive/MSc-RAG/`) = persistent experiment archive/recovery
- Local Mac = secondary offline backup + main dev copy

**Requirements:** Incremental saves, checkpoint/resume, duplicate prevention, raw-result preservation, phase backup reminders, master-record backup status. No second permanent copy of full V2 repo on Drive. No Colab CLI/gcloud.

**Docs:** `docs/storage_backup_recovery.md`, `docs/IMPLEMENTATION_PLAN.md`, `.cursor/rules/06-storage-backup-recovery.mdc`, config `storage` section.

**Drive root NEEDS VERIFICATION** until user creates and confirms `Google Drive/MSc-RAG/` layout.

## 2026-08-22 — Validation evidence system

**Decision:** After every major phase, save actual test/smoke/benchmark results to `project_record/evidence/phaseN_validation.md` plus machine-readable JSON where useful (e.g. `results/config/phase7_smoke_test.json`). Record PASS/FAIL/NEEDS VERIFICATION from observed runs only — never fabricate PASS. Master record must reference the evidence file. Benchmark raw outputs stay in `results/raw/`; evidence files are concise summaries.

**Backfilled:** `phase1_validation.md` through `phase7_validation.md`. Colab GPU smoke in Phase 7 recorded as **NEEDS VERIFICATION**.

## 2026-08-22 — Phase 7 GGUF filename correction

**Correction:** `model.gguf_filename` → `Qwen_Qwen3-8B-Q4_K_M.gguf` on `bartowski/Qwen_Qwen3-8B-GGUF`. Previous value `Qwen3-8B-Q4_K_M.gguf` did not exist on the repo.

**Verified:** HF Hub metadata (5027784224 bytes); pytest 36 passed; local `ollama_dev` smoke PASS; **Colab `llama_cpp` on Tesla T4 PASS** (2026-08-22T16:23:06Z) — see `results/config/phase7_smoke_test.json`.

## 2026-08-22 — Phase 8 Single-Agent RAG baseline

**Decision:** Implement `single_agent` as retrieve (Phase 6 KB) → baseline prompt → Qwen3-8B generate. Use `RAGCaseResult` matching `storage.raw_result_fields`. Always `decision=ANSWER`; leave confidence/verification/threshold null until Phase 10. Do not implement multi-agent or abstention here.

**Verified smoke:** n=3 frozen questions; real Chroma retrieval + `ollama_dev` generation; status **PASS**. Artefacts: `results/config/phase8_single_agent_smoke.json`, `project_record/evidence/phase8_validation.md`.

## 2026-08-23 — Phase 9 Multi-Agent RAG

**Decision:** Implement `multi_agent` as retrieve (shared Phase 6 KB) → draft → verification (lexical + LLM support score). Populate `verification_result` and set `confidence` to verification score. Always `decision=ANSWER`; no self-consistency, combined UQ, or abstention (Phase 10). Do not rebuild or duplicate the knowledge base.

**Verified smoke:** n=3 frozen questions; real retrieval + mock draft/verify LLM; status **PASS**; run_id `phase9_20260823T130745Z_22fab337`. Artefacts: `results/config/phase9_multi_agent_smoke.json`, `project_record/evidence/phase9_validation.md`. Colab T4 `llama_cpp` smoke **PASS** (2026-08-23T13:51:40Z); run_id `phase9_20260823T134858Z_6260bf43`.

## 2026-08-23 — Phase 10 Multi-Agent + UQ / abstention

**Decision:** Implement `multi_agent_uq` as Phase 9 pipeline plus combined confidence = mean(retrieval_score, verification_score) and binary gate `ANSWER | ABSTAIN`. No self-consistency (V1 cost/variance issue). Smoke uses `uncertainty.smoke_threshold` (0.55) only — final threshold locked on dev calibration (Phase 14), never on frozen test 140. Preserve draft in `configuration.draft_answer` when abstaining.

**Colab entrypoint:** `notebooks/colab_phase10_smoke.ipynb` → `smoke_multi_agent_uq.py --backend llama_cpp --limit 3`.
