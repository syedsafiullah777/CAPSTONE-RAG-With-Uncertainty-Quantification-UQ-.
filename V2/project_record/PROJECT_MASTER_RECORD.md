# PROJECT MASTER RECORD — V2

**Authoritative chronological record of the implemented V2 project.**  
Plan intent is secondary to actual code, configuration, artefacts, and test results in this repository.

| Field | Value |
| --- | --- |
| Last updated | 2026-08-28 |
| Current completed phase | **Phase 17 complete:** paired statistics on frozen Phase 15/16 (**PASS**). Phase 16 CPU + official 420-case judge remain **PASS**. Phase 15 Drive archive still **NEEDS VERIFICATION**. |
| Next phase (not started) | **Phase 18 dissertation evidence pack** |
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
| Threshold lock | **LOCKED T = 0.65** (DEV 40 only; not tuned on frozen 140) | `results/config/threshold.lock.json` |
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
| Phase 12 pilot | 6 frozen IDs × 3 architectures = 18 cases; checkpoint/resume | local mock 18/18 PASS; Colab T4 18/18 PASS |
| Phase 12 local mock run ID | `phase12_20260824T011511Z_415d75de` | mock raw JSONL |
| Phase 12 Colab run ID | `phase12_20260826T183704Z_9773516a` | `phase12_smoke_test.json` (copied 2026-08-26) |
| Colab Phase 12 T4 / Qwen3-8B | **PASS** (2026-08-26T18:44:41Z); Tesla T4; `llama_cpp`; git `162fe3c` | `phase12_pilot_summary.json` |
| Phase 12 Colab raw JSONL (local) | **present** — 18 unique T4 cases | `results/raw/phase12_pilot/phase12_20260826T183704Z_9773516a/cases.jsonl` |
| Phase 12 artefacts | `phase12_runtime_fingerprint.json`, `phase12_smoke_test.json`, `phase12_pilot_summary.json` | local config copy verified |
| Phase 13 calibration | DEV 40 UQ; pre-registered T rule; official lock on Colab T4 | local mock n=3 PASS; Colab 40/40 PASS |
| Phase 13 local mock run ID | `phase13_20260826T190630Z_e3c9b993` | mock smoke (NOT LOCKED) |
| Phase 13 Colab run ID | `phase13_20260826T192003Z_7bcd6ed3` | `phase13_smoke_test.json` |
| Colab Phase 13 T4 / Qwen3-8B | **PASS** (2026-08-26T19:37:00Z); Tesla T4; `llama_cpp`; git `19368f1` | `phase13_calibration_summary.json` |
| Official `threshold.lock.json` | **LOCKED** T=0.65; coverage 0.55; selective accuracy 0.5455 (12/22) | `results/config/threshold.lock.json` |
| Phase 13 Colab raw JSONL (local) | **present** — 40 unique T4 DEV UQ cases | `results/raw/phase13_calibration/phase13_20260826T192003Z_7bcd6ed3/cases.jsonl` |
| Phase 14 runner | 140×3 prepared; 9-case engineering validation complete | `scripts/run_benchmark.py` |
| Phase 14 local mock 9-case | **PASS** (supporting engineering) | run_id `phase14_20260826T195616Z_f9550cce` |
| Phase 14 Colab T4 9-case | **PASS** (2026-08-26T20:11:45Z); Tesla T4; `llama_cpp`; Qwen3-8B Q4_K_M; git `20ee91e` | `phase14_smoke_test.json` |
| Phase 14 Colab run ID | `phase14_20260826T200828Z_e91e588d` | 9/9; T=0.65 LOCKED |
| Colab Phase 14 Drive sync (from summary) | reported `MyDrive/MSc-RAG/results/raw/phase14_benchmark/phase14_20260826T200828Z_e91e588d` | JSON artefact; Drive folder not re-checked locally |
| Phase 15 notebook | `notebooks/colab_phase15_full_benchmark.ipynb` | on GitHub (`cursor/empty-v2-workspace`) |
| Phase 15 entrypoint | `scripts/run_full_benchmark.py` | mock refused; n=140 |
| Phase 15 Colab T4 420-case | **PASS** (local inspect 2026-08-27); Tesla T4; `llama_cpp`; Qwen3-8B Q4_K_M; git `e3c6094` | `phase15_smoke_test.json` |
| Phase 15 Colab run ID | `phase15_20260826T203744Z_dae9c3a4` | 420/420; T=0.65 LOCKED |
| Phase 15 raw JSONL (local) | **present** — 420 unique keys, 0 duplicates, 0 errors | `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` |
| Phase 15 Drive sync (from summary) | reported `MyDrive/MSc-RAG/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4` | **NEEDS VERIFICATION** (not listed from this Mac) |
| Phase 16 evaluation | **PASS** (2026-08-26T23:51:41Z); CPU; no RAG/Qwen; 420/420 scored | `phase16_smoke_test.json` |
| Phase 16 run ID | `phase16_20260826T235141Z_73fdbf58` | scoring-only; raw `run_id` remains Phase 15 |
| Phase 16 processed JSONL | **present** — 420 scored rows | `results/processed/phase16_cases.jsonl` |
| Phase 16 metrics | displayed AC 32/140, 29/140, 32/140 (SA / MA / UQ); UQ selective acc. 32/78 | `results/metrics/phase16_summary.csv` |
| Phase 16 LLM judge | Official Colab 420 **PASS** (verified 2026-08-28); run_id `phase16_judge_20260828T152623Z_06661255` | `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl` |
| Phase 16 LLM judge means | SA 0.3241; MA 0.3484; UQ 0.3749 (all); UQ ANSWER-only 0.6548 | `phase16_judge_summary.csv`; **not official RAGAS** |
| Phase 17 statistics | **PASS** (2026-08-28); CPU; paired n=140; no RAG/judge rerun | `phase17_smoke_test.json` |
| Phase 17 RQ1 | SA 32/140 vs MA 29/140; McNemar p=0.6776 (not significant) | `results/metrics/phase17_tests.csv` |
| Phase 17 figures | **PASS** (2026-08-28); presentation only; statistics unchanged | `docs/phase17_figures.md`; `phase17_figure_render.json` |

### Architectures

1. **Single-Agent RAG** — implemented (Phase 8); local + Colab smoke **PASS** (n=3 each)
2. **Multi-Agent RAG** — implemented (Phase 9); local + Colab smoke **PASS** (n=3 each)
3. **Multi-Agent + UQ / abstention** — implemented (Phase 10); local + Colab smoke **PASS** (n=3 each); architecture `multi_agent_uq`

**NEEDS VERIFICATION / later phases:** confidence method weights; whether Arch3 reuses Arch2 draft/verify; dense vs hybrid retrieval; judge configuration.

### Test suite status (as of last update)

