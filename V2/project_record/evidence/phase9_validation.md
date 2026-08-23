# Phase 9 validation evidence

| Field | Value |
| --- | --- |
| Phase | 9 — Multi-Agent RAG |
| Evidence file | `project_record/evidence/phase9_validation.md` |
| Last updated | 2026-08-23 |
| Phase 9 status | **Implementation complete**; Colab T4 `llama_cpp` smoke **NEEDS VERIFICATION** |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Unit/integration (prompts, verification, mock pipeline) | **PASS** | `tests/test_phase9_multi_agent.py` |
| 2 | Full pytest suite | **PASS** | 49 passed (2026-08-23) |
| 3 | Live multi-agent smoke — local Mac (3 frozen questions) | **PASS** | `results/config/phase9_smoke_test.json` (mock backend) |
| 4 | Colab Multi-Agent smoke — T4 `llama_cpp` (3 frozen questions) | **NEEDS VERIFICATION** | `notebooks/colab_phase9_smoke.ipynb` → `results/config/phase9_*.json` |

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
| Date/time (UTC) | 2026-08-23T13:29:49Z |
| Phase | 9 |
| Test name | `phase9_multi_agent_smoke` (local dev) |
| Command | `PYTHONPATH=. python scripts/smoke_multi_agent.py --backend mock --limit 3` |
| Environment | Local Mac; Phase 6 Chroma KB (preflight PASS 1239/1239); mock Qwen3 backend for draft+verify LLM calls |
| Expected | Each case: 4 evidence chunks, non-empty draft answer, verification_result, no error, decision=ANSWER |
| Actual (observed) | **PASS** — 3/3; run_id `phase9_20260823T132941Z_f4571194`; git `a9d6b0a` |
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
- Superseded for official GPU path by Colab run (section 4) when completed.
- Frozen 140 / calibration 40 **not modified**.

### 4. Colab Multi-Agent RAG smoke — T4 `llama_cpp` (n=3) — **official GPU validation**

| Field | Value |
| --- | --- |
| Date/time (UTC) | **NEEDS VERIFICATION** |
| Phase | 9 |
| Test name | `phase9_colab_multi_agent_smoke` |
| Command | `notebooks/colab_phase9_smoke.ipynb` → restore KB from Drive → preflight → `smoke_multi_agent.py --backend llama_cpp --limit 3` |
| Environment | Google Colab GPU **Tesla T4**; `llama_cpp`; Qwen3-8B Q4_K_M (expected — same as Phase 8) |
| Git commit (notebook clone) | **a9d6b0a** (pushed 2026-08-23; includes Phase 9 source + notebook) |
| Run ID | **NEEDS VERIFICATION** |
| Expected | Preflight PASS (1239 chunks); each case n_evidence=4, non-empty draft answer, verification_result populated, no error; decision=ANSWER |
| Actual (observed) | **Not run from this environment** — Colab GPU notebook must be executed manually |
| Status | **NEEDS VERIFICATION** |
| Error | — |

**Runbook (user action required):**

1. Open `notebooks/colab_phase9_smoke.ipynb` on [Google Colab](https://colab.research.google.com/) with **GPU** runtime.
2. Run all cells (clone branch `cursor/empty-v2-workspace` → install → restore KB from `MyDrive/MSc-RAG/artifacts/knowledge_base/` or rebuild → smoke).
3. Confirm cell 6 prints `status: PASS` and per-case `n_evidence=4`.
4. Run cell 7 to save JSONs to `MyDrive/MSc-RAG/configs/phase9/`.
5. Copy the four `phase9_*.json` / `.jsonl` files into local `V2/results/config/` and re-run this evidence update with observed values.

**Evidence files (when Colab run completes):**

| Role | Path |
| --- | --- |
| PASS status | `results/config/phase9_smoke_test.json` |
| Per-case raw results | `results/config/phase9_multi_agent_smoke.json` |
| Runtime / GPU | `results/config/phase9_runtime_fingerprint.json` |
| Drive archive | `MyDrive/MSc-RAG/configs/phase9/` — **NEEDS VERIFICATION** |

**Notes:**

- No Multi-Agent architecture changes unless the Colab run exposes a genuine compatibility/runtime issue.
- No abstention / combined UQ (Phase 10).
- Frozen 140 / calibration 40 **not modified**.

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 9 — Multi-Agent RAG
