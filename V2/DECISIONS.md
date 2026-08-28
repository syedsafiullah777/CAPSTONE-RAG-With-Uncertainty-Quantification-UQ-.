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

**Verified Colab smoke:** n=3 frozen questions; T4 `llama_cpp`; status **PASS**; run_id `phase10_20260823T140737Z_ab9b33d4`; git `2f3882e`; threshold 0.55 (smoke); all cases `ANSWER`. Artefacts: `results/config/phase10_multi_agent_uq_smoke.json`, `project_record/evidence/phase10_validation.md`.

## 2026-08-23 — Phase 11 Streamlit live artefact

**Decision:** Implement one Streamlit app that calls the three existing V2 pipelines independently on the same original question (fresh or frozen). Reuse the Phase 6 KB and one backend instance. Do not look up precomputed answers, rebuild the KB, or change frozen sets. Treat original-plan “schema/logging” as already delivered by `RAGCaseResult`.

**Verified smoke:** 1 frozen + 1 fresh question; 3 architectures each; mock LLM + real retrieval; status **PASS**; run_id `phase11_20260823T222633Z_90aab3d6`. Streamlit HTTP 200. Artefacts: `results/config/phase11_live_smoke.json`, `project_record/evidence/phase11_validation.md`.

## 2026-08-23 — Phase 11 live failure display

**Decision:** In the live artefact only, treat missing evidence, empty generation, or a runtime exception (including ProxyError 403) as ERROR/UNAVAILABLE. Do not display ANSWER, do not keep a mock/fabricated answer, and do not assign confidence. Mock remains a UI/testing backend only.

**Verified:** `tests/test_phase11_live_artefact.py` **10 passed**; full suite **65 passed**. Phase 8–10 pipeline modules unchanged.

## 2026-08-24 — Phase 12 pilot (18 cases)

**Decision:** Run a small reproducible subset of the frozen 140 — first 6 CSV rows (Phase 4 seed-42 order) × 3 independent architectures = 18 cases — to validate checkpoint/resume/raw persistence before calibration lock and the 420-case benchmark. Use `uncertainty.smoke_threshold` 0.55 only, labelled **NOT LOCKED**. Cap the runner at 6 questions. Do not modify the frozen 140/40, lock T, or change the three RAG modules.

**Verified local:** 18/18 mock + real retrieval **PASS**; run_id `phase12_20260824T011511Z_415d75de`; resume-latest skipped 18 duplicates.

**Verified Colab raw (2026-08-26):** 18 unique T4 cases in `results/raw/phase12_pilot/phase12_20260826T183704Z_9773516a/cases.jsonl`. Latency 21.01–45.58 s. UQ 5 ANSWER + 1 ABSTAIN (`finqa_test_1000`, 0.5032 < 0.55). Threshold NOT LOCKED.

## 2026-08-26 — Phase 13 DEV calibration / threshold lock

**Decision:** Lock T only on the frozen FinQA **dev** 40, architecture `multi_agent_uq`, with a pre-registered rule: maximise selective accuracy subject to coverage ≥ 0.50 (tie: lowest T). Score the UQ draft against `program_answer`. Official `threshold.lock.json` requires `llama_cpp` + CUDA + n=40. Mock writes a candidate only.

**Verified local:** mock n=3 DEV cases **PASS**; run_id `phase13_20260826T190630Z_e3c9b993`; `locked=false`; mock cannot write the official lock.

**Verified Colab lock (2026-08-26):** 40/40 T4 `llama_cpp` cases in `results/raw/phase13_calibration/phase13_20260826T192003Z_7bcd6ed3/cases.jsonl`. Official **T=0.65** (`threshold.lock.json`; coverage 0.55; selective accuracy 12/22 ≈ 0.5455). Not tuned on the frozen 140. YAML `confidence_threshold` remains null. 420-case benchmark not started.

## 2026-08-26 — Phase 14 9-case benchmark validation

**Decision:** Prepare the 140×3 runner but execute only 3 frozen-test questions × 3 independent architectures = 9 cases. Load T=0.65 from `threshold.lock.json`. Never recalibrate. CLI refuses `--allow-full-420`. Incremental JSONL + checkpoint/resume + Drive sync when `V2_DRIVE_ROOT` is set.

**Verified local:** mock 9/9 **PASS** after retry; run_id `phase14_20260826T195616Z_f9550cce`; T=0.65 LOCKED; UQ 3/3 ABSTAIN (mock confidence < 0.65). Resume skipped 9.

**Verified Colab T4 (2026-08-26):** 9/9 PASS; run_id `phase14_20260826T200828Z_e91e588d`; Tesla T4; `llama_cpp`; Qwen3-8B Q4_K_M. Keep as engineering evidence. Full 420 not launched from this 9-case job.

