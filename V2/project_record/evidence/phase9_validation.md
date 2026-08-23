# Phase 9 validation evidence

| Field | Value |
| --- | --- |
| Phase | 9 — Multi-Agent RAG |
| Evidence file | `project_record/evidence/phase9_validation.md` |
| Last updated | 2026-08-23 |
| Phase 9 status | **Complete** (local smoke verified) |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Unit/integration (prompts, verification, mock pipeline) | **PASS** | `tests/test_phase9_multi_agent.py` |
| 2 | Full pytest suite | **PASS** | 49 passed (2026-08-23) |
| 3 | Live multi-agent smoke — local Mac (3 frozen questions) | **PASS** | `results/config/phase9_smoke_test.json` |

---

## Test records

### 1. Unit/integration tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T13:07:00 |
| Phase | 9 |
| Test name | `test_phase9_multi_agent` |
| Command | `PYTHONPATH=. pytest tests/test_phase9_multi_agent.py -v` |
| Environment | Local Mac; `.venv` |
| Expected | Draft + verification pipeline; verification_result populated; decision=ANSWER; threshold null |
| Actual (observed) | **6 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase9_multi_agent.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T13:07:00 |
| Phase | 9 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -v --tb=short` |
| Environment | Local Mac; `.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **49 passed** |
| Status | **PASS** |
| Error | — |

### 3. Live Multi-Agent RAG smoke — local Mac (n=3)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T13:07:54Z |
| Phase | 9 |
| Test name | `phase9_multi_agent_smoke` |
| Command | `PYTHONPATH=. python scripts/smoke_multi_agent.py --backend mock --limit 3` |
| Environment | Local Mac; Phase 6 Chroma KB (preflight PASS 1239/1239); mock Qwen3 backend for draft+verify LLM calls |
| Expected | Each case: 4 evidence chunks, non-empty draft answer, verification_result, no error, decision=ANSWER |
| Actual (observed) | **PASS** — 3/3; run_id `phase9_20260823T130745Z_22fab337` |
| Status | **PASS** |
| Error | — |
| Output path | `results/config/phase9_multi_agent_smoke.json`, `phase9_smoke_test.json` |

**Per-case (observed):**

| question_id | n_evidence | verification_score | status | decision |
| --- | --- | --- | --- | --- |
| finqa_test_1000 | 4 | 0.425 | WEAK_EVIDENCE | ANSWER |
| finqa_test_1012 | 4 | 0.425 | WEAK_EVIDENCE | ANSWER |
| finqa_test_1017 | 4 | 0.425 | WEAK_EVIDENCE | ANSWER |

**Notes:**

- Mock backend used for generation/verification LLM calls; **real retrieval** from existing Phase 6 index (no KB rebuild).
- WEAK_EVIDENCE expected with mock canned answers (low lexical overlap); pipeline exercised end-to-end.
- Colab `llama_cpp` smoke **NEEDS VERIFICATION** (optional GPU parity before full benchmark).
- No abstention / combined UQ (Phase 10).
- Frozen 140 / calibration 40 **not modified**.

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 9 — Multi-Agent RAG