- Command: `PYTHONPATH=. pytest -q -k "not test_analyse_paired_140"` (2026-08-28, after Phase 17 figure refresh)
- Result: **130 passed**, 1 deselected (`analyse()` not re-run; no statistical tests recomputed). Official 420-case RAG job and official 420-case judge were **not** re-executed.

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
| Validation evidence | `project_record/evidence/phase1_validation.md` … `phase17_validation.md`; backup checklist `evidence/phase15_backup_manifest.md` |
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
24. **Phase 11 output-quality (2026-08-24):** Prompts now distinguish final/ending value vs absolute change vs ROI/percentage change, and require the answer once. `clean_generated_answer` collapses repeated sentences. Retrieval, UQ method, and smoke threshold 0.55 NOT LOCKED unchanged. Additional numerical live case: frozen `finqa_test_1012`. Local mock smoke 3/3 **PASS**; Colab T4/Qwen3 re-run **NEEDS VERIFICATION**. Phase 12 not started.
25. **Phase 12 pilot (2026-08-24):** First 6 frozen-140 rows × 3 independent architectures = 18 cases. Runner writes append-only JSONL, checkpoints after each case, resumes by `{architecture}:{question_id}`, skips completed, retries failed, refuses overwrite and n>6. Smoke threshold 0.55 **NOT LOCKED**. Frozen 140/40 and Phase 8–10 architectures unchanged. Local mock 18/18 **PASS** (`phase12_20260824T011511Z_415d75de`); resume skipped 18. Colab T4/Qwen3-8B **NEEDS VERIFICATION**. Calibration lock and 420-case benchmark not started.
26. **Phase 12 Colab T4 verification (2026-08-26):** User copied Colab config results. Observed: backend `llama_cpp`, device `cuda`, GPU Tesla T4, Qwen3-8B Q4_K_M, run_id `phase12_20260826T183704Z_9773516a`, status **PASS**, 18/18 completed, 0 failed, threshold 0.55 **NOT LOCKED**, git `162fe3c`, recorded 2026-08-26T18:44:41Z. Local `results/raw/` does **not** contain that Colab run directory (only the mock run). Per-case T4 answers/confidence/latency therefore not verified locally. Calibration lock / 420-case benchmark still not started.
27. **Phase 12 Colab raw JSONL archived (2026-08-26):** User copied raw files. 18 unique T4 cases verified: 4 evidence chunks each, 0 errors, latency 21.01–45.58 s, seed 42. UQ: 5 ANSWER + 1 genuine ABSTAIN on `finqa_test_1000` (confidence 0.5032 < 0.55 NOT LOCKED). Files landed in the old mock folder name; canonical copy is `results/raw/phase12_pilot/phase12_20260826T183704Z_9773516a/`. Mock JSONL in that old folder is no longer present. Phase 13+ not started.
28. **Phase 13 DEV calibration (2026-08-26):** Pre-registered T rule = max selective accuracy with coverage ≥ 0.50 (tie: lowest T), on frozen FinQA **dev** 40 only, architecture `multi_agent_uq`. Official lock requires `llama_cpp` + CUDA + n=40. Mock n=3 smoke **PASS** (`phase13_20260826T190630Z_e3c9b993`); `threshold.lock.json` **not** written. Frozen 140/40 CSVs unmodified. 420-case benchmark not started. Colab official lock **NEEDS VERIFICATION**.
29. **Phase 13 Colab T4 official lock (2026-08-26):** User copied Colab config + raw. Observed: backend `llama_cpp`, device `cuda`, GPU Tesla T4, Qwen3-8B Q4_K_M, run_id `phase13_20260826T192003Z_7bcd6ed3`, 40/40 DEV `multi_agent_uq` cases, 0 errors, `used_frozen_test_140=false`, IDs match Phase 5 manifest. Locked **T=0.65** (coverage 0.55, selective accuracy 12/22 ≈ 0.5455). YAML `confidence_threshold` remains null; Phase 12 still uses smoke 0.55. Phase 14 must load `threshold.lock.json`. 420-case benchmark not started.
30. **Phase 14 9-case benchmark validation (2026-08-26):** Implement the 140×3 runner but validate only first 3 frozen-140 rows × 3 independent architectures = 9 cases, using locked T=0.65 from `threshold.lock.json`. Do not recalibrate. Do not launch 420 (`--allow-full-420` refused). Local mock 9/9 **PASS** after retrying ProxyError 403 (`phase14_20260826T195616Z_f9550cce`); UQ 3/3 ABSTAIN at mock confidence < 0.65. Resume skipped 9. Frozen 140/40 and Phase 8–10 modules unchanged. Colab T4 9-case **NEEDS VERIFICATION**. Full 420 not started.
31. **Phase 14 Colab T4 9-case + next execution is 420 (2026-08-26):** User copied Colab config + raw. Observed: backend `llama_cpp`, device `cuda`, GPU Tesla T4, Qwen3-8B Q4_K_M, run_id `phase14_20260826T200828Z_e91e588d`, **9/9 PASS**, T=0.65 LOCKED, Drive sync reported to `MyDrive/MSc-RAG/results/raw/phase14_benchmark/phase14_20260826T200828Z_e91e588d`. UQ: 2 ANSWER + 1 ABSTAIN (`finqa_test_1000`, 0.5032 < 0.65). The 9-case run is **engineering validation evidence only** — do not add another 9-case gate. **Next execution:** final **140 × 3 = 420** on Colab GPU with the same lock, KB, and retrieval. This update does not launch 420. Frozen 140/40 and T are unchanged.
32. **Phase 15 420-case notebook created (2026-08-26):** Official evaluation vehicle is `notebooks/colab_phase15_full_benchmark.ipynb` + `scripts/run_full_benchmark.py` (always n=140, `allow_full=True`, mock refused). Raw store is `results/raw/phase15_benchmark/` so `--resume-latest` cannot pick the Phase 14 9-case run. Locked T=0.65, Qwen3-8B Q4_K_M, `llama_cpp`, Colab GPU, shared Phase 6 KB, identical retrieval. Incremental JSONL, Drive checkpoint, resume, retry failures, duplicate prevention, progress logs, completion summary. Phase 14 9-case notebook **unchanged**. Frozen 140/40, T, V1, RAG modules, and retrieval **unchanged**. 420-case Colab execution **not launched**.
33. **Phase 15 Colab 420 locally verified (2026-08-27):** Inspected user-copied artefacts at `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/`. Observed **420/420** unique keys, 0 duplicates, 0 missing, 0 errors; 140 frozen-test IDs; 140 cases per architecture; T=0.65 LOCKED; Tesla T4 `llama_cpp` Qwen3-8B Q4_K_M. JSONL not rewritten. Drive folder not listed from this Mac (**NEEDS VERIFICATION**). Backup checklist: `project_record/evidence/phase15_backup_manifest.md`. Next: Phase 16 metrics — do not retune T or the frozen 140.
34. **Phase 16 CPU evaluation (2026-08-26/27):** Score the frozen Phase 15 JSONL only. No RAG/Qwen/GPU. `judge_model` remains null (not official RAGAS). Metrics: numeric `program_answer` match; CPU token-overlap faithfulness; gold file/`context_id` context P/R; coverage, selective accuracy, unsupported-emitted rate. Observed displayed correctness: Single-Agent **32/140**, Multi-Agent **29/140**, UQ **32/140** displayed / **34/140** claim; UQ 78 ANSWER / 62 ABSTAIN; selective accuracy 32/78. Context P/R identical across architectures (0.4304 / 0.9000). Do **not** claim Multi-Agent improves accuracy. Phase 17 statistics not started.
35. **Phase 16 LLM-as-judge pass prepared (2026-08-27):** Separate post-hoc faithfulness job over the frozen Phase 15 JSONL. Qwen3-8B Q4_K_M `llama_cpp` on Colab, temp 0, 32 new tokens, 420 calls. Claim = displayed answer except UQ `draft_answer`. No gold context/answer in the prompt. Label: `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not** official RAGAS. Token-overlap remains secondary. CPU Phase 16 tables are not rewritten. Official Colab 420 **not launched** on this date. Phase 17 not started.
36. **Phase 16 official 420-case LLM-as-judge verified (2026-08-28):** User copied Colab artefacts. Local inspect of `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl`: **420/420** unique keys, 140 per architecture, 0 duplicates, 0 missing, 0 errors, 0 parse failures, all COMPLETED; `llama_cpp`; Qwen3-8B Q4_K_M; Tesla T4; `used_rag_rerun=false`; no gold context/answer; UQ `draft_answer`; UQ 78 ANSWER / 62 ABSTAIN; Phase 15 SHA unchanged. Mean faithfulness: SA 0.3241, MA 0.3484, UQ 0.3749, UQ ANSWER-only 0.6548. JSONL records `temperature=0.0`, `max_new_tokens=32`, `n_ctx=4096` (source of truth). Do not use fingerprint `model_config` 0.1 / 512 as judge-call settings. **Not official RAGAS.** CPU Phase 16 tables unchanged. Phase 17 not started on this date. Drive folder **NEEDS VERIFICATION**.
37. **Phase 17 paired statistics (2026-08-28):** CPU analysis of frozen Phase 16 scored cases + official judge JSONL. Statistical unit = question (n=140), paired across architectures. Confirmatory RQ1 McNemar SA vs MA displayed correctness p=0.6776 (**not significant**). RQ2: Spearman confidence vs LLM-as-judge faithfulness ρ=0.6988 (Holm significant); Mann–Whitney ANSWER vs ABSTAIN faithfulness Holm significant; paired Wilcoxon MA vs UQ faithfulness **not** significant. RQ3: unsupported-emitted McNemar vs SA and MA Holm significant; coverage 78/140; selective accuracy 32/78; 2 false abstains. **Not official RAGAS.** Phase 15/16 JSONL SHAs unchanged. Phase 18 not started.
38. **Phase 17 figure refresh (2026-08-28):** Presentation-only redraw of six dissertation figures from saved Phase 17 tables. No RAG/Qwen/judge rerun. No statistical tests recomputed. Result-file SHA-256 unchanged. Primary: RQ1 Wilson-CI correctness (%); RQ2 UQ confidence vs custom/RAGAS-inspired LLM-as-judge faithfulness; RQ3 coverage vs selective accuracy at locked T=0.65. Appendix: McNemar counts, faithfulness boxplot, UQ outcome counts. Phase 18 not started.

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

## Phase 11 — Output-quality (no-repeat, ROI vs value)

- **Date:** 2026-08-24
- **Objective:** Stop Multi-Agent/UQ answer repetition and incorrect final-value vs ROI answers without changing retrieval or UQ.
- **Why required:** Colab T4/Qwen3-8B live was working, but answers could repeat and a numerical question could report ending investment value instead of ROI.
- **Work completed:**
  - Prompts require one answer and distinguish final value / absolute change / ROI or percentage change
  - `collapse_repeated_answers()` keeps one copy of a repeated sentence
  - Verification still scores support, now including whether the asked quantity type is reported (same score formula)
  - Notebook/smoke now include `finqa_test_1000`, `finqa_test_1012`, and the insufficient-evidence question
- **Technical decisions:** Retrieval, model, architectures, UQ method, and smoke threshold 0.55 NOT LOCKED unchanged. Frozen 140/40 and V1 unchanged.
- **Files created/modified:**
  - `V2/config/prompts.yaml`, `V2/src/rag/prompts.py`, `V2/src/rag/text_utils.py`
  - `V2/src/rag/live.py`, `V2/scripts/smoke_live_artefact.py`, `V2/notebooks/colab_phase11_live.ipynb`
  - `V2/tests/test_phase9_multi_agent.py`, `V2/tests/test_phase11_live_artefact.py`
  - `V2/project_record/evidence/phase11_validation.md`, `V2/project_record/PROJECT_MASTER_RECORD.md`
- **Tests/validation:**
  - Full suite **77 passed**
  - Mock smoke **PASS** — run_id `phase11_20260824T003215Z_9a838089`
  - UQ: 1000 ANSWER 0.6185; 1012 ANSWER 0.5886; insufficient ABSTAIN 0.5351
  - Colab T4/Qwen3-8B after this fix — **NEEDS VERIFICATION**
- **Actual outcome:** Output handling is stricter. Mock answers cannot prove Qwen3 numerical correctness. Phase 12 not started.
- **Problems encountered:** Qwen3 can tile the same answer; ROI vs cumulative value confusion on Snap-on S&P graph questions.
- **Problems resolved:** Prompt quantity rules + repeat collapse. UQ behaviour left as-is.
- **Remaining issues:** Re-run `notebooks/colab_phase11_live.ipynb` on Colab T4 to confirm Qwen3 answers are concise and use ROI/percentage where asked.
- **Dissertation relevance:** Live answers must be examiner-readable and numerically well-specified.
- **Evidence/source file paths:** `V2/results/config/phase11_live_smoke.json`
- **Validation evidence:** `V2/project_record/evidence/phase11_validation.md`
- **Backup status:**
  - Colab: output-quality T4 re-run **NEEDS VERIFICATION**
  - Google Drive: **NEEDS VERIFICATION**
  - Local: verified — tests, mock smoke, notebook, evidence updated 2026-08-24
  - GitHub: output-quality files **uncommitted**

---

## Phase 12 — Pilot (18 cases)

- **Date:** 2026-08-24
- **Objective:** Validate end-to-end experimental stability on a small reproducible subset of the frozen 140 before calibration lock and the 420-case benchmark.
- **Why required:** The 420-case job needs proven checkpoint/resume, raw persistence, a common schema, and per-case error handling. A 18-case pilot is the approved gate.
- **Work completed:**
  - Pilot subset = first 6 rows of `selected_140_questions.csv` (Phase 4 seed-42 order): `finqa_test_1000`, `1012`, `1017`, `1027`, `1039`, `1040`
  - Manifest `data/final/pilot_subset_manifest.json` (does not replace the 140 CSV)
  - `src/run/store.py` append-only JSONL + checkpoint; skip completed; retry failed; refuse silent overwrite
  - `src/run/pilot.py` / `scripts/run_pilot.py` run the three architectures independently (no chaining)
  - Colab notebook `notebooks/colab_phase12_pilot.ipynb` with Drive sync and `--resume-latest`
  - Local mock 18/18 **PASS**; resume-latest skipped 18 duplicates
- **Technical decisions:**
  - Cap at 6 questions / 18 cases; refuse 140/420 from this script
  - UQ uses `uncertainty.smoke_threshold` 0.55 labelled **smoke/demo — NOT LOCKED**
  - Do not create `threshold.lock.json`
  - Phase 8–10 architecture modules not modified
- **Files created/modified:**
  - `V2/src/run/subset.py`, `store.py`, `pilot.py`, `__init__.py`
  - `V2/scripts/run_pilot.py`
  - `V2/tests/test_phase12_pilot.py`
  - `V2/notebooks/colab_phase12_pilot.ipynb`
  - `V2/data/final/pilot_subset_manifest.json`
  - `V2/docs/phase12_pilot.md`
  - `V2/config/experiment.yaml` (`phase12_pilot_n`, `phase12_entrypoint`)
  - `V2/project_record/evidence/phase12_validation.md`
- **Tests/validation:**
  - `tests/test_phase12_pilot.py` **10 passed**
  - Full suite **87 passed**
  - Local mock pilot **PASS** — run_id `phase12_20260824T011511Z_415d75de`; 18/18; 4 chunks each; UQ 0.5637–0.6349 ANSWER at 0.55 NOT LOCKED
  - Resume **PASS** — 0 executed / 18 skipped; 18 unique keys
  - Colab T4 / Qwen3-8B — **NEEDS VERIFICATION**
- **Actual outcome:** Pilot infrastructure is stable on mock + real retrieval. Mock answers cannot prove Qwen3 quality or T4 latency. Threshold remains unlocked. 420-case benchmark not started.
- **Problems encountered:** This session cannot execute Colab T4. Local first-case latency 3.43s was embedding-model load, not Qwen3.
- **Problems resolved:** Resume/duplicate prevention verified on the real 18-case store. Runner refuses n>6 and a locked `confidence_threshold`.
- **Remaining issues:** Run `notebooks/colab_phase12_pilot.ipynb` on Colab GPU after pushing V2; copy raw JSONL + checkpoint to Drive; then start Phase 13+ only after that verification if required.
- **Dissertation relevance:** Shows the 420-case job can survive Colab disconnects without restarting from question 1, and that T is not tuned on the test set.
- **Evidence/source file paths:**
  - `V2/results/raw/phase12_pilot/phase12_20260824T011511Z_415d75de/cases.jsonl`
  - `V2/results/config/phase12_smoke_test.json`
  - `V2/results/config/phase12_pilot_summary.json`
- **Validation evidence:** `V2/project_record/evidence/phase12_validation.md`
- **Backup status:**
  - Colab: T4 / Qwen3-8B pilot **NEEDS VERIFICATION**
  - Google Drive: **NEEDS VERIFICATION** (notebook section 7 copies raw + checkpoints when run)
  - Local: verified — tests, mock 18/18 raw JSONL, checkpoint, evidence, master record
  - GitHub: Phase 12 files **uncommitted**

---

## Phase 12 — Colab T4 verification

- **Date:** 2026-08-26
- **Objective:** Record the real Colab T4 / Qwen3-8B pilot after the user copied Phase 12 config results.
- **Why required:** Local mock 18/18 could not prove T4/`llama_cpp` execution. Config files now contain that run.
- **Work completed:** Read `phase12_smoke_test.json`, `phase12_pilot_summary.json`, `phase12_runtime_fingerprint.json` (local timestamps 2026-08-26 19:46). Updated evidence and this record. Did not start Phase 13+.
- **Technical decisions:** Treat the three config files as verified Colab evidence. Do not invent per-case answers or UQ scores without the Colab `cases.jsonl`.
- **Files created/modified:**
  - `V2/project_record/evidence/phase12_validation.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
  - `V2/PROJECT_CONTEXT.md`, `V2/README.md`, `V2/docs/IMPLEMENTATION_PLAN.md`, `V2/DECISIONS.md`
