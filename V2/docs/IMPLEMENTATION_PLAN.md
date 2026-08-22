# V2 Implementation Plan

Approved phased plan for the MSc RAG V2 rebuild.  
Actual code, configuration, tests, and saved outputs take precedence over this document.

| Field | Value |
| --- | --- |
| Last updated | 2026-08-22 |
| Current completed phase | **Phase 7** |
| Next implementation phase | Phase 8 — Single-Agent RAG baseline (not started) |
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

1. Update `V2/project_record/PROJECT_MASTER_RECORD.md`
2. Report backup status using `V2/project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md`
3. Run tests; review git status/diff; commit if appropriate
4. Stop before starting the next phase

### Live artefact

Streamlit demo uses the same V2 RAG pipelines as benchmark mode (not precomputed lookup for new questions). Session outputs follow Drive persistence rules where applicable.

### Explicitly excluded infrastructure

Colab CLI, gcloud, ADC, Kubernetes, distributed orchestration — unless explicitly required later.

---

## Phase overview

| Phase | Name | Status | Storage notes |
| --- | --- | --- | --- |
| 1 | Project foundation | ✅ Complete | GitHub: code/config/tests |
| 2 | V1 audit + FinQA profile | ✅ Complete | GitHub: profile JSON + docs |
| 3 | PDF resolvability | ✅ Complete | GitHub: probe JSON + checkpoint doc |
| 4 | Freeze test 140 | ✅ Complete | GitHub: CSV + manifest (authoritative) |
| 5 | Freeze calibration 40 | ✅ Complete | GitHub: CSV + manifest |
| 6 | Knowledge base | ✅ Complete | GitHub: index manifest; KB bulk on local/Drive not git |
| 7 | Qwen3-8B backend | ✅ Complete | GitHub: smoke/fingerprint configs; Colab GPU **NEEDS VERIFICATION** |
| 8 | Single-Agent RAG baseline | ⬜ Not started | Log raw per-case outputs; design for 420-case resume |
| 9 | Multi-Agent RAG | ⬜ Not started | Same storage/recovery contract |
| 10 | Multi-Agent + UQ / abstention | ⬜ Not started | Same; include confidence/threshold fields |
| 11 | Result schema + logging | ⬜ Not started | Implement `storage.raw_result_fields` in code |
| 12 | Streamlit live artefact | ⬜ Not started | Live mode ≠ benchmark lookup |
| 13 | Pilot run | ⬜ Not started | Drive checkpoints + incremental saves |
| 14 | Calibration / threshold lock | ⬜ Not started | DEV only; lock file to GitHub when ready |
| 15 | 420-case benchmark | ⬜ Not started | Full recovery contract mandatory |
| 16 | Evaluation + metrics | ⬜ Not started | Raw before aggregation; metrics to Drive |
| 17 | Statistics + final tables | ⬜ Not started | Final aggregated tables → GitHub where appropriate |
| 18 | Dissertation evidence pack | ⬜ Not started | Master record + verified artefact paths |

Phase numbers 11–18 are indicative; adjust if merged — storage requirements remain.

---

## Phase details (completed summary)

Phases 1–7 chronology and evidence: `V2/project_record/PROJECT_MASTER_RECORD.md`

**Next validation (not a new dev phase):** Colab GPU smoke via `notebooks/colab_phase7_smoke.ipynb` — **NEEDS VERIFICATION**

---

## Phase 8 — Single-Agent RAG baseline (next; not started)

**Objective:** Baseline RAG pipeline using frozen KB + Qwen3-8B backend.

**Storage / recovery (required from design):**

- Per-case raw JSONL compatible with `storage.raw_result_fields`
- Checkpoint file under `results/checkpoints/` (local) mirrored to Drive `checkpoints/`
- Skip/resume by `{architecture}:{question_id}`
- No silent overwrite of raw results

**Do not start until explicitly approved.**

---

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
| Decisions | `V2/DECISIONS.md` |
| Context | `V2/PROJECT_CONTEXT.md` |
| Storage spec | `V2/docs/storage_backup_recovery.md` |
| Backup reminder template | `V2/project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md` |
