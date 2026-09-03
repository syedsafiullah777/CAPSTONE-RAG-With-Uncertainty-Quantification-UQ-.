# V2 Implementation Plan

Approved phased plan for the MSc RAG V2 rebuild.  
Actual code, configuration, tests, and saved outputs take precedence over this document.

| Field | Value |
| --- | --- |
| Last updated | 2026-08-29 |
| Current completed phase | **Phase 21 complete:** canonical Colab final live-demo launcher (static checks **PASS**; official T4 viva launch **NEEDS VERIFICATION**). Research Phases 15–20 unchanged. |
| Next implementation phase | **None.** Stop after Phase 21. |
| V1 | Reference-only — never modified |

---

## Research questions (locked)

1. **RQ1:** Multi-Agent RAG vs Single-Agent RAG — answer accuracy on FinQA financial documents.
2. **RQ2:** Does uncertainty quantification reduce hallucinated/unsupported responses in Multi-Agent RAG?
3. **RQ3:** Does confidence-based abstention improve reliability when evidence is insufficient?

**Benchmark target:** 140 frozen test questions × 3 architectures = **420** cases (independent; no chaining).

---

## Storage, Backup, Recovery and Monitoring

This requirement applies to **all** phases — especially benchmark, evaluation, calibration, and statistics.

### Storage model

| Layer | Role |
| --- | --- |
| **GitHub** | Source / version control (V2 code, config, tests, docs, manifests, final reproducible tables) |
| **Google Colab** | Computation only (GPU notebooks; `/content` is ephemeral) |
| **Google Drive** | Persistent experiment archive (`Google Drive/MSc-RAG/…`) |
| **Local Mac** | Main dev copy + secondary offline backup after milestones |

Full specification: `V2/docs/storage_backup_recovery.md`  
Config: `V2/config/experiment.yaml` → `storage`

### Drive layout (logical)

```text
Google Drive/MSc-RAG/
├── results/raw/
├── results/processed/
├── results/metrics/
├── results/final/
├── checkpoints/
├── logs/
├── configs/
└── artifacts/
```

Do **not** mirror the full V2 git repository on Drive.

### Benchmark / evaluation requirements (all relevant phases)

Every benchmark or evaluation runner must implement:

- **incremental checkpointing** — save after each case (or small batch)
- **Drive persistence** — sync checkpoints, raw results, logs to Drive during/after Colab runs
- **local backup** — recommended after major milestones
- **GitHub milestone commits** — code/config/manifests after each completed phase
- **resumable execution** — resume from latest valid checkpoint
- **progress monitoring** — log completed / failed / pending counts
- **failure recovery** — retry failed cases; skip completed; no duplicates
- **backup validation** — verify paths exist before claiming backup; never restart from Q1

### Raw result schema (before aggregation)

Each architecture–question case must preserve structured fields listed in `storage.raw_result_fields` (config). Never silently overwrite raw outputs.

### Phase completion (every phase)

1. Run relevant tests / smoke / validation for the phase.
2. Save **actual** results to `V2/project_record/evidence/phaseN_validation.md` (and machine-readable JSON under `results/config/` where useful).
3. Update `V2/project_record/PROJECT_MASTER_RECORD.md` with a concise reference to the evidence file.
4. Report backup status using `V2/project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md`
5. Run tests; review git status/diff; commit if appropriate
6. Stop before starting the next phase

**Do not fabricate PASS.** Record FAIL with the actual error. Do not mark a phase complete until approved criteria are met.

---

## Validation and evidence (all phases)

After every major phase that performs tests, smoke tests, model runs, retrieval validation, benchmark execution, calibration, evaluation, or live-artifact validation:

1. Run the relevant tests.
2. Save actual output to a dedicated file inside V2.
3. Record: date/time, phase, test name, command/notebook, environment/device/GPU, expected, **actual**, PASS/FAIL, error (if any), output path.
4. Update the master record with a reference to the evidence file.

**Evidence layout:**

```text
V2/project_record/evidence/
├── phase1_validation.md … phase7_validation.md
├── artifacts/              # pytest captures, small logs
└── _TEMPLATE.md
```

Machine-readable smoke output example: `results/config/phase7_smoke_test.json`

**Benchmark / evaluation:** do **not** put every raw case in one giant markdown file. Keep raw machine-readable results in `results/raw/` + `checkpoints/`; evidence files are concise summaries pointing to those paths.

Continues through: RAG validation, calibration, 420-case benchmark, metrics, statistics, Streamlit live validation, final reproducibility validation.

Capture helpers:

- `scripts/capture_pytest_evidence.py --phase N`
- `scripts/smoke_generate.py` → `results/config/phase7_smoke_test.json`