## 2026-08-26 — Phase 15 final 420-case notebook

**Decision:** Create a dedicated Colab notebook and CLI for the official 140 × 3 = 420 evaluation. Keep the Phase 14 9-case notebook unchanged. Use locked T=0.65, Qwen3-8B Q4_K_M, `llama_cpp`, Colab GPU, shared Phase 6 KB, and a separate `phase15_benchmark` raw store. Do not execute 420 during notebook creation.

**Verified:** Notebook/entrypoint structure tests only. Frozen 140/40, T, V1, RAG modules, and retrieval unmodified. Official Colab 420 run **not launched**.

## 2026-08-27 — Phase 16 CPU evaluation of saved 420 cases

**Decision:** Score the canonical Phase 15 JSONL on CPU. Do not rerun RAG or Qwen3-8B. Do not use an LLM-as-judge (`judge_model: null`). Do not retune T=0.65 or the frozen 140/40. Do not start statistical tests (Phase 17).

**Metric choices:** numeric match to `program_answer` for answer correctness; CPU token-overlap for faithfulness (not official RAGAS); gold `file_name`/`context_id` for context precision/recall; coverage, selective accuracy, and unsupported-emitted rate for abstention.

**Verified:** 420/420 scored; run_id `phase16_20260826T235141Z_73fdbf58`; raw SHA-256 unchanged; T=0.65 lock SHA unchanged. Displayed correctness 32/140, 29/140, 32/140 (SA / MA / UQ). UQ selective accuracy 32/78. Full pytest **116 passed**.

## 2026-08-27 — Phase 16 post-hoc LLM-as-judge (not official RAGAS)

**Decision:** Add a separate resumable faithfulness judge over the frozen Phase 15 JSONL. Do not rerun RAG. Do not rewrite CPU Phase 16 tables. Do not feed gold context or gold answers to the judge. Use Qwen3-8B Q4_K_M, temperature 0, 32 tokens, 420 cases on Colab. Label: `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)`. Keep token-overlap secondary. Do not start Phase 17.

**Verified 2026-08-27:** implementation + local mock n=3 (pytest). Official Colab 420 **not launched** on this date.

## 2026-08-28 — Phase 16 official 420-case LLM-as-judge verified

**Decision:** Treat the copied Colab judge JSONL as the official post-hoc faithfulness artefact. Do not rerun RAG or the judge. Do not rewrite CPU Phase 16 tables. Do not start Phase 17. Label remains `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS**. Judge-call source of truth is the JSONL (`temperature=0.0`, `max_new_tokens=32`, `n_ctx=4096`), not fingerprint `model_config` 0.1 / 512.

**Verified:** run_id `phase16_judge_20260828T152623Z_06661255` **PASS**; 420/420 completed; 140 per architecture; 0 duplicates; 0 missing; 0 errors; 0 parse failures; all COMPLETED; `llama_cpp`; Qwen3-8B Q4_K_M; Tesla T4; `used_rag_rerun=false`; UQ `draft_answer`; UQ 78 ANSWER / 62 ABSTAIN; Phase 15 SHA unchanged. Means: SA 0.3241, MA 0.3484, UQ 0.3749, UQ ANSWER-only 0.6548. JSONL: `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl`.

## 2026-08-28 — Phase 17 paired statistics (frozen Phase 15/16)

**Decision:** Analyse RQ1–RQ3 on the frozen Phase 16 CPU rows joined to the official judge JSONL. Statistical unit = question (n=140), paired across architectures. Exact McNemar for binary paired outcomes; Wilcoxon for paired continuous scores after Shapiro fails; Spearman for confidence vs support; Holm within RQ families. Do not rerun RAG, Qwen, or the judge. Do not retune T=0.65. Do not start Phase 18. Label remains `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS**.

**Verified:** RQ1 McNemar SA vs MA displayed correctness p=0.6776 (**not significant**; 32/140 vs 29/140). RQ2 Spearman ρ=0.6988 (Holm significant); Mann–Whitney ANSWER vs ABSTAIN faithfulness Holm significant; Wilcoxon MA vs UQ faithfulness Holm p=0.4032 (**not significant**). RQ3 unsupported-emitted McNemar vs SA and MA Holm significant; coverage 78/140; selective accuracy 32/78; 2 false abstains. Phase 15/16 SHA-256 unchanged. Full suite **130 passed**.

## 2026-08-28 — Phase 17 dissertation figures (presentation only)

