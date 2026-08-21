# FinQA (T²-RAGBench) dataset profile — Phases 2–3

Generated (UTC): `2026-08-21T15:52:54.702322+00:00`  
Phase 3 PDF probe: see `docs/phase3_dataset_verification.md` and `data/processed/finqa_pdf_probe.json`.

- Dataset: `G4KMU/t2-ragbench` subset `FinQA`
- Load: `load_dataset("G4KMU/t2-ragbench", "FinQA")`
- Total rows: **8281**
- Columns match expected schema: **True**

## Splits and row counts

- **train**: 6251
- **dev**: 883
- **test**: 1147

## Columns

- `id`
- `context_id`
- `split`
- `question`
- `program_answer`
- `original_answer`
- `context`
- `table`
- `pre_text`
- `post_text`
- `file_name`
- `company_name`
- `company_symbol`
- `report_year`
- `page_number`
- `company_sector`
- `company_industry`
- `company_headquarters`
- `company_date_added`
- `company_cik`
- `company_founded`

## Split `train`

- Rows: **6251**
- Unique `id`: 6251 (duplicate id groups: 0)
- Unique questions: 6237 (duplicate question groups: 14; extra rows: 14)
- Unique `context_id`: 2110
- Unique `file_name`: 2110
- Unique `company_name`: 134
- Essential-field rows (id, question, answer, context_id, file_name, context): **6251**
- `program_answer` == `original_answer` rate: 0.0434
- Question length (chars): mean=179.41, median=174
- Context length (chars): mean=4558.91, median=4470
- Table length (chars): mean=861.48, median=679

### Missing values

- `original_answer`: 48 (0.77%)

### Duplicate question examples

- count=2: "What proportion of Devon Energy's estimated 2005 oil production, in million barrels (mmbbls), is expected to come from unproved reserves as of December 31, 2004"
- count=2: "What percentage of A. O. Smith's total aggregate contractual obligations as of December 31, 2010, is composed of long-term debt?"
- count=2: 'What is the difference between the statutory tax rate and the effective tax rate for international operations in 2018 for Aon?'
- count=2: 'What was the percentage increase in net income attributable to noncontrolling interests, net of tax, from fiscal 2008 to fiscal 2009 for Global Payments?'
- count=2: "In 2016, as part of Entergy Arkansas' intent to implement a forward test year formula rate plan pursuant to Arkansas legislation passed in 2015, what was the ra"

## Split `dev`

- Rows: **883**
- Unique `id`: 883 (duplicate id groups: 0)
- Unique questions: 883 (duplicate question groups: 0; extra rows: 0)
- Unique `context_id`: 299
- Unique `file_name`: 299
- Unique `company_name`: 96
- Essential-field rows (id, question, answer, context_id, file_name, context): **883**
- `program_answer` == `original_answer` rate: 0.043
- Question length (chars): mean=176.29, median=173
- Context length (chars): mean=4487.64, median=4418
- Table length (chars): mean=852.57, median=643

### Missing values

- `original_answer`: 12 (1.36%)

## Split `test`

- Rows: **1147**
- Unique `id`: 1147 (duplicate id groups: 0)
- Unique questions: 1146 (duplicate question groups: 1; extra rows: 1)
- Unique `context_id`: 380
- Unique `file_name`: 380
- Unique `company_name`: 99
- Essential-field rows (id, question, answer, context_id, file_name, context): **1146**
- `program_answer` == `original_answer` rate: 0.0392
- Question length (chars): mean=181.58, median=175
- Context length (chars): mean=4451.78, median=4510
- Table length (chars): mean=864.59, median=699

### Missing values

- `original_answer`: 14 (1.22%)
- `question`: 1 (0.09%)

### Duplicate question examples

- count=2: 'What was the percentage increase in the average price of WTI crude oil from 2011 to 2013 for Marathon Oil, as reflected in the benchmark crude oil price average'

## Question / answer / context structure

- **Question:** context-independent FinQA query string (`question`).
- **Reference answers:** `program_answer` (numeric/program-normalised; primary for evaluation) and `original_answer` (source form).
- **Oracle context:** `context` combines supporting text/table evidence for the item; also available as `pre_text`, `table`, `post_text`.
- **Provenance:** `context_id`, `file_name`, `page_number`, company/report metadata.

## Source documents / PDFs

- Unique `file_name` values across splits: **2789**
- PDFs as row blobs in `load_dataset`: **False**
- Dataset card claims PDFs available via repo clone: **True**
- **Phase 3 verified mapping:** `repo_path = data/FinQA/{split}/{file_name}`
- **Test PDFs:** 380/380 unique `file_name` values resolve in the HF dataset repo (100%).
- Note: Official card: clone or download from G4KMU/t2-ragbench under `data/FinQA/{train,dev,test}/`. `load_dataset()` returns text/metadata columns, not PDF bytes.
- Detail: `docs/phase3_dataset_verification.md`, `data/processed/finqa_pdf_probe.json`
- Example `file_name` values:
  - `pdf/AAL/2010/page_72.pdf`
  - `pdf/AAL/2013/page_15.pdf`
  - `pdf/AAL/2013/page_172.pdf`
  - `pdf/AAL/2013/page_18.pdf`
  - `pdf/AAL/2014/page_15.pdf`
  - `pdf/AAL/2014/page_18.pdf`
  - `pdf/AAL/2014/page_219.pdf`
  - `pdf/AAL/2014/page_59.pdf`
  - `pdf/AAL/2014/page_80.pdf`
  - `pdf/AAL/2014/page_89.pdf`

## Sampling readiness (no 140 selected in Phases 2–3)

- **recommended_test_pool**: test
- **recommended_calibration_pool**: dev
- **frozen_test_target**: 140
- **test_rows**: 1147
- **test_essential_eligible_estimate**: 1146
- **dev_rows**: 883
- **can_support_140_from_test**: True
- **phase2_selected_140**: False
- **phase3_selected_140**: False

## RQ implications

- **RQ1/RQ2/RQ3** [info]: Test pool size 1147, essential-eligible ≈ 1146 — enough for a 140 sample.
- **RQ1 (paired tests)** [medium]: Duplicate question text exists in test; sampling must dedupe by question/id.
- **RQ2** [medium]: No native hallucination/unsupported label. Must pre-register an evidence-grounded definition using retrieved evidence + verification (not wrong≠hallucination).
- **RQ3** [high]: No insufficient_evidence label. Gold context is oracle; every row has supporting C. Abstention/insufficient criteria must be pre-registered from retrieval/verify signals (and optional withheld-document probes), not a dataset field.
- **All** [high]: Feeding gold `context` to the generator as retrieval would invalidate RAG claims. KB must use source documents (file_name / PDFs), with gold context for evaluation only.

## Phase 2–3 boundary

- Final 140 **not** selected.
- Knowledge base **not** built.
- RAG architectures **not** implemented.