Spec: `project_record/evidence/README.md`

---

Streamlit demo uses the same V2 RAG pipelines as benchmark mode (not precomputed lookup for new questions). Session outputs follow Drive persistence rules where applicable.

### Explicitly excluded infrastructure

Colab CLI, gcloud, ADC, Kubernetes, distributed orchestration — unless explicitly required later.

---

## Phase overview

| Phase | Name | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Project foundation | ✅ Complete | `evidence/phase1_validation.md` |
| 2 | V1 audit + FinQA profile | ✅ Complete | `evidence/phase2_validation.md` |
| 3 | PDF resolvability | ✅ Complete | `evidence/phase3_validation.md` |
| 4 | Freeze test 140 | ✅ Complete | `evidence/phase4_validation.md` |
| 5 | Freeze calibration 40 | ✅ Complete | `evidence/phase5_validation.md` |
| 6 | Knowledge base | ✅ Complete | `evidence/phase6_validation.md` |
| 7 | Qwen3-8B backend | ✅ Complete | `evidence/phase7_validation.md` (Colab GPU **NEEDS VERIFICATION**) |
| 8 | Single-Agent RAG baseline | ✅ Complete | `evidence/phase8_validation.md` |
| 9 | Multi-Agent RAG | ✅ Complete | `evidence/phase9_validation.md` |
| 10 | Multi-Agent + UQ / abstention | ✅ Complete | `evidence/phase10_validation.md` |
| 11 | Streamlit live artefact (schema already in Phases 8–10) | ✅ Complete | `evidence/phase11_validation.md` |
| 12 | Pilot run (6 × 3 = 18 cases) | ✅ Local 18/18 + Colab T4 18/18 PASS (raw JSONL archived) | `evidence/phase12_validation.md` |
| 13 | Calibration / threshold lock | ✅ Complete — T=0.65 locked on Colab T4 DEV 40 | `evidence/phase13_validation.md` |
| 14 | 9-case engineering validation | ✅ Complete (Colab T4 9/9). Keep as evidence. Do not re-run. | `evidence/phase14_validation.md` |
| 15 | Final 420-case benchmark | ✅ Local 420/420 verified (Colab T4). Drive **NEEDS VERIFICATION**. | `evidence/phase15_validation.md`; `evidence/phase15_backup_manifest.md` |
| 16 | Evaluation + metrics | ✅ CPU complete. Official Colab 420 LLM-judge **PASS** (verified 2026-08-28) | `evidence/phase16_validation.md` |
| 17 | Statistics + final tables | ✅ Complete — paired n=140 on frozen Phase 15/16 | `evidence/phase17_validation.md` |
| 18 | Dissertation evidence pack | ⬜ Not started | master record + all phase evidence |

Phase numbers 11–18 are indicative; adjust if merged — storage requirements remain.

---

## Phase details (completed summary)

Phases 1–7 chronology and evidence: `V2/project_record/PROJECT_MASTER_RECORD.md`

**Next validation:** Optional Colab `llama_cpp` single-agent smoke for GPU parity with Phase 7.

---

## Phase 8 — Single-Agent RAG baseline (complete)

**Objective:** Baseline RAG pipeline using frozen KB + Qwen3-8B backend.

**Verified:** Smoke n=3 **PASS** (real retrieval + generation). Evidence: `project_record/evidence/phase8_validation.md`.

**Storage / recovery (design carried forward):**

- Per-case raw JSONL compatible with `storage.raw_result_fields`
- Checkpoint / resume for later 420-case runner
- Skip/resume by `{architecture}:{question_id}`
- No silent overwrite of raw results

---

## Phase 9 — Multi-Agent RAG (complete)

Retrieve → draft → verify. See `docs/phase9_multi_agent.md`.

## Phase 10 — Multi-Agent + UQ / abstention (complete)

See `docs/phase10_multi_agent_uq.md`.

## Phase 11 — Streamlit live artefact (complete)

See `docs/phase11_live_artefact.md`. Original-plan schema/logging is `RAGCaseResult` from Phases 8–10.

## Phase 12 — Pilot (complete; Colab T4 18/18 PASS)

See `docs/phase12_pilot.md`. 6 frozen questions × 3 architectures = 18 resumable cases. Colab run_id `phase12_20260826T183704Z_9773516a`.

## Phase 13 — DEV calibration / threshold lock (complete; T=0.65)

See `docs/phase13_calibration_lock.md`. Frozen FinQA **dev** 40; `multi_agent_uq` only. Colab T4 run_id `phase13_20260826T192003Z_7bcd6ed3`. Official lock `results/config/threshold.lock.json`. Does not run the 420-case benchmark.

