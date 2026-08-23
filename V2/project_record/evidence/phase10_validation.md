# Phase 10 validation evidence

| Field | Value |
| --- | --- |
| Phase | 10 — Multi-Agent RAG + UQ / abstention |
| Evidence file | `project_record/evidence/phase10_validation.md` |
| Last updated | 2026-08-23 |
| Phase 10 status | **Complete** (local + Colab smoke verified) |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Unit/integration (UQ, abstention gate, mock pipeline) | **PASS** | `tests/test_phase10_multi_agent_uq.py` |
| 2 | Full pytest suite | **PASS** | 55 passed (2026-08-23) |
| 3 | Live multi_agent_uq smoke — local Mac (3 frozen questions) | **PASS** | `results/config/phase10_smoke_test.json` (mock backend; dev only) |
| 4 | Colab multi_agent_uq smoke — T4 `llama_cpp` (3 frozen questions) | **PASS** | `results/config/phase10_smoke_test.json` |

---

## Test records

### 1. Unit/integration tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T14:58:00 |
| Phase | 10 |
| Test name | `test_phase10_multi_agent_uq` |
| Command | `PYTHONPATH=. pytest tests/test_phase10_multi_agent_uq.py -v` |
| Environment | Local Mac; `.venv` |
| Expected | Combined confidence, threshold, ANSWER/ABSTAIN gate, uncertainty_result, schema fields |
| Actual (observed) | **6 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase10_multi_agent_uq.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T14:58:00 |
| Phase | 10 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -q` |
| Environment | Local Mac; `.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **55 passed** |
| Status | **PASS** |
| Error | — |

### 3. Live Multi-Agent + UQ smoke — local Mac (n=3)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T14:58:09Z |
| Phase | 10 |
| Test name | `phase10_multi_agent_uq_smoke` (local dev) |
| Command | `PYTHONPATH=. python scripts/smoke_multi_agent_uq.py --backend mock --limit 3` |
| Environment | Local Mac; Phase 6 Chroma KB; mock Qwen3 backend |
| Expected | Each case: evidence, verification_result, uncertainty_result, confidence, threshold, decision ∈ {ANSWER, ABSTAIN} |
| Actual (observed) | **PASS** — 3/3; run_id `phase10_20260823T135800Z_bb26b25c`; all `ANSWER` at smoke threshold 0.55 |
| Status | **PASS** |
| Error | — |
| Output path | `results/config/phase10_multi_agent_uq_smoke.json` (superseded by Colab run for official GPU path) |

### 4. Colab Multi-Agent + UQ smoke — T4 `llama_cpp` (n=3) — **official GPU validation**

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-23T14:10:15Z** |
| Phase | 10 |
| Test name | `phase10_colab_multi_agent_uq_smoke` |
| Command | `notebooks/colab_phase10_smoke.ipynb` → restore KB → preflight → `smoke_multi_agent_uq.py --backend llama_cpp --limit 3` |
| Environment | Google Colab GPU **Tesla T4**; CUDA; Python 3.13.15; `llama_cpp` 0.3.35 |
| Model | **Qwen3-8B** Q4_K_M (`bartowski/Qwen_Qwen3-8B-GGUF`) |
| Git commit | **2f3882e** |
| Run ID | **phase10_20260823T140737Z_ab9b33d4** |
| Threshold | **0.55** (`uncertainty.smoke_threshold` — smoke only, not locked benchmark threshold) |
| Expected | Preflight PASS; each case n_evidence=4, uncertainty_result populated, confidence/threshold/decision set, no error |
| Actual (observed) | **PASS** — 3/3; all decisions `ANSWER` (confidence ≥ 0.55 on all cases) |
| Status | **PASS** |
| Error | — |

**Evidence files (authoritative):**

| Role | Path |
| --- | --- |
| PASS status | `results/config/phase10_smoke_test.json` |
| Per-case raw results | `results/config/phase10_multi_agent_uq_smoke.json` |
| Runtime / GPU | `results/config/phase10_runtime_fingerprint.json` |
| JSONL | `results/config/phase10_multi_agent_uq_smoke.jsonl` |
| Drive archive | `MyDrive/MSc-RAG/configs/phase10/` — **NEEDS VERIFICATION** (user copied JSONs locally) |

**Per-case (observed from `phase10_multi_agent_uq_smoke.json`):**

| question_id | n_evidence | top score | confidence | threshold | decision | latency (s) | error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| finqa_test_1000 | 4 | 0.8718 | 0.725 | 0.55 | ANSWER | ~82.0 | none |
| finqa_test_1012 | 4 | 0.7765 | 0.715 | 0.55 | ANSWER | ~22.5 | none |
| finqa_test_1017 | 4 | 0.8166 | 0.813 | 0.55 | ANSWER | ~22.8 | none |

**UQ method (observed):** `mean_retrieval_verification` — confidence = mean(retrieval_score, verification_score).

**Notes:**

- All three smoke cases exceeded smoke threshold → `ANSWER` (abstention gate not triggered on this subset; gate verified structurally and via unit tests with high threshold).
- Smoke threshold **0.55** is **not** the locked benchmark threshold (calibration on dev 40 remains Phase 14).
- Frozen 140 / calibration 40 **not modified**.
- Qwen3 draft verbosity at `max_new_tokens=512` observed (same as Phase 9); not a smoke failure.

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 10 — Multi-Agent RAG + UQ / abstention