- **Tests/validation:**
  - Colab summary **PASS** — run_id `phase12_20260826T183704Z_9773516a`; 18/18; Tesla T4; `llama_cpp`; threshold 0.55 NOT LOCKED
  - Local Colab raw JSONL — **NEEDS VERIFICATION** (directory absent)
- **Actual outcome:** End-to-end T4 pilot completed according to the copied summary. Raw T4 cases are not in the local archive.
- **Problems encountered:** Config copy does not include `cases.jsonl` or the Colab checkpoint file.
- **Problems resolved:** Colab T4 execution is no longer NEEDS VERIFICATION at the summary level.
- **Remaining issues:** Copy `phase12_20260826T183704Z_9773516a` from Colab or Drive into local `results/raw/phase12_pilot/` and `results/checkpoints/phase12_pilot/`. Drive path still **NEEDS VERIFICATION**. Do not lock the threshold. Do not start the 420-case benchmark.
- **Dissertation relevance:** Confirms the 18-case pilot ran on the official compute path (Colab T4, Qwen3-8B, `llama_cpp`) with T still unlocked.
- **Evidence/source file paths:**
  - `V2/results/config/phase12_smoke_test.json`
  - `V2/results/config/phase12_pilot_summary.json`
  - `V2/results/config/phase12_runtime_fingerprint.json`
- **Validation evidence:** `V2/project_record/evidence/phase12_validation.md`
- **Backup status:**
  - Colab: verified from copied config — T4 `llama_cpp` 18/18 **PASS** (`phase12_20260826T183704Z_9773516a`); Colab `/content` is ephemeral
  - Google Drive: **NEEDS VERIFICATION**
  - Local: verified — three Phase 12 config JSONs; Colab raw JSONL **not copied**
  - GitHub: config JSONs gitignored by default; evidence/master-record updates uncommitted

