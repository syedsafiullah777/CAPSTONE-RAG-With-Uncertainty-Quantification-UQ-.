# Storage, Backup, Recovery and Monitoring

Project-wide rules for the MSc RAG V2 rebuild.  
Cursor rule: `.cursor/rules/06-storage-backup-recovery.mdc`  
Config: `V2/config/experiment.yaml` → `storage`

---

## 1. Storage strategy

### GitHub = source / version control

**Store:**

- V2 source code, configuration, scripts, tests, documentation, project rules
- sampling manifests, calibration manifests
- final reproducible artefacts and final aggregated metric/statistical tables where appropriate

**Do not normally store:**

- model weights, huge raw experiment outputs, large caches, unnecessary generated files

See `V2/.gitignore` for enforced exclusions.

### Google Colab = computation only

**Use for:**

- Qwen3-8B inference
- knowledge-base heavy processing where required
- calibration, benchmark execution, metric evaluation, statistical processing

**Do not** treat `/content` as the only copy of important data. Sync to Drive during and after runs.

Entrypoint: standard GPU notebooks (e.g. `notebooks/colab_phase7_smoke.ipynb`). Colab CLI / gcloud are **not** used.

### Google Drive = persistent experiment storage

**Logical root:** `Google Drive/MSc-RAG/` (**NEEDS VERIFICATION** — create on your Drive account)

```text
Google Drive/MSc-RAG/
├── results/
│   ├── raw/
│   ├── processed/
│   ├── metrics/
│   └── final/
├── checkpoints/
├── logs/
├── configs/
└── artifacts/
```

**Store on Drive:**

- raw benchmark outputs, checkpoints, progress state, logs
- intermediate metrics, experiment configurations
- large artefacts required to resume interrupted runs

**Do not** create a second permanent copy of the entire V2 repository on Drive.

### Local Mac = secondary / offline backup

- Local V2 repo = main development copy
- After major milestones, copy important Drive results to local Mac
- Never assume local backup exists unless verified

---

## 2. Benchmark recovery

Target: **140 questions × 3 architectures = 420** cases.

Must survive: Colab disconnect, runtime kill, GPU failure, manual stop, timeout, crash, model failure.

| Requirement | Description |
| --- | --- |
| Incremental save | Write each case (or batch) before proceeding |
| Checkpoint state | Persist completed / failed / pending sets |
| Skip completed | Do not re-run successful cases |
| Retry failed | Re-attempt failed cases with limits |
| Duplicate prevention | Unique key `{architecture}:{question_id}` |
| Resume | Continue from latest valid checkpoint |
| No full restart | Never require restart from question 1 |

---

## 3. Raw result storage

Save structured output **before** aggregation. Do not silently overwrite raw data.

Required fields (config: `storage.raw_result_fields`):

run ID, question ID, architecture, question, retrieved evidence, retrieval scores, answer, reference answer, verification result, confidence, threshold, ANSWER/ABSTAIN decision, latency, model, model version, quantisation, device/GPU, configuration, random seed, timestamp, error information.

---

## 4. Backup checkpoints

Create a checkpoint after major phases involving: dataset, 140 sampling, calibration, KB, model/runtime, RAG architecture, benchmark, evaluation, statistics, final artefact.

Before large/destructive operations:

1. verify latest checkpoint exists  
2. verify important files are backed up  
3. then proceed  

Template: `V2/project_record/PHASE_COMPLETION_BACKUP_TEMPLATE.md`

---

## 5. Master project record

`V2/project_record/PROJECT_MASTER_RECORD.md` — authoritative chronology and dissertation evidence.

Updated after every completed phase. Also maintain validation evidence at `project_record/evidence/phaseN_validation.md`.

---

## 6. Validation evidence (every major phase)

See `project_record/evidence/README.md` and `docs/IMPLEMENTATION_PLAN.md`.

Record **actual** observed results. Do not fabricate PASS. Benchmark raw data stays in `results/raw/`; evidence files are concise summaries.

---

## 7. Phase completion reminder

At end of each relevant phase, report:

```text
Backup status:
* Colab: ...
* Google Drive: ...
* Local: ...
* GitHub: ...

Action needed:
* ...
```

**Never claim backup completed unless verified.**

---

## 7. Dissertation support

Preserve verified information for: research aim, objectives, RQs, contribution, dataset, sampling, calibration, KB, retrieval, architectures, model, prompts, confidence, abstention, setup, metrics, statistics, results, error analysis, limitations, live artefact, reproducibility, hardware/runtime, decisions.

Final results come from **saved outputs**, not planning text.

---

## 8. Live artefact

Streamlit uses actual V2 RAG code. Same pipelines support benchmark mode and live demonstration mode. Fresh user questions are not served from precomputed benchmark tables.

---

## 9. Git workflow

After each major phase: status → diff → no V1 changes → pytest → commit (`Phase N: description`).

No force-push. No secrets. No large raw dumps in git.

---

## 10. Workflow summary

```text
Cursor / GitHub (source)
    ↓
Google Colab GPU notebook (compute)
    ↓
Google Drive/MSc-RAG (persistent results/checkpoints)
    ↓
Local Mac (milestone backup)
```
