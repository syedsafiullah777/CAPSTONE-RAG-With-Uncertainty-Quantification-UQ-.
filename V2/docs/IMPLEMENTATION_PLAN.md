# V2 Implementation Plan

Approved phased plan for the MSc RAG V2 rebuild.  
Actual code, configuration, tests, and saved outputs take precedence over this document.

| Field | Value |
| --- | --- |
| Last updated | 2026-08-23 |
| Current completed phase | **Phase 11** |
| Next implementation phase | Pilot / calibration lock / 420-case benchmark (not started) |
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
Cursor rule: `.cursor/rules/06-storage-backup-recovery.mdc`  
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
| 12 | Streamlit live artefact | ✅ Absorbed into Phase 11 | `evidence/phase11_validation.md` |
| 13 | Pilot run | ⬜ Not started | concise summary → raw/checkpoints on Drive |
| 14 | Calibration / threshold lock | ⬜ Not started | calibration evidence |
| 15 | 420-case benchmark | ⬜ Not started | summary only; raw in `results/raw/` |
| 16 | Evaluation + metrics | ⬜ Not started | metrics evidence → Drive |
| 17 | Statistics + final tables | ⬜ Not started | aggregated tables evidence |
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