---

## Phase 12 — Colab raw JSONL archived

- **Date:** 2026-08-26
- **Objective:** Archive and inspect the Colab T4 per-case raw results.
- **Why required:** Config summaries do not contain answers, evidence, confidence, or latency.
- **Work completed:** Verified 18-line `cases.jsonl` (run_id `phase12_20260826T183704Z_9773516a`, `llama_cpp`, Tesla T4). Copied out of the misnamed mock folder into the matching run-id directory. Updated evidence.
- **Technical decisions:** Do not treat this 18-case file as the 420-case benchmark or as a threshold lock. Report ABSTAIN as the existing UQ rule.
- **Files created/modified:**
  - Canonical raw: `V2/results/raw/phase12_pilot/phase12_20260826T183704Z_9773516a/`
  - Checkpoint copy: `V2/results/checkpoints/phase12_pilot/phase12_20260826T183704Z_9773516a.json`
  - `V2/project_record/evidence/phase12_validation.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
- **Tests/validation:** 18 unique keys; schema fields present; 4 chunks each; 0 errors; UQ 5 ANSWER / 1 ABSTAIN; threshold 0.55 NOT LOCKED
- **Actual outcome:** End-to-end T4 pilot raw results are now local. One UQ abstention on `finqa_test_1000`.
- **Problems encountered:** Raw files were copied into `phase12_20260824T011511Z_415d75de`, overwriting the local mock JSONL.
- **Problems resolved:** Canonical Colab run directory created with the correct run_id.
- **Remaining issues:** Google Drive copy **NEEDS VERIFICATION**. Some generated answers still verbose or self-report “evidence insufficient” while `decision=ANSWER` (Single-Agent / Multi-Agent). Optional later prompt work; not a Phase 13 start.
- **Dissertation relevance:** Documents real T4 latency (~21–46 s/case), retrieval+verify+UQ behaviour, and that T remains unlocked.
- **Evidence/source file paths:** `V2/results/raw/phase12_pilot/phase12_20260826T183704Z_9773516a/cases.jsonl`
- **Validation evidence:** `V2/project_record/evidence/phase12_validation.md`
- **Backup status:**
  - Colab: T4 18/18 **PASS**; `/content` ephemeral
  - Google Drive: **NEEDS VERIFICATION**
  - Local: verified — Colab raw JSONL + checkpoint under the correct run_id
  - GitHub: raw JSONL gitignored; evidence/master-record updates uncommitted

---

## Phase 13 — DEV calibration / threshold lock

- **Date:** 2026-08-26
- **Objective:** Select and (on Colab) lock the UQ abstention threshold T on the frozen FinQA **dev** 40-question set, using a pre-registered rule. Never peek at the frozen 140.
- **Why required:** RQ3 and the 420-case benchmark need a locked T that is not tuned on test.
- **Work completed:**
  - Numeric matcher for `program_answer`
  - Selector: max selective accuracy among T with coverage ≥ 0.50; tie = lowest T
  - Runner: 40 DEV `multi_agent_uq` cases, checkpoint/resume, no test IDs
  - Official lock only if `llama_cpp` + CUDA + n=40; mock writes candidate only
  - Colab notebook `notebooks/colab_phase13_calibration.ipynb`
- **Technical decisions:** Do not change Phase 8–10 architecture modules. Do not lock from mock. Do not run 420 cases. Score the UQ **draft** (not the abstention message) against gold.
- **Files created/modified:**
  - `V2/src/evaluation/numeric.py`
  - `V2/src/calibration/data.py`, `select.py`, `lock.py`, `runner.py`
  - `V2/scripts/run_calibration.py`
  - `V2/tests/test_phase13_calibration.py`
  - `V2/notebooks/colab_phase13_calibration.ipynb`
  - `V2/docs/phase13_calibration_lock.md`
  - `V2/project_record/evidence/phase13_validation.md`
- **Tests/validation:**
  - Phase 13 tests **7 passed**; full suite **94 passed**
  - Local mock n=3 **PASS** — run_id `phase13_20260826T190630Z_e3c9b993`; locked=false
  - `threshold.lock.json` **absent**
  - Colab 40-case official lock — **NEEDS VERIFICATION**
- **Actual outcome:** Calibration runner is ready. T is still **not** officially locked.
- **Problems encountered:** Mock drafts are not Qwen3 answers, so a mock T (here candidate 0.0 on n=3) must not be frozen.
- **Problems resolved:** Lock guards refuse mock, Mac MPS, n<40, and frozen-test IDs.
- **Remaining issues:** Push V2 and run `notebooks/colab_phase13_calibration.ipynb` on Colab T4; copy `threshold.lock.json` + raw JSONL locally. Then Phase 14 (420) can read the lock.
- **Dissertation relevance:** Documents DEV-only T selection and the coverage/selective-accuracy trade-off before test evaluation.
- **Evidence/source file paths:**
  - `V2/results/config/phase13_smoke_test.json`
  - `V2/results/config/threshold.candidate.json`
  - `V2/results/raw/phase13_calibration/phase13_20260826T190630Z_e3c9b993/cases.jsonl`
- **Validation evidence:** `V2/project_record/evidence/phase13_validation.md`
- **Backup status:**
  - Colab: official 40-case lock **NEEDS VERIFICATION**
  - Google Drive: **NEEDS VERIFICATION**
  - Local: verified — tests, mock n=3, candidate (NOT LOCKED), evidence, master record
  - GitHub: Phase 13 files **uncommitted**

---

## Phase 13 — Colab T4 official threshold lock

- **Date:** 2026-08-26
- **Objective:** Archive and record the official DEV-only threshold lock from Colab T4.
- **Why required:** RQ3 and the 420-case benchmark need a locked T that is not tuned on the frozen 140.
- **Work completed:** Verified Colab config + lock + 40-line `cases.jsonl` (run_id `phase13_20260826T192003Z_7bcd6ed3`). Copied raw files out of the misnamed mock folder into the matching run-id directory. Updated evidence.
- **Technical decisions:** Keep `experiment.yaml` `uncertainty.confidence_threshold` as `null` so Phase 12 cannot pick up a yaml-locked value. Official T lives in `threshold.lock.json`. Do not start the 420-case benchmark. Do not retune T on test. Report modest DEV selective accuracy honestly.
- **Files created/modified:**
  - Canonical raw: `V2/results/raw/phase13_calibration/phase13_20260826T192003Z_7bcd6ed3/`
  - Checkpoint copy: `V2/results/checkpoints/phase13_calibration/phase13_20260826T192003Z_7bcd6ed3.json`
  - User-copied config: `threshold.lock.json`, `threshold.candidate.json`, `phase13_*.json`
  - `V2/project_record/evidence/phase13_validation.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
- **Tests/validation:**
  - Colab summary **PASS** — 40/40; Tesla T4; `llama_cpp`; Qwen3-8B Q4_K_M; git `19368f1`
  - 40 unique DEV keys; 0 `finqa_test_*`; IDs match Phase 5 `selected_ids`; 4 chunks each; 0 errors
  - Latency 19.41–47.95 s (sum 1016.18 s)
  - Collection gate at smoke 0.55: 28 ANSWER / 12 ABSTAIN
  - Locked T=0.65: coverage 0.55 (22 ANSWER / 18 ABSTAIN); selective accuracy 12/22 ≈ 0.5455
- **Actual outcome:** Official threshold is **LOCKED at 0.65** on FinQA DEV only.
- **Problems encountered:** Raw files were copied into `phase13_20260826T190630Z_e3c9b993`, overwriting the local mock JSONL. Lock `question_ids_sha256` uses newline-joined IDs (`da212641…`); Phase 5 manifest SHA (`b229d453…`) is JSON-compact of the same ID list — sets match.
- **Problems resolved:** Canonical Colab run directory created with the correct run_id. Lock payload has `locked: true`, `source_split: dev`, `used_frozen_test_140: false`.
- **Remaining issues:** Google Drive copy **NEEDS VERIFICATION**. Phase 14 must load T from `threshold.lock.json`. Live/pilot smoke path still uses 0.55 unless given an explicit override.
- **Dissertation relevance:** Records DEV-only T selection (coverage floor 0.50, max selective accuracy, lowest-T tie-break) before any 140-question test evaluation. Selective accuracy on DEV at T=0.65 is 54.5% with 55% coverage — not a test-set claim.
- **Evidence/source file paths:**
  - `V2/results/config/threshold.lock.json`
  - `V2/results/config/phase13_smoke_test.json`
  - `V2/results/config/phase13_calibration_summary.json`
  - `V2/results/raw/phase13_calibration/phase13_20260826T192003Z_7bcd6ed3/cases.jsonl`