## Phase 14 — 9-case engineering validation (complete)

See `docs/phase14_benchmark.md`. 3 frozen questions × 3 architectures = 9 cases at locked T=0.65. Colab T4 run_id `phase14_20260826T200828Z_e91e588d` **PASS**. Keep as engineering evidence only. **Do not run another 9-case validation.**

## Phase 15 — Final 420-case benchmark (Colab executed; locally verified)

See `docs/phase15_full_benchmark.md` and `project_record/evidence/phase15_backup_manifest.md`.

Notebook: `notebooks/colab_phase15_full_benchmark.ipynb`. Entrypoint: `scripts/run_full_benchmark.py`.

Colab T4 run_id `phase15_20260826T203744Z_dae9c3a4`: **420/420** unique cases, T=0.65 LOCKED. Phase 16 scored these saved cases on CPU (no RAG/Qwen rerun).

**140 frozen test questions × 3 architectures = 420 cases.** Independent; no chaining. Phase 14 9-case notebook remains engineering evidence and is unchanged.

| Item | Locked value |
| --- | --- |
| Eval set | Frozen FinQA **test** 140 (`selected_140_questions.csv`) |
| Architectures | `single_agent`, `multi_agent`, `multi_agent_uq` |
| Threshold | **T = 0.65** (`threshold.lock.json`; do not recalibrate) |
| Model | Qwen3-8B **Q4_K_M** via **`llama_cpp`** |
| Compute | Google Colab GPU |
| Knowledge base | Shared Phase 6 (230 PDFs / 1239 chunks) |
| Retrieval | Identical across architectures (`top_k=4`, `BAAI/bge-small-en-v1.5`) |
| Raw store | `results/raw/phase15_benchmark/{run_id}/` (separate from Phase 14) |

Must: incremental raw JSONL; checkpoint to Google Drive; resume after interruption (`--resume-latest`); retry genuine failures; skip completed / prevent duplicates; progress monitoring; preserve raw results and logs; print a 420-case completion summary.

Must not: modify frozen 140 or calibration 40; recalibrate T; modify V1; change RAG architectures or retrieval; rewrite the Phase 14 9-case notebook; rerun 420 because of this documentation update.

## Phase 16 — Evaluation + metrics (complete; CPU)

See `docs/phase16_evaluation.md` and `project_record/evidence/phase16_validation.md`.

Entrypoint: `scripts/run_evaluation.py`. Sole input: Phase 15 JSONL `phase15_20260826T203744Z_dae9c3a4` (SHA-256 `f5256ae40fa8…`). No RAG/Qwen/GPU. `judge_model: null` (not official RAGAS).

Observed displayed correctness: Single-Agent 32/140, Multi-Agent 29/140, UQ 32/140 displayed / 34/140 claim. UQ 78 ANSWER / 62 ABSTAIN at T=0.65. Context P/R identical across architectures. Do not claim Multi-Agent improves accuracy.

## Phase 16 — LLM-as-judge faithfulness (official 420 PASS; locally verified)

See `docs/phase16_judge.md`. Separate post-hoc job: `scripts/run_judge.py` + `notebooks/colab_phase16_judge.ipynb`. Frozen Phase 15 JSONL only. **Not official RAGAS.** CPU Phase 16 tables not overwritten.

Historical (2026-08-27): implementation + mock n=3; official Colab 420 **not launched** / **NEEDS VERIFICATION**.

Official run (verified 2026-08-28): run_id `phase16_judge_20260828T152623Z_06661255`; **420/420 PASS**; `llama_cpp`; Qwen3-8B Q4_K_M; Tesla T4; `used_rag_rerun=false`; UQ `draft_answer`; UQ 78 ANSWER / 62 ABSTAIN; Phase 15 SHA unchanged. Means: SA 0.3241, MA 0.3484, UQ 0.3749, UQ ANSWER-only 0.6548. JSONL is source of truth for judge calls (`temperature=0.0`, `max_new_tokens=32`, `n_ctx=4096`); do not use fingerprint `0.1` / `512`. **Do not rerun the judge.**

## Phase 17 — Statistics (complete; CPU; frozen Phase 15/16)

See `docs/phase17_statistics.md` and `project_record/evidence/phase17_validation.md`.

Entrypoint: `scripts/run_statistics.py`. Statistical unit = question (n=140), paired. RQ1 McNemar SA vs MA displayed correctness **not significant** (p=0.6776). RQ2 LLM-as-judge faithfulness is custom/RAGAS-inspired, **not official RAGAS**. RQ3 abstention at T=0.65 reduces unsupported_emitted (McNemar significant) at coverage 78/140.

