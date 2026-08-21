# Phase 5 — Frozen FinQA DEV calibration set

**Status:** complete  
**Purpose:** confidence / threshold **development only** (threshold not locked yet).

## Artefacts

- `V2/data/calibration/calibration_questions.csv`
- `V2/data/calibration/calibration_manifest.json`
- Snapshot: `V2/results/config/phase5_calibration_manifest.json`

## Method

1. Require Phase 4 freeze (`selected_140_questions.csv`).
2. Load FinQA **dev** only.
3. Same essential-field filter + question dedupe as Phase 4.
4. Drop any row whose `id` or normalized question overlaps the frozen test 140.
5. Seeded diversity sample (`calibration_seed=42`):
   - **n = 40**
   - max **2** per company
   - max **1** per `file_name`
6. Write CSV + manifest. `threshold_locked: false`.

## Freeze summary

| Item | Value |
| --- | --- |
| n | 40 |
| Seed | 42 |
| Companies | 32 |
| Files | 40 |
| SHA-256 (ids) | `b229d45331fc18dd7c784175abd37cee3550775f268c843b2417d3f9d2e3aeca` |
| Overlap with test 140 | none (ids and questions) |
| Threshold lock | **not created** |

## Reproduce

```bash
cd V2
PYTHONPATH=. python scripts/select_calibration.py
# Does not overwrite unless --force
```

## Explicitly not done in Phase 5

- Threshold selection / `threshold.lock.json`
- Knowledge-base construction
- RAG architectures
- Test-set evaluation
