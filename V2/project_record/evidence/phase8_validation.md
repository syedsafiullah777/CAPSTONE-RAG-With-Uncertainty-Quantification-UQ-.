# Phase 8 validation evidence

| Field | Value |
| --- | --- |
| Phase | 8 — Single-Agent RAG baseline |
| Evidence file | `project_record/evidence/phase8_validation.md` |
| Last updated | 2026-08-23 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Unit/integration (schema, prompts, mock pipeline) | **PASS** | `tests/test_phase8_single_agent.py` |
| 2 | Full pytest suite | **PASS** | 43 passed (2026-08-23 local run) |
| 3 | Live single-agent smoke — local Mac (3 frozen questions) | **PASS** | `results/config/phase8_smoke_test.json` |
| 4 | Index preflight validation | **PASS** | `scripts/validate_kb_index.py` |
| 5 | Colab Single-Agent RAG smoke — T4 `llama_cpp` (n=3) | **NEEDS VERIFICATION** | Run `notebooks/colab_phase8_smoke.ipynb` |

---

## Test records

### 1. Unit/integration tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:46:00 |
| Phase | 8 |
| Test name | `test_phase8_single_agent` |
| Command | `PYTHONPATH=. pytest tests/test_phase8_single_agent.py -v` |
| Environment | Local Mac; `.venv` |
| Expected | Schema fields present; mock retrieve+generate works; decision=ANSWER; no UQ fields |
| Actual (observed) | Tests pass as part of full suite |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase8_single_agent.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23 |
| Phase | 8 (incl. preflight tests) |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -v --tb=short` |
| Environment | Local Mac; `.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **43 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_index_preflight.py`, `tests/test_phase8_single_agent.py`, … |

### 3. Live Single-Agent RAG smoke — local Mac (n=3)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:45:59 |
| Phase | 8 |
| Test name | `phase8_single_agent_smoke` |
| Command | `PYTHONPATH=. python scripts/smoke_single_agent.py --backend ollama_dev --limit 3` |
| Environment | Local Mac; Phase 6 Chroma KB; Ollama `qwen3:8b` (`think=False`); device `mps_capable_host` |
| Expected | Each case: non-empty retrieved_evidence (top_k=4), non-empty answer, no error |
| Actual (observed) | **PASS** — 3/3 cases; architecture `single_agent`; run_id `phase8_20260822T164524Z_bd962134` |
| Status | **PASS** |
| Error | — |
| Output path | `results/config/phase8_single_agent_smoke.json`, `phase8_smoke_test.json` |

**Per-case (observed):**

| question_id | n_evidence | top score | answer preview |
| --- | --- | --- | --- |
| finqa_test_1000 | 4 | 0.8718 | non-empty (S&P ROI / Snap-on); top file `pdf/SNA/2013/page_34.pdf` |
| finqa_test_1012 | 4 | 0.7765 | non-empty |
| finqa_test_1017 | 4 | 0.8166 | non-empty |

### 4. Index preflight validation (Colab fix)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23 |
| Phase | 8 |
| Test name | `validate_kb_index` + `test_index_preflight` |
| Command | `PYTHONPATH=. python scripts/validate_kb_index.py`; `pytest tests/test_index_preflight.py -v` |
| Environment | Local Mac; existing Phase 6 Chroma index |
| Expected | Manifest `chunks` matches `collection.count()`; empty-index fixture fails with actionable error |
| Actual (observed) | Preflight **PASS** — expected=1239, actual=1239; unit tests **3 passed** (incl. empty-index failure case) |
| Status | **PASS** |
| Error | — |
| Output path | `src/retrieval/preflight.py`, `scripts/validate_kb_index.py` |

### 5. Colab Single-Agent RAG smoke — T4 `llama_cpp` (n=3)

| Field | Value |
| --- | --- |
| Date/time (UTC) | — |
| Phase | 8 |
| Test name | `phase8_colab_single_agent_smoke` |
| Command | Run all cells in `notebooks/colab_phase8_smoke.ipynb` |
| Environment | Google Colab GPU (T4); clone → `build_index.py --distractors 50` → preflight → `smoke_single_agent.py --backend llama_cpp --limit 3` |
| Expected | Index rebuild 1239 chunks; preflight PASS; each case n_evidence=4, non-empty answer; `phase8_smoke_test.json` status PASS |
| Actual (observed) | **Not run from this environment** — Colab execution required |
| Status | **NEEDS VERIFICATION** |
| Error | — |
| Output path | `results/config/phase8_smoke_test.json` (after Colab run) |

**Colab workflow (Option B — no Mac DB copy):**

1. `scripts/build_index.py --distractors 50` — downloads FinQA PDFs from Hugging Face, rebuilds Chroma
2. `scripts/validate_kb_index.py` — manifest vs `collection.count()`
3. `scripts/smoke_single_agent.py --backend llama_cpp --limit 3` — preflight runs again before cases

**Notes:**
- Frozen 140 / calibration 40 **not modified**.
- Retrieval config unchanged (top_k=4, `finqa_source_pdfs`, BGE).
- Diagnosis: `project_record/evidence/phase8_colab_retrieval_diagnosis.md`

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 8 — Single-Agent RAG baseline
