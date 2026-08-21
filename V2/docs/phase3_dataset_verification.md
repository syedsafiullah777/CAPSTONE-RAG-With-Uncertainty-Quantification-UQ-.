# Phase 3 — Dataset verification checkpoint

**Status:** complete  
**Scope:** Verify T²-RAGBench FinQA schema, splits, quality signals, and source-PDF resolvability.  
**Out of scope:** frozen 140 selection (Phase 4), calibration freeze (Phase 5), knowledge-base build (Phase 6).

## Load command

```python
from datasets import load_dataset
ds = load_dataset("G4KMU/t2-ragbench", "FinQA")
```

## Verified split sizes

| Split | Rows |
| --- | ---: |
| train | 6251 |
| dev | 883 |
| test | 1147 |
| **total** | **8281** |

## Schema (21 columns)

`id`, `context_id`, `split`, `question`, `program_answer`, `original_answer`, `context`, `table`, `pre_text`, `post_text`, `file_name`, `company_name`, `company_symbol`, `report_year`, `page_number`, `company_sector`, `company_industry`, `company_headquarters`, `company_date_added`, `company_cik`, `company_founded`.

## Structure notes

- **Question / answers:** `question` is context-independent; evaluate primarily with `program_answer`; keep `original_answer` for display/judge context (`original_answer` missing on a small fraction of rows).
- **Oracle context:** `context` (+ `pre_text` / `table` / `post_text`) is the gold supporting passage — **evaluation only**, not the live retriever output.
- **Provenance:** `context_id`, `file_name`, `page_number`, company/report metadata support stratified sampling and KB metadata.

## Quality signals (for Phase 4 filters)

- Test: 1 empty `question`; 14 empty `original_answer`; essential-eligible ≈ **1146** (≥ 140).
- Duplicate question text: train 14 groups, test 1 group, dev 0 — **dedupe before freeze**.
- IDs unique within and across splits.

## Source documents / PDFs

- `load_dataset` does **not** return PDF bytes.
- Hugging Face dataset repo contains FinQA page PDFs under `data/FinQA/{split}/...`.
- Mapping rule: `repo_path = data/FinQA/{split}/{file_name}`  
  Example: `file_name=pdf/AAL/2010/page_72.pdf` → `data/FinQA/test/pdf/AAL/2010/page_72.pdf`.
- **Test split:** 380 unique `file_name` values; **380/380** resolve in the repo (match rate 100%).
- Unique FinQA PDFs in repo: **2789** (matches card document count).

Artefact: `V2/data/processed/finqa_pdf_probe.json`.

## RQ implications (unchanged; still binding)

- **RQ1:** Test pool large enough; dedupe questions for paired analysis.
- **RQ2:** No unsupported/hallucination label — pre-register evidence-grounded definition later.
- **RQ3:** No insufficient-evidence label; abstention criteria must come from retrieval/verify signals, not a dataset field.
- **All:** Building a KB from gold `context` would invalidate RAG claims.

## Sampling readiness

- Final evaluation pool: FinQA **test**.
- Calibration pool: FinQA **dev**.
- Frozen 140: **not selected in Phase 3**.

## Related artefacts

- Full profile: `V2/docs/dataset_profile.md`
- Machine-readable profile: `V2/data/processed/finqa_profile.json`
- V1 lessons: `V2/docs/v1_audit.md`
- Re-run profile: `PYTHONPATH=. python scripts/inspect_dataset.py`

## Definition of done

- [x] FinQA loaded live
- [x] Splits and row counts documented
- [x] Columns documented
- [x] Missing/duplicate signals documented
- [x] Source PDF resolvability verified for test `file_name`s
- [x] No 140 freeze performed
- [x] V1 untouched