**Decision:** Redraw Phase 17 figures for dissertation presentation only. Do not rerun RAG, Qwen, the judge, or statistical tests. Do not change p-values, CIs, effect sizes, T=0.65, freeze files, or Phase 15/16 JSONL. Primary main-body figures: RQ1 Wilson-CI correctness (%); RQ2 UQ confidence vs LLM-as-judge faithfulness (custom/RAGAS-inspired, not official RAGAS); RQ3 coverage vs selective accuracy at locked T=0.65. Keep the three supporting plots for the appendix.

**Verified:** Figure renderer reads saved Phase 17 tables + frozen JSONL. Result-file SHA-256 unchanged after render. Phase 18 not started.

## 2026-08-28 — Phase 17 canonical figure set (PNG + PDF)

**Decision:** Keep exactly six figures in `results/metrics/phase17_figures/`, each as one PNG and one PDF. Remove SVG and superseded stems. Fix the overlapping RQ1 title. Spread stacked RQ2 points along x for display only. Index in `FIGURE_INDEX.md`. Do not recompute statistics.

**Verified:** 12 canonical files + index. 12 redundant exports removed. Result-file SHA-256 unchanged. Phase 18 not started on this date.

## 2026-08-28 — Phase 18 qualitative error analysis

**Decision:** Label all 420 frozen cases with a mutually exclusive taxonomy from recorded fields, plus a stratified qualitative sample (seed 18). Do not rerun RAG, Qwen, the judge, or Phase 17 tests. Do not retune T=0.65. Do not call numeric incorrectness hallucination. Do not start Phase 19. Metric label remains custom/RAGAS-inspired — **not official RAGAS**.

**Verified:** n_sample=81 cases / 42 questions; both false abstentions included; source SHA-256 unchanged. Tests `test_phase18_error_analysis.py` 4 passed. Full suite excluding `analyse()` 134 passed.

## 2026-08-28 — Phase 19 reproducibility audit

**Decision:** Phase 19 is a read-only reproducibility and research-integrity audit of the frozen chain (40 DEV → locked T=0.65 → frozen 140 → 420 cases → Phase 16/17/18). The dissertation evidence pack is **Phase 20**. Do not rerun RAG, Qwen, the judge, calibration, or statistical tests. Do not retune T. Do not modify V1 or frozen result files. Flag inconsistencies as NEEDS VERIFICATION rather than rewriting results. Do not commit Phase 15 raw JSONL or judge JSONL. Metric label remains custom/RAGAS-inspired — **not official RAGAS**.

**Verified:** Scientific chain PASS (0 FAIL). Frozen SHA-256 unchanged. 420/420. Figure-to-table and Phase 18 counts consistent. Drive archive, GitHub commit, judge fingerprint vs JSONL, and leftover `phase5_threshold_locked: false` remain NEEDS VERIFICATION. Phase 20 not started.

## 2026-08-28 — Phase 20 live artefact (not a dissertation pack)

**Decision:** Numbered Phase 20 is final live-artefact validation at locked **T=0.65**. The earlier plan that Phase 20 would be a dissertation evidence pack is superseded; no dissertation pack and no Phase 21 were started. The Streamlit app must always apply `threshold.lock.json`, run the three V2 RAG pipelines independently on the shared Phase 6 KB, and must not look up Phase 15 outputs. Do not rerun 420, calibration, the judge, or statistics. Do not retune T. Do not modify V1 or frozen result files. Official Colab T4 + Qwen3-8B + `llama_cpp` answers cannot be claimed from a local mock run. Metric label remains custom/RAGAS-inspired — **not official RAGAS**.

**Verified:** Live layer uses T=0.65; smoke 0.55 control removed. Mock demo run_id `phase20_20260828T180650Z_36ed9b1a`; insufficient-evidence UQ ABSTAIN at 0.5351; frozen SHA-256 unchanged; Streamlit HTTP 200. Tests `test_phase20_live_artefact.py` 6 passed. Full suite excluding `analyse()` 143 passed. Official T4 live demo **NEEDS VERIFICATION**.

## 2026-08-28 — Phase 20 Streamlit Benchmark Questions page

**Decision:** Add a read-only **Benchmark Questions** page to the existing Phase 20 Streamlit app so the frozen 140 can be browsed in a viva. Do not create a new phase. Do not rerun 420/judge/calibration/statistics. Do not modify the CSV, T=0.65, RAG architectures, or Phase 15–18 results. **Use this question in Live Demo** copies question text only (not FinQA gold, not Phase 15 answers). Benchmark Results is a read-only view of existing metric CSVs.

**Verified:** Catalogue loads 140 unique IDs matching `selected_140_questions.csv`; SHA-256 unchanged. `test_phase20_live_artefact.py` 7 passed. Pagination 21–40 of 140 on page 2.
