# Phase 4 — Frozen 140-question FinQA test set

**Status:** complete  
**Frozen artefacts:**
- `V2/data/final/selected_140_questions.csv`
- `V2/data/final/sampling_manifest.json`
- Snapshot: `V2/results/config/phase4_sampling_manifest.json`

## Method

1. Load FinQA **test** split only (`G4KMU/t2-ragbench`, `FinQA`).
2. Keep rows with non-empty: `id`, `question`, `program_answer`, `context_id`, `file_name`, `context`.
3. Deduplicate by normalized question text (keep lowest `id`).
4. Seeded shuffle (`sampling_seed=42`).
5. Greedy diversity selection until **140**:
   - max **3** questions per company (`company_symbol` / name)
   - max **1** question per `file_name`
6. Sort selected rows by `id` for stable CSV ordering.
7. Write CSV + manifest with SHA-256 over selected ids.

## Freeze summary

See `sampling_manifest.json` for exact ids and distributions. Do **not** change this set because of experimental results.

Calibration remains **Phase 5** (FinQA **dev** only).

## Reproduce

```bash
cd V2
source .venv/bin/activate
PYTHONPATH=. python scripts/select_140.py
# Existing freeze is left unchanged unless --force is passed.
```

## Out of scope for Phase 4

- Calibration set
- PDF download / knowledge base
- RAG architectures
- Benchmark runs
