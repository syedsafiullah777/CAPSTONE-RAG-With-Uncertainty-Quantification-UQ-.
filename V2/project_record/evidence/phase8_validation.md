# Phase 8 validation evidence

| Field | Value |
| --- | --- |
| Phase | 8 — Single-Agent RAG baseline |
| Evidence file | `project_record/evidence/phase8_validation.md` |
| Last updated | 2026-08-22 |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Unit/integration (schema, prompts, mock pipeline) | **PASS** | `tests/test_phase8_single_agent.py` |
| 2 | Full pytest suite | **PASS** | `project_record/evidence/artifacts/phase8_pytest_20260822T164600Z.txt` |
| 3 | Live single-agent smoke (3 frozen questions) | **PASS** | `results/config/phase8_smoke_test.json` |

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
| Actual (observed) | Tests pass as part of full suite (**40 passed**) |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase8_single_agent.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-22T16:46:00 |
| Phase | 8 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -v --tb=short` |
| Environment | Local Mac; `.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **40 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `project_record/evidence/artifacts/phase8_pytest_20260822T164600Z.txt` |

### 3. Live Single-Agent RAG smoke (n=3)

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

**Notes:**
- Frozen 140 / calibration 40 **not modified**.
- No multi-agent / abstention.
- Colab `llama_cpp` path uses the same `run_single_agent()` + verified Phase 7 GPU config; this smoke used local `ollama_dev` for generation while retrieval used the real Phase 6 index.

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 8 — Single-Agent RAG baseline