Dissertation figures (canonical PNG+PDF; 2026-08-28): `scripts/render_phase17_figures.py` + `results/metrics/phase17_figures/FIGURE_INDEX.md`. Does **not** recompute tests. Main body: `rq1_answer_correctness_95ci`, `rq2_confidence_vs_faithfulness`, `rq3_coverage_vs_selective_accuracy`. Appendix: `rq1_mcnemar_counts`, `rq2_faithfulness_distribution`, `rq3_uq_outcomes`.

**Do not start Phase 20 from this documentation. Do not rerun RAG or the judge.**

## Phase 18 — Qualitative error analysis (complete; CPU; frozen 15/16/17)

See `docs/phase18_error_analysis.md` and `project_record/evidence/phase18_validation.md`.

Entrypoint: `scripts/run_error_analysis.py`. Taxonomy on all 420 cases; stratified sample seed 18 (**81 cases / 42 questions**). Both false abstentions included. No RAG/Qwen/judge/statistics rerun. Numeric error is not labelled hallucination. **Not official RAGAS.**

**Do not start Phase 20 from this documentation.**

## Phase 19 — Final reproducibility and research-integrity audit (complete; CPU; read-only)

See `docs/phase19_reproducibility.md` and `project_record/evidence/phase19_reproducibility_audit.md`.

Entrypoint: `scripts/run_reproducibility_audit.py`. Frozen chain 40 DEV → T=0.65 → 140 test → 420 cases → Phase 16/17/18. No RAG/Qwen/judge/stats rerun. Scientific chain **PASS**. Drive/GitHub **NEEDS VERIFICATION**. Artefact manifest: `results/final/phase19_artefact_manifest.md`.

**Do not start further numbered phases from this documentation.** Phase 20 (live artefact) was completed 2026-08-28.

## Phase 20 — Final live artefact (complete; local plumbing PASS; Colab T4 NV)

See `docs/phase20_live_artefact.md` and `project_record/evidence/phase20_live_artefact_validation.md`.

Entrypoint: `PYTHONPATH=. streamlit run app/streamlit_app.py`. GPU demo: `notebooks/colab_phase11_live.ipynb` (no new benchmark notebook). Locked **T=0.65**. Shared Phase 6 KB. Actual RAG pipelines — not Phase 15 lookup. Sidebar pages: Live RAG Demo, Benchmark Results (read-only frozen metrics), Benchmark Questions (read-only frozen 140).

Local mock three-question demo (`scripts/run_live_demo.py --backend mock`) recorded insufficient-evidence UQ **ABSTAIN** at 0.5351 < 0.65. Official Qwen/T4 answers **NEEDS VERIFICATION**. Frozen 140/40, lock, and Phase 15–18 results unchanged.

At the time of this Phase 20 entry, Phase 21 had not yet started. Phase 21 was completed subsequently as a live-demo launcher only. Do not rerun the 420-case benchmark, calibration, judge, or statistics.

## Phase 21 — Canonical final live-demo launcher (complete; static PASS; Colab T4 NV)

See `docs/phase21_final_live_demo.md` and `project_record/evidence/phase21_validation.md`.

**Canonical viva notebook:** `notebooks/colab_phase21_final_live_demo.ipynb`. Previous live notebooks (`colab_phase11_live.ipynb` and earlier) are historical development/validation evidence.

Launch (Colab VM, from `V2/`): `PYTHONPATH=. python -m streamlit run app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true` with `V2_LIVE_BACKEND=llama_cpp` and `V2_FORBID_MOCK=1`. Browser URL: Colab `proxyPort(8501)`. Does **not** rerun 420, calibration, judge, or statistics. Locked **T=0.65** unchanged.

**Do not start Phase 22. Do not rerun the 420-case benchmark, calibration, judge, or statistics.**

## Git workflow (all phases)

After each completed major phase:

1. `git status` / `git diff`
2. Confirm no V1 changes
3. Run `pytest`
4. Commit: `Phase N: <short description>`

Do not force-push. Do not commit secrets, weights, or large raw dumps.

---

## Authoritative records

| Record | Path |
| --- | --- |
| Master chronology | `V2/project_record/PROJECT_MASTER_RECORD.md` |
| Phase validation evidence | `V2/project_record/evidence/phaseN_validation.md` |
| Decisions | `V2/DECISIONS.md` |
| Context | `V2/PROJECT_CONTEXT.md` |
| Storage spec | `V2/docs/storage_backup_recovery.md` |
| Backup reminder template | `V2/project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md` |
