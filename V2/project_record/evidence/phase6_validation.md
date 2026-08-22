# Phase 6 validation evidence

| Field | Value |
| --- | --- |
| Phase | 6 — Knowledge base (source PDFs) |
| Evidence file | `project_record/evidence/phase6_validation.md` |
| Last updated | 2026-08-21 (index build); tests re-verified 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | KB unit/integration tests | PASS | `tests/test_phase6_knowledge_base.py` |
| 2 | Index build manifest | PASS | `knowledge_base/index/index_manifest.json` |
| 3 | Retrieval demo | PASS | `knowledge_base/index/retrieval_demo.json` |

---

## Test records

### 1. Source-PDF index build

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-21T16:20:26Z (`built_at_utc`) |
| Phase | 6 |
| Test name | `build_index.py` + retrieval smoke |
| Command | `PYTHONPATH=. python scripts/build_index.py` |
| Environment | Local Mac CPU; `BAAI/bge-small-en-v1.5`; Chroma |
| Expected | 230 PDFs indexed; chunks persisted; no gold-context ingestion |
| Actual (observed) | **230** docs indexed; **1239** chunks; **0** download failures; demo top hit `pdf/SNA/2013/page_34.pdf` |
| Status | **PASS** |
| Error | — |
| Output path | `knowledge_base/index/index_manifest.json` |

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 6 — Knowledge base