- **Validation evidence:** `V2/project_record/evidence/phase13_validation.md`
- **Backup status:**
  - Colab: verified from copied artefacts — T4 `llama_cpp` 40/40 **PASS**; lock T=0.65; `/content` is ephemeral
  - Google Drive: **NEEDS VERIFICATION**
  - Local: verified — lock file, config JSONs, Colab raw JSONL under the correct run_id
  - GitHub: `threshold.lock.json` is git-allowed; raw JSONL gitignored; evidence/master-record updates uncommitted

---

## Phase 14 — Benchmark runner / 9-case validation

- **Date:** 2026-08-26
- **Objective:** Prepare the 140-question × 3-architecture benchmark runner and validate it on 9 cases only.
- **Why required:** The 420-case job needs proven checkpoint/resume, locked T=0.65, independent architectures, Drive persistence, and duplicate prevention before a multi-hour Colab run.
- **Work completed:**
  - Read-only load of `threshold.lock.json` (T=0.65; refuse recalibration)
  - Runner: frozen test 140 path implemented; this phase caps at 3 questions / 9 cases
  - Incremental JSONL, checkpoint, resume, retry failed, skip completed, refuse overwrite
  - Optional Drive sync via `V2_DRIVE_ROOT`
  - Colab notebook `notebooks/colab_phase14_benchmark_validation.ipynb` (`llama_cpp`, n=3 only)
- **Technical decisions:** Load T from the Phase 13 lock file, not yaml. Pass T only into `multi_agent_uq` as an override. Keep yaml `confidence_threshold` null. CLI refuses `--allow-full-420`. Do not change Phase 8–10 modules. Mock UQ abstentions are not Qwen3 evidence.
- **Files created/modified:**
  - `V2/src/run/benchmark.py`, `V2/src/run/drive_sync.py`
  - `V2/src/calibration/lock.py` (read-only `load_official_lock`)
  - `V2/scripts/run_benchmark.py`
  - `V2/tests/test_phase14_benchmark.py`
  - `V2/notebooks/colab_phase14_benchmark_validation.ipynb`
  - `V2/docs/phase14_benchmark.md`
  - `V2/project_record/evidence/phase14_validation.md`
- **Tests/validation:**
  - Phase 14 tests **11 passed**; full suite **105 passed**
  - Local mock 9/9 **PASS** — run_id `phase14_20260826T195616Z_f9550cce`; T=0.65 LOCKED; resume skipped 9
  - `--allow-full-420` refused
  - Colab T4 9-case — **NEEDS VERIFICATION**
- **Actual outcome:** Benchmark runner is ready. 9-case local validation passed. Full 420-case run was not launched.
- **Problems encountered:** First local pass failed all 9 cases with `ProxyError: 403 Forbidden` (embedding/retrieval network in sandbox).
- **Problems resolved:** `--resume-latest` retried failed keys and completed 9/9 with 4 chunks each.
- **Remaining issues:** Push V2 and run `notebooks/colab_phase14_benchmark_validation.ipynb` on Colab T4; copy raw JSONL to Drive. Then a later step can launch 420. Google Drive 9-case archive **NEEDS VERIFICATION**.
- **Dissertation relevance:** Shows the 420-case job can use locked T=0.65 on the frozen test set without retuning T, and can survive interruption without restarting from question 1.
- **Evidence/source file paths:**
  - `V2/results/config/phase14_smoke_test.json`
  - `V2/results/config/phase14_benchmark_summary.json`
  - `V2/results/raw/phase14_benchmark/phase14_20260826T195616Z_f9550cce/cases.jsonl`
  - `V2/results/config/threshold.lock.json`
- **Validation evidence:** `V2/project_record/evidence/phase14_validation.md`
- **Backup status:**
  - Colab: 9-case T4 **NEEDS VERIFICATION**
  - Google Drive: **NEEDS VERIFICATION** (local run used `--no-drive-sync`)
  - Local: verified — tests, mock 9/9 PASS, lock T=0.65 unchanged, evidence, master record
  - GitHub: Phase 14 files **uncommitted**

---

## Phase 14 — Colab T4 9-case archived; next execution is 420

- **Date:** 2026-08-26
- **Objective:** Record the completed Colab T4 9-case run as engineering validation evidence and lock the **next** job as the final 420-case benchmark.
- **Why required:** The 9-case gate is finished. Repeating it would waste GPU time and is not a research requirement. The dissertation benchmark is 140 × 3 = 420.
- **Work completed:** Inspected user-copied Colab config + 9-line `cases.jsonl` (run_id `phase14_20260826T200828Z_e91e588d`). Updated plan, master record, and Phase 14 evidence. Did **not** re-run 9 cases. Did **not** launch 420.
- **Technical decisions:** Keep the 9-case results as supporting engineering evidence. Next execution uses locked T=0.65, Qwen3-8B Q4_K_M, `llama_cpp`, Colab GPU, shared Phase 6 KB, identical retrieval. Incremental JSONL, Drive checkpoints, resume, retry genuine failures, duplicate prevention, progress logs, raw preservation.
- **Files created/modified:**
  - `V2/project_record/evidence/phase14_validation.md`
  - `V2/docs/IMPLEMENTATION_PLAN.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
  - `V2/docs/phase14_benchmark.md`
- **Tests/validation:** No new pytest or smoke. Observed Colab artefacts: **9/9 PASS**; T=0.65; 4 chunks; 0 errors; latency 16.47–43.16 s; UQ 2 ANSWER / 1 ABSTAIN (`finqa_test_1000`).
- **Actual outcome:** 9-case engineering validation is complete. Full 420 is the next execution and is **not** started.
- **Problems encountered:** Colab raw files were copied into folder name `phase14_20260826T195616Z_f9550cce`; JSONL `run_id` is `phase14_20260826T200828Z_e91e588d`.
- **Problems resolved:** Evidence records the Colab run_id from the JSON, not the folder name.
- **Remaining issues:** Launch 420 on Colab GPU when ready (not in this update). Local Drive tree not independently re-listed. Do not rerun 9 cases.
- **Dissertation relevance:** 9-case T4 results demonstrate locked T and independent architectures on the official compute path; they are not the 420-case test evaluation.
- **Evidence/source file paths:**
  - `V2/results/config/phase14_smoke_test.json`
  - `V2/results/config/phase14_benchmark_summary.json`
  - `V2/results/config/phase14_runtime_fingerprint.json`
  - `V2/results/raw/phase14_benchmark/phase14_20260826T195616Z_f9550cce/cases.jsonl` (Colab 9 T4 cases; run_id in file `phase14_20260826T200828Z_e91e588d`)
- **Validation evidence:** `V2/project_record/evidence/phase14_validation.md`
- **Backup status:**
  - Colab: T4 9/9 **PASS** (`phase14_20260826T200828Z_e91e588d`); `/content` ephemeral
  - Google Drive: reported in summary JSON — `MyDrive/MSc-RAG/results/raw/phase14_benchmark/phase14_20260826T200828Z_e91e588d` (folder not re-listed from this machine)
  - Local: verified — Colab config JSONs + 9-line T4 JSONL
  - GitHub: evidence/plan/master-record updates uncommitted

---

## Phase 15 — Final 420-case notebook and entrypoint (execution not launched)

- **Date:** 2026-08-26
- **Objective:** Create the official 140 × 3 = 420 benchmark execution vehicle without launching the run.
- **Why required:** Phase 14 9-case engineering validation is complete. The dissertation evaluation is 420 independent cases at locked T=0.65. A separate notebook and raw store prevent mixing the 9-case job with the official run.
- **Work completed:**
  - Added `notebooks/colab_phase15_full_benchmark.ipynb` (clone, install, Drive KB + lock restore, preflight, T=0.65 check, `run_full_benchmark.py`, resume cell, 420 completion summary, Drive copy)
  - Added `scripts/run_full_benchmark.py` (always n=140, `allow_full=True`, mock refused)
  - Extended `src/run/benchmark.py` / `drive_sync.py` so Phase 15 uses `phase15_benchmark` paths
  - Left `notebooks/colab_phase14_benchmark_validation.ipynb` unchanged
  - Did **not** modify frozen 140/40, T=0.65, V1, RAG modules, or retrieval
  - Did **not** execute the 420-case benchmark
- **Technical decisions:** Keep Phase 14 CLI (`run_benchmark.py`) as the 9-case evidence path. Phase 15 uses a separate entrypoint and Drive/raw prefix so `--resume-latest` cannot resume the 9-case store. Load T from `threshold.lock.json` only. Refuse mock.
- **Files created/modified:**
  - `V2/notebooks/colab_phase15_full_benchmark.ipynb`
  - `V2/scripts/run_full_benchmark.py`
  - `V2/src/run/benchmark.py`
  - `V2/src/run/drive_sync.py`
  - `V2/tests/test_phase15_benchmark.py`
  - `V2/docs/phase15_full_benchmark.md`
  - `V2/project_record/evidence/phase15_validation.md`
  - `V2/docs/IMPLEMENTATION_PLAN.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
  - `V2/config/experiment.yaml` (`phase15_entrypoint`)
  - `V2/results/raw/phase15_benchmark/.gitkeep` (empty placeholder; added 2026-08-27)
  - `V2/results/checkpoints/phase15_benchmark/.gitkeep` (empty placeholder; added 2026-08-27)
