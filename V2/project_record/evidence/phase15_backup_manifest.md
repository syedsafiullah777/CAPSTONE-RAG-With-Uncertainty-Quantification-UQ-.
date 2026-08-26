# Phase 15 backup / sync checklist

| Field | Value |
| --- | --- |
| Date (local inspection) | 2026-08-27 |
| Verified at UTC | 2026-08-26T23:38:22Z |
| Run ID | `phase15_20260826T203744Z_dae9c3a4` |
| Benchmark rerun | **not performed** |
| Frozen 140/40, T=0.65, RAG modules, V1, JSONL | **not modified** |
| Machine-readable copy | `project_record/evidence/artifacts/phase15_backup_manifest.json` |

## Completeness (local Mac, observed)

| Check | Result |
| --- | --- |
| Frozen test questions | **140** unique `finqa_test_*` IDs; set equals `data/final/selected_140_questions.csv` / Phase 4 manifest |
| Architectures | `single_agent` 140, `multi_agent` 140, `multi_agent_uq` 140 |
| Planned keys | 140 × 3 = **420** |
| JSONL lines | **420** |
| Unique `{architecture}:{question_id}` | **420** |
| Duplicates | **0** |
| Missing vs planned | **0** |
| Extra vs planned | **0** |
| DEV IDs leaked | **0** |
| `error` field set | **0** |
| `case_status=COMPLETED` | **420** |
| Summary `n_completed` / `n_failed` / `n_pending` | **420 / 0 / 0** |
| Checkpoint completed list | **420**; failed `{}`; pending `[]` |
| Log `OK` progress lines | **420**; ends `status=PASS completed=420` |
| Locked T | **0.65** (`threshold.lock.json`; UQ 140/140; `used_frozen_test_140=false`) |
| Model / backend / device | Qwen3-8B **Q4_K_M**, `llama_cpp`, `cuda`, Tesla T4 (all 420 rows) |
| Evidence chunks | **4** per case |
| Schema `storage.raw_result_fields` | all present |
| Decisions (descriptive, not scored here) | single/multi: 140 ANSWER each; UQ: 78 ANSWER + 62 ABSTAIN |
| Latency (s) | 16.96–47.85 |
| `results/processed/` | empty (`.gitkeep` only) — Phase 16 |
| `results/final/` | empty (`.gitkeep` only) — later |

JSONL SHA-256: `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa`

Checkpoint `question_ids_sha256` (`8b7061d4…`) is the runner’s ID-list hash, not Phase 4 `selected_ids_sha256` (`1a69d93e…`). The **ID set** matches the freeze.

## Roles (project storage model)

| Layer | Role |
| --- | --- |
| Local Mac | Dev copy + offline backup of raw 420 + configs + log |
| Google Drive | Persistent experiment archive (self-reported sync; folder **not listed from this machine**) |
| GitHub | Source, docs, evidence, small config snapshots — **not** raw JSONL |
| Colab `/content` | Ephemeral — do not rely on it |

Drive self-report (from `phase15_benchmark_summary.json`, **not** independently listed):

`/content/drive/MyDrive/MSc-RAG/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4`

## File-by-file checklist

Legend: Local = exists on this Mac now. Drive verified = listed from this machine (none were).

| Path | Purpose | Size | Local now | Local keep | Drive keep | GitHub | Status |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` | Raw 420 cases | 3 123 276 | yes | **yes** | **yes** | **no** (LARGE/RAW) | VERIFIED_LOCAL |
| `…/checkpoint.json` | Progress / resume | 19 577 | yes | **yes** | **yes** | **no** | VERIFIED_LOCAL |
| `…/summary.json` | Per-run summary | 20 375 | yes | **yes** | **yes** | **no** | VERIFIED_LOCAL |
| `results/checkpoints/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4.json` | Checkpoint copy (byte-identical to raw checkpoint) | 19 577 | yes | **yes** | **yes** | **no** | VERIFIED_LOCAL |
| `results/logs/phase15_20260826T203639Z.log` | Colab run log | 329 457 | yes | **yes** | **yes** | **no** | VERIFIED_LOCAL |
| `results/config/phase15_benchmark_summary.json` | Completion summary | 20 713 | yes | **yes** | **yes** | **yes** | VERIFIED_LOCAL |
| `results/config/phase15_runtime_fingerprint.json` | GPU / model fingerprint | 1 187 | yes | **yes** | **yes** | **yes** | VERIFIED_LOCAL |
| `results/config/phase15_smoke_test.json` | Machine-readable PASS record | 1 901 | yes | **yes** | **yes** | **yes** | VERIFIED_LOCAL |
| `results/config/threshold.lock.json` | Official T=0.65 | 33 873 | yes | **yes** | **yes** | **yes** | VERIFIED_LOCAL |
| `results/processed/*` | Metrics (Phase 16) | — | none | n/a | n/a | n/a | not generated |
| `results/final/*` | Final tables | — | none | n/a | n/a | n/a | not generated |
| `notebooks/colab_phase15_full_benchmark.ipynb` | Colab notebook | 15 646 | yes | yes | no | **yes** (already on origin) | VERIFIED_LOCAL |
| `scripts/run_full_benchmark.py` | Official runner | 7 275 | yes | yes | no | **yes** (already on origin) | VERIFIED_LOCAL |
| `docs/phase15_full_benchmark.md` | Phase 15 docs | — | yes | yes | no | **yes** | VERIFIED_LOCAL |
| `project_record/evidence/phase15_validation.md` | Evidence | — | yes | yes | no | **yes** | VERIFIED_LOCAL |
| `project_record/evidence/phase15_backup_manifest.md` | This checklist | — | yes | yes | no | **yes** | this file |
| `project_record/PROJECT_MASTER_RECORD.md` | Master record | — | yes | yes | no | **yes** | VERIFIED_LOCAL |
| `docs/IMPLEMENTATION_PLAN.md` | Plan | — | yes | yes | no | **yes** | VERIFIED_LOCAL |

`.gitignore` previously ignored `results/config/**` after the phase15 un-ignore lines, so lock + summaries were **not** on GitHub. Un-ignore rules were repeated **after** `results/config/**` so those small files can be committed.

## Required vs optional

**REQUIRED on local Mac (already present):** raw run-id folder (3 files), checkpoint copy, log, three `phase15_*.json` configs, `threshold.lock.json`.

**REQUIRED on Google Drive (existence NEEDS VERIFICATION):** same raw run-id folder, checkpoint copy, `configs/phase15/` summaries, `logs/phase15/` (or the phase15 log).

**SHOULD commit to GitHub:** source, tests, docs, evidence, master record, plan, `threshold.lock.json`, three small `phase15_*.json` configs, this manifest.

**MUST NOT commit to GitHub:** `cases.jsonl`, raw/checkpoint JSON, the 329 KB log.

## Google Drive

**NEEDS VERIFICATION** — this machine did not list Drive. Colab summary reported `synced: true` to the path above. Confirm in the Drive UI before treating Drive as the archive.

## GitHub

Branch `cursor/empty-v2-workspace` was **clean** at inspection (`d1a4aaa` on origin). Phase 15 **source** is already pushed. Local raw/config/log files were gitignored / untracked. After this verification, commit the new evidence + allowlisted config snapshots (not the JSONL).
