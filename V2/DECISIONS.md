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