- **Tests/validation:** `PYTHONPATH=. pytest tests/test_phase15_benchmark.py -q` → **6 passed** (2026-08-27, after empty raw/checkpoint folders). 420-case job not run. Full suite not re-run in this session (last recorded 105 passed through Phase 14).
- **Actual outcome:** Notebook and runner exist for the official 420-case Colab job. Execution is **not launched**.
- **Problems encountered:** None during notebook creation. A previous 9-case raw store must not be used as `--resume-latest` for 420 — separate `phase15_benchmark` job prefix addresses this.
- **Problems resolved:** Separate Phase 15 raw/checkpoint/config Drive paths. On 2026-08-27, user-copied Colab files were moved from `results/raw/phase15_benchmark/{cases,checkpoint,summary}` into `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/` (SHA-256 unchanged). Checkpoint copy: `results/checkpoints/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4.json`.
- **Remaining issues:** Push Phase 15 to GitHub, then run `notebooks/colab_phase15_full_benchmark.ipynb` on Colab GPU. Do not re-run the 9-case notebook instead. Google Drive Phase 15 archive does not exist until the run starts.
- **Dissertation relevance:** The official test evaluation is 140 × 3 at T=0.65, not the 9-case engineering check.
- **Evidence/source file paths:**
  - `V2/notebooks/colab_phase15_full_benchmark.ipynb`
  - `V2/scripts/run_full_benchmark.py`
  - `V2/docs/phase15_full_benchmark.md`
  - `V2/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl`
- **Validation evidence:** `V2/project_record/evidence/phase15_validation.md`
- **Backup status:**
  - Colab: 420-case job **not launched**
  - Google Drive: Phase 15 raw/checkpoints **do not exist yet**
  - Local: verified — canonical raw store `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/` (420-line JSONL; SHA-256 unchanged from the misplaced copy)
  - GitHub: Phase 15 files **uncommitted** (push required before Colab clone)

---

## Phase 15 — Colab 420-case output verified locally; backup checklist

- **Date:** 2026-08-27
- **Objective:** Verify the official 140 × 3 = 420 Colab artefacts on the Mac and record what to keep on Drive vs GitHub. Do not rerun.
- **Why required:** Colab `/content` is ephemeral. Dissertation scoring needs a complete raw JSONL plus a documented backup split (local / Drive / GitHub).
- **Work completed:** Counted JSONL vs frozen 140 and planned 420 keys. Compared summary, checkpoint, log, fingerprint, lock. Wrote `evidence/phase15_backup_manifest.md` + JSON artefact. Did **not** rewrite JSONL, freeze files, T, RAG modules, or V1.
- **Technical decisions:** Treat local 420 JSONL as the scoring input. Do not commit raw JSONL or the run log to GitHub. Drive presence remains **NEEDS VERIFICATION**.
- **Files created/modified:**
  - `V2/project_record/evidence/phase15_backup_manifest.md`
  - `V2/project_record/evidence/artifacts/phase15_backup_manifest.json`
  - `V2/project_record/evidence/phase15_validation.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
  - `V2/docs/IMPLEMENTATION_PLAN.md`
  - `V2/.gitignore` (un-ignore Phase 15 small config snapshots after `results/config/**`)
- **Tests/validation:** Local file inspection only. 420-case job not re-run. Completeness **PASS** on Mac artefacts.
- **Actual outcome:** 420 unique completed cases; processed/final empty (expected).
- **Problems encountered:** User-copied files originally lacked the run-id folder (fixed earlier). Drive not listed from this machine.
- **Problems resolved:** Canonical local path used for counts.
- **Remaining issues:** Confirm Drive folder in the UI. Commit small config snapshots + evidence (not JSONL). Phase 16 metrics not started.
- **Dissertation relevance:** Official test evaluation artefacts exist locally for RQ1–RQ3 scoring.
- **Evidence/source file paths:**
  - `V2/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl`
  - `V2/results/config/phase15_benchmark_summary.json`
  - `V2/project_record/evidence/phase15_backup_manifest.md`
- **Validation evidence:** `V2/project_record/evidence/phase15_validation.md`
- **Backup status:**
  - Colab: `/content` ephemeral; run finished 2026-08-26T23:11:58Z
  - Google Drive: **NEEDS VERIFICATION** (summary self-reports sync)
  - Local: verified — 420 JSONL + checkpoint + log + configs
  - GitHub: source already on origin; config snapshots + this evidence **not yet committed**

---

## Phase 16 — Evaluation + metrics (CPU; no RAG/Qwen)

- **Date:** 2026-08-27 (evaluation UTC 2026-08-26T23:51:41Z)
- **Objective:** Compute the approved Phase 16 metrics from the saved Phase 15 420-case JSONL.
- **Why required:** Dissertation scoring must use frozen raw results. Rerunning Qwen would mix a new generation run with the official 420-case artefact.
- **Work completed:**
  - Inspected metric implementations: none require LLM/GPU. Faithfulness is CPU `token_overlap`; stored `verification_score` is reused, not recomputed.
  - CPU runner `scripts/run_evaluation.py` scores the canonical Phase 15 JSONL only.
  - Saved processed JSONL, metric JSON/CSV/markdown, evaluation summary, and evidence.
  - Verified 420 unique keys; raw SHA unchanged; freeze CSVs and T=0.65 lock SHA unchanged.
  - Did **not** import architecture runners or `llama_cpp`. Did **not** start Phase 17.
- **Technical decisions:** `judge_model: null`. Do not claim official RAGAS LLM-as-judge. UQ displayed correctness uses the abstention template; claim correctness uses the draft. `unsupported_emitted_rate` = ANSWER and failed numeric match (not a hallucination label). Context P/R use gold `file_name` / `context_id`.
- **Files created/modified:**
  - `V2/src/evaluation/metrics.py`, `V2/src/evaluation/runner.py`, `V2/src/evaluation/__init__.py`
  - `V2/scripts/run_evaluation.py`
  - `V2/tests/test_phase16_evaluation.py`
  - `V2/config/experiment.yaml` (evaluation CPU flags + metric list; `results_metrics` path)
  - `V2/.gitignore` (allowlist Phase 16 processed/metrics/config snapshots)
  - `V2/docs/phase16_evaluation.md`
  - `V2/results/processed/phase16_cases.jsonl`
  - `V2/results/metrics/phase16_summary.csv`, `phase16_summary.md`, `phase16_by_architecture.json`
  - `V2/results/config/phase16_evaluation_summary.json`, `phase16_smoke_test.json`
  - `V2/project_record/evidence/phase16_validation.md`
- **Tests/validation:**
  - Phase 16 + related tests **18 passed** in the pre-eval command; full suite **116 passed**
  - CPU evaluation **PASS** — run_id `phase16_20260826T235141Z_73fdbf58`; n=420; `used_llm_inference=false`; `used_gpu=false`; `used_rag_rerun=false`
  - Raw SHA-256 `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` unchanged
- **Actual outcome:** All 420 cases scored on CPU. Observed displayed answer correctness: Single-Agent **32/140 (0.2286)**, Multi-Agent **29/140 (0.2071)**, UQ **32/140 (0.2286)** displayed and **34/140 (0.2429)** claim. UQ: 78 ANSWER / 62 ABSTAIN; selective accuracy **32/78 (0.4103)**; unsupported-emitted rate **0.3286** vs **0.7714** / **0.7929** for always-answer systems. Context precision **0.4304** and recall **0.9000** are identical across architectures. Faithfulness ≈ 0.55–0.56 (CPU token-overlap, not RAGAS).
- **Problems encountered:** Importing `src.run.benchmark` would have loaded RAG/LLM modules. Package `__init__` also created a circular import with `src.calibration.lock`.
- **Problems resolved:** Evaluation runner uses schema constants only. `run_evaluation` is imported from `src.evaluation.runner`, not package `__init__`.
- **Remaining issues:** Google Drive copy of processed/metrics **NEEDS VERIFICATION**. Phase 17 statistical tests **not started**. Do not claim Multi-Agent improves accuracy from these point estimates.
- **Dissertation relevance:** Provides the 420-case metric tables for RQ1–RQ3 without a second generation run. RQ1 point estimates do not show a Multi-Agent accuracy gain. RQ2/RQ3 operationalisation is unsupported-emitted rate and selective accuracy at locked T=0.65, not a labelled hallucination corpus.
- **Evidence/source file paths:**
  - `V2/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` (input only; unchanged)
  - `V2/results/processed/phase16_cases.jsonl`
  - `V2/results/metrics/phase16_summary.csv`
  - `V2/results/config/phase16_evaluation_summary.json`
  - `V2/results/config/threshold.lock.json` (T=0.65; SHA unchanged)
- **Validation evidence:** `V2/project_record/evidence/phase16_validation.md`
- **Backup status:**
  - Colab: **N/A** (CPU local scoring; no new Colab/Qwen run)
  - Google Drive: **NEEDS VERIFICATION** (processed/metrics not listed from this Mac)
  - Local: verified — processed JSONL, metric tables, evaluation summary, evidence, master record
  - GitHub: Phase 16 source/docs/tables **uncommitted** (do not commit Phase 15 raw JSONL)

---

## Phase 16 — LLM-as-judge faithfulness (implementation; Colab 420 not launched)

Historical section (2026-08-27). Official 420-case Colab run was **not launched** on this date. Later local verification (2026-08-28) is the next section. Do not treat this section as the final judge status.

- **Date:** 2026-08-27
- **Objective:** Add a post-hoc LLM-as-judge faithfulness pass over the frozen Phase 15 420-case JSONL without rerunning RAG.
- **Why required:** CPU token-overlap is a weak faithfulness proxy. RQ2 needs an evidence-support score of the saved claims. Official RAGAS is not used.
- **Work completed:**
  - Judge prompt + parser (`src/evaluation/judge.py`)
  - Resumable runner + CLI (`src/evaluation/judge_runner.py`, `scripts/run_judge.py`)
  - Colab notebook `notebooks/colab_phase16_judge.ipynb`
  - Local mock n=3 validation (SHA unchanged; Phase 16 CPU JSONL unchanged)
  - Did **not** launch the official 420-case Colab judge (on this date)
  - Did **not** start Phase 17
- **Technical decisions:** One Qwen3-8B instance; temperature 0.0; max_new_tokens 32; n_ctx 4096. UQ claim = `configuration.draft_answer`. No gold context or gold answer in the prompt. Separate `results/raw/phase16_judge/{run_id}/judge.jsonl`. Label exactly `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)`. Keep token-overlap as secondary. Do not LLM-judge answer correctness or context P/R.
- **Files created/modified:**
  - `V2/src/evaluation/judge.py`, `V2/src/evaluation/judge_runner.py`
  - `V2/scripts/run_judge.py`
  - `V2/notebooks/colab_phase16_judge.ipynb`
  - `V2/tests/test_phase16_judge.py`
  - `V2/docs/phase16_judge.md`
  - `V2/config/experiment.yaml`, `V2/config/prompts.yaml`, `V2/.gitignore`
- **Tests/validation:** `tests/test_phase16_judge.py` **8 passed**; full suite **124 passed**. Mock n=3 resume skipped 3. Official 420 GPU job **not run** on this date.
- **Actual outcome:** Implementation and local mock validation ready. Colab 420 judge **NEEDS VERIFICATION** / not launched (2026-08-27).
- **Problems encountered:** CPU evaluation import-graph test had to stay limited to CPU modules so the judge job can load `create_backend`.
- **Problems resolved:** Judge store uses `judge.jsonl` via `CaseStore(raw_filename=...)`. Official mock-420 is refused.
- **Remaining issues (as of 2026-08-27):** Push V2 and run `notebooks/colab_phase16_judge.ipynb` on Colab GPU. Copy frozen Phase 15 JSONL from Drive. Do not rerun RAG. Phase 17 not started. **Superseded 2026-08-28:** official 420 **PASS** verified locally (next section).
- **Dissertation relevance:** Separates (1) Phase 15 generation, (2) Phase 16 CPU metrics, (3) post-hoc same-model faithfulness judging. Same-family Qwen3-8B judge is a limitation, not official RAGAS.
- **Evidence/source file paths:**
  - `V2/scripts/run_judge.py`
  - `V2/notebooks/colab_phase16_judge.ipynb`
  - `V2/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` (input only)
- **Validation evidence:** `V2/project_record/evidence/phase16_validation.md`
- **Backup status:**
  - Colab: 420-case judge **not launched** (2026-08-27)
  - Google Drive: judge raw **does not exist yet** on this date
  - Local: verified — code, tests, notebook, mock n=3 store (gitignored)
  - GitHub: judge implementation **uncommitted**

---

## Phase 16 — Official 420-case LLM-as-judge (Colab T4; locally verified)

- **Date:** 2026-08-28
- **Objective:** Record and locally verify the official post-hoc 420-case LLM-as-judge faithfulness run. Do not rerun RAG or the judge job.
- **Why required:** The 2026-08-27 implementation left official Colab 420 as **not launched** / **NEEDS VERIFICATION**. Dissertation RQ2 needs the verified JSONL, not the notebook alone.
- **Work completed:**
  - Inspected user-copied Colab artefacts. Official files had been dropped into the old mock folder name `phase16_judge_test_mock3`; folder renamed to the run ID (JSONL contents unchanged).
  - Counted 420 unique keys vs frozen 140 × 3. Compared checkpoint, log, summary, fingerprint, Phase 15 SHA, T lock, freeze CSVs.
  - Updated evidence + docs. Did **not** rewrite Phase 15 JSONL, Phase 16 CPU tables, freeze files, T, RAG modules, or V1. Did **not** start Phase 17.
- **Technical decisions:** Metric label remains exactly `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS**. CPU numeric correctness and context P/R unchanged. **Judge-call source of truth is the JSONL:** `temperature=0.0`, `max_new_tokens=32`, `n_ctx=4096`. Do not use `phase16_judge_runtime_fingerprint.json` `model_config` (`temperature=0.1`, `max_new_tokens=512`) as the judge-call settings.
- **Files created/modified (documentation only, 2026-08-28):**
  - `V2/project_record/evidence/phase16_validation.md`
  - `V2/project_record/PROJECT_MASTER_RECORD.md`
  - `V2/docs/phase16_judge.md`
  - `V2/docs/IMPLEMENTATION_PLAN.md`
- **Tests/validation:** Local file inspection of official JSONL. Job not re-run. Completeness **PASS**: 420/420; 140 per architecture; 0 duplicates; 0 missing; 0 errors; 0 parse failures; all COMPLETED; `llama_cpp`; Qwen3-8B Q4_K_M; Tesla T4; `used_rag_rerun=false`; no gold context/answer; UQ `draft_answer`; UQ 78 ANSWER / 62 ABSTAIN; Phase 15 SHA `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` unchanged.
- **Actual outcome:** Official run_id `phase16_judge_20260828T152623Z_06661255` **PASS** (Colab ended 2026-08-28T15:39:49Z). Mean LLM-as-judge faithfulness: Single-Agent **0.3241**, Multi-Agent **0.3484**, UQ **0.3749** (all 140); UQ ANSWER-only **0.6548** (78 cases). JSONL SHA-256 `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3`. T=0.65 and frozen 140/40 SHAs unchanged.
- **Problems encountered:** Copy landed under the mock3 directory name. Runtime fingerprint `model_config` does not match per-row judge settings.
- **Problems resolved:** Folder renamed to the official run ID. Fingerprint discrepancy documented; JSONL used as source of truth.
- **Remaining issues:** Google Drive copy of the judge run **NEEDS VERIFICATION** (summary self-reports sync to `MyDrive/MSc-RAG/results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255`). GitHub commit of small tables/docs **not done**. Phase 17 **not started**. Do not claim official RAGAS. Do not claim Multi-Agent improves numeric accuracy (CPU tables unchanged).
- **Dissertation relevance:** Adds a same-model post-hoc faithfulness score for RQ2 without a second RAG generation. UQ ANSWER-only faithfulness (0.6548) is higher than always-answer architectures (~0.32–0.35) because abstains drop low-support claims; this is not a significance test (Phase 17 not run). Same-family Qwen3-8B judge is a limitation.
- **Evidence/source file paths:**
  - `V2/results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl`
  - `V2/results/checkpoints/phase16_judge/phase16_judge_20260828T152623Z_06661255.json`
  - `V2/results/logs/phase16_judge_20260828T152554Z.log`
  - `V2/results/metrics/phase16_judge_summary.csv`
  - `V2/results/config/phase16_judge_summary.json`
  - `V2/results/config/phase16_judge_runtime_fingerprint.json` (fingerprint only; not judge-call settings)
  - `V2/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` (input only; unchanged)
- **Validation evidence:** `V2/project_record/evidence/phase16_validation.md`
- **Backup status:**
  - Colab: `/content` ephemeral; official judge finished 2026-08-28T15:39:49Z
  - Google Drive: **NEEDS VERIFICATION** (summary self-reports sync; folder not listed from this Mac)
  - Local: verified — official `judge.jsonl` (420) + checkpoint + log + judge metrics/config
  - GitHub: Phase 16 docs/tables **uncommitted** (do not commit raw `judge.jsonl`)

---

## Phase 17 — Statistics on frozen Phase 15/16 results

- **Date:** 2026-08-28
- **Objective:** Rigorous paired statistical analysis of RQ1–RQ3 using only frozen Phase 15/16 artefacts.
- **Why required:** Point estimates from Phase 16 cannot answer significance, effect size, or the coverage/selective-accuracy trade-off. Dissertation reporting needs n, SD, CIs, tests, p-values, and honest non-significant findings.
- **Work completed:**
  - CPU statistics package `src/statistics/` + `scripts/run_statistics.py` (no RAG/Qwen/judge rerun).
  - SHA gates on Phase 15 JSONL, Phase 16 processed JSONL, official judge JSONL, frozen 140/40, and T=0.65 lock.
  - Confirmatory + exploratory families with Holm–Bonferroni; Wilson CIs; bootstrap (seed 42, 10 000); Shapiro assumption checks; figures.
  - Did **not** rewrite Phase 15/16 JSONL, freeze files, T, RAG modules, or V1. Did **not** start Phase 18.
- **Technical decisions:** Statistical unit = frozen test question (n=140), paired by `question_id`. RQ1 primary = exact McNemar on displayed numeric correctness (SA vs MA). RQ2 primary = `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS**. RQ3 = coverage / selective accuracy / unsupported_emitted at locked T=0.65. Token-overlap is secondary. Context P/R are retrieval controls (identical across architectures). Wilcoxon used for paired continuous scores because Shapiro fails.
- **Files created/modified:**
  - `V2/src/statistics/*.py`
  - `V2/scripts/run_statistics.py`
  - `V2/tests/test_phase17_statistics.py`
  - `V2/docs/phase17_statistics.md`
  - `V2/results/metrics/phase17_*.csv`, `phase17_summary.md`, `phase17_figures/*.png`
  - `V2/results/config/phase17_statistics_summary.json`, `phase17_smoke_test.json`
  - `V2/results/final/phase17_interpretation.md`
  - `V2/project_record/evidence/phase17_validation.md`
- **Tests/validation:** `tests/test_phase17_statistics.py` **6 passed**; full suite **130 passed**. SHA of Phase 15/16 JSONL unchanged after `analyse()`.
- **Actual outcome:**
  - **RQ1:** SA 32/140 vs MA 29/140; McNemar exact p=0.6776 (Holm p=0.6776); Cohen's g=−0.0652. **Not significant.** Does not support a Multi-Agent accuracy gain.
  - **RQ2:** Spearman ρ(confidence, LLM faithfulness)=0.6988, Holm p=2.403×10⁻²¹; Mann–Whitney ANSWER vs ABSTAIN Holm p=1.767×10⁻¹⁴; paired Wilcoxon MA vs UQ faithfulness Holm p=0.4032 (**not significant**).
  - **RQ3:** Coverage 78/140=0.5571; selective accuracy 32/78=0.4103; 60 true abstains, 2 false abstains; unsupported-emitted McNemar vs SA and MA both Holm-significant.
- **Problems encountered:** Paired LLM-faithfulness differences are non-normal (Shapiro p≪0.05). Matplotlib was not previously pinned in the V2 venv.
- **Problems resolved:** Wilcoxon used as primary continuous test. `matplotlib` added to `requirements.txt` and installed in `.venv`.
- **Remaining issues:** Google Drive copy of Phase 17 tables **NEEDS VERIFICATION**. GitHub commit of stats code/tables **not done**. Phase 18 **not started**. Do not claim official RAGAS. Do not claim Multi-Agent improves numeric accuracy.
- **Dissertation relevance:** Supplies confirmatory paired tests, CIs, effect sizes, and honest negative RQ1 finding. RQ2 support is within-UQ confidence/faithfulness association, not a paired faithfulness gain vs Multi-Agent. RQ3 shows abstention reduces emitted numeric errors at the cost of coverage.
- **Evidence/source file paths:**
  - `V2/results/processed/phase16_cases.jsonl` (input; unchanged)
  - `V2/results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl` (input; unchanged)
  - `V2/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` (SHA verified; unchanged)
  - `V2/results/metrics/phase17_tests.csv`
  - `V2/results/config/phase17_statistics_summary.json`
- **Validation evidence:** `V2/project_record/evidence/phase17_validation.md`
- **Backup status:**
  - Colab: **N/A** (CPU local statistics; no new GPU job)
  - Google Drive: **NEEDS VERIFICATION** (Phase 17 tables not listed from this Mac)
  - Local: verified — tests CSV/MD, figures, summary JSON, evidence, master record
  - GitHub: Phase 17 source/docs/tables **uncommitted** (do not commit Phase 15 raw JSONL or judge JSONL)

---

## Phase 17 figure refresh — dissertation presentation only

- **Date:** 2026-08-28
- **Objective:** Replace the draft Phase 17 plots with dissertation-quality primary and appendix figures without changing any statistical results.
- **Why required:** The first Phase 17 plots used a 0–0.5 y-axis, proportion scale, 150 dpi, and incomplete labels. Dissertation insertion needs 0–100% axes, n=140, locked T=0.65, and explicit custom/RAGAS-inspired (not official RAGAS) wording.
- **Work completed:**
  - Added `src/statistics/figures.py` and `scripts/render_phase17_figures.py` (figures only; SHA-gates frozen artefacts; does not write Phase 17 CSVs).
  - Redrew three primary figures (RQ1 Wilson CI correctness; RQ2 confidence vs faithfulness scatter; RQ3 coverage vs selective accuracy) and three appendix figures (McNemar counts; faithfulness boxplot; UQ outcome counts).
  - Wrote PNG (300 dpi), PDF, and SVG for each stem.
  - Documented figure roles in `docs/phase17_figures.md`.
  - Did **not** rerun RAG, Qwen, the judge, or `scripts/run_statistics.py`. Did **not** start Phase 18.
- **Technical decisions:** Architecture labels locked as Single-Agent / Multi-Agent / Multi-Agent + UQ. RQ1 uses a 0–100% zero baseline and does not mark significance. RQ2 y-axis is `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)`. RQ3 states T=0.65 is locked from the separate DEV 40. Scatter points are joined read-only from Phase 16 processed JSONL + official judge JSONL.
- **Files created/modified:**
  - `V2/src/statistics/figures.py`
  - `V2/scripts/render_phase17_figures.py`
  - `V2/src/statistics/report.py` (`write_plots` now delegates to saved-table renderer)
  - `V2/tests/test_phase17_statistics.py` (figure-render SHA guard)
  - `V2/docs/phase17_figures.md`
  - `V2/docs/phase17_statistics.md`
  - `V2/results/metrics/phase17_figures/*.{png,pdf,svg}`
  - `V2/results/config/phase17_figure_render.json`
  - `V2/project_record/evidence/phase17_validation.md`
- **Tests/validation:** `test_render_figures_does_not_change_results` **PASS**. `pytest -q -k "not test_analyse_paired_140"`: **130 passed**. Result-file SHA-256 unchanged (see `phase17_figure_render.json`).
- **Actual outcome:** Primary and appendix figures regenerated. Phase 17 descriptive/tests/effect/assumptions CSVs, summary MD, interpretation MD, and statistics JSON **unchanged**. Frozen Phase 15/16 JSONL SHAs **unchanged**. T=0.65 **unchanged**.
- **Problems encountered:** Matplotlib 3.11 `boxplot` uses `tick_labels` rather than `labels`. Title weight `"medium"` is not in DejaVu Sans.
- **Problems resolved:** `tick_labels` with `labels` fallback; title weight set to `normal`.
- **Remaining issues:** Google Drive copy of figure files **NEEDS VERIFICATION**. GitHub commit **not done**. Phase 18 **not started**.
- **Dissertation relevance:** Supplies the three main-body RQ figures and three appendix figures with consistent naming and captions.
- **Evidence/source file paths:**
  - `V2/docs/phase17_figures.md`
  - `V2/results/config/phase17_figure_render.json`
  - `V2/results/metrics/phase17_descriptive.csv` (unchanged)
  - `V2/results/metrics/phase17_tests.csv` (unchanged)
  - `V2/results/config/phase17_statistics_summary.json` (unchanged)
- **Validation evidence:** `V2/project_record/evidence/phase17_validation.md`
- **Backup status:**
  - Colab: **N/A** (CPU local figure render; no GPU job)
  - Google Drive: **NEEDS VERIFICATION**
  - Local: verified — `V2/results/metrics/phase17_figures/` (18 files)
  - GitHub: figure code/docs/PNGs **uncommitted**

---

## Not started (explicit)

| Phase | Name | Status |
| --- | --- | --- |
| 18 | Dissertation evidence pack | Not started |

---

## How to update this record

After each completed phase, append a new `## Phase X — ...` section with the required fields, update the **Project snapshot** table with newly verified facts, and append any assumption changes to the **Decisions log** without rewriting prior phase sections.
