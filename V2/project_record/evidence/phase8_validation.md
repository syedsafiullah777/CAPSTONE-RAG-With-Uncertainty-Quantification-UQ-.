# Phase 8 validation evidence

| Field | Value |
| --- | --- |
| Phase | 8 — Single-Agent RAG baseline |
| Evidence file | `project_record/evidence/phase8_validation.md` |
| Last updated | 2026-08-23 |
| Phase 8 status | **Complete** (local + Colab verified) |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Unit/integration (schema, prompts, mock pipeline) | **PASS** | `tests/test_phase8_single_agent.py` |
| 2 | Full pytest suite | **PASS** | 43 passed (2026-08-23) |
| 3 | Live single-agent smoke — local Mac (3 frozen questions) | **PASS** | local run 2026-08-22 (`ollama_dev`) |
| 4 | Index preflight validation | **PASS** | `scripts/validate_kb_index.py` |
| 5 | Colab Single-Agent RAG smoke — T4 `llama_cpp` (n=3) | **PASS** | `results/config/phase8_smoke_test.json` |

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
| Test name | `phase8_single_agent_smoke` (local) |
| Command | `PYTHONPATH=. python scripts/smoke_single_agent.py --backend ollama_dev --limit 3` |
| Environment | Local Mac; Phase 6 Chroma KB; Ollama `qwen3:8b` (`think=False`) |
| Expected | Each case: non-empty retrieved_evidence (top_k=4), non-empty answer, no error |
| Actual (observed) | **PASS** — 3/3; run_id `phase8_20260822T164524Z_bd962134` |
| Status | **PASS** |
| Error | — |
| Note | Superseded for official GPU path by Colab run below; retained as local dev evidence |

### 4. Index preflight validation

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23 |
| Phase | 8 |
| Test name | `validate_kb_index` + `test_index_preflight` |
| Command | `PYTHONPATH=. python scripts/validate_kb_index.py`; `pytest tests/test_index_preflight.py -v` |
| Environment | Local Mac; existing Phase 6 Chroma index |
| Expected | Manifest `chunks` matches `collection.count()`; empty-index fixture fails with actionable error |
| Actual (observed) | Preflight **PASS** — expected=1239, actual=1239; unit tests **3 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `src/retrieval/preflight.py`, `scripts/validate_kb_index.py` |

### 5. Colab Single-Agent RAG smoke — T4 `llama_cpp` (n=3) — **official GPU validation**

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-23T12:42:22Z** |
| Phase | 8 |
| Test name | `phase8_colab_single_agent_smoke` |
| Command | `notebooks/colab_phase8_smoke.ipynb` → `build_index.py --distractors 50` → preflight → `smoke_single_agent.py --backend llama_cpp --limit 3` |
| Environment | Google Colab GPU **Tesla T4**; CUDA; Python 3.13.15; `llama_cpp` 0.3.35 |
| Model | **Qwen3-8B** Q4_K_M (`bartowski/Qwen_Qwen3-8B-GGUF`) |
| Git commit | **846c143** |
| Run ID | **phase8_20260823T124009Z_70a29b9f** |
| Expected | Index rebuild 1239 chunks; preflight PASS; each case n_evidence=4, non-empty answer, no error |
| Actual (observed) | **PASS** — 3/3 questions; 4 evidence chunks each; retrieval + generation succeeded |
| Status | **PASS** |
| Error | — |

**Evidence files (authoritative):**

| Role | Path |
| --- | --- |
| PASS status | `results/config/phase8_smoke_test.json` |
| Per-case raw results | `results/config/phase8_single_agent_smoke.json` |
| Runtime / GPU | `results/config/phase8_runtime_fingerprint.json` |
| Colab KB manifest | `knowledge_base/index/index_manifest.json` on Colab/Drive (rebuilt session) — **not** `results/config/phase6_index_manifest.json` (stale Mac copy) |

**KB rebuild (Colab Option B):**

- Index path at smoke time: `/content/capstone-rag/V2/knowledge_base/index`
- 230 docs / 1239 chunks (same schema as Phase 6 Mac build)
- Preflight passed before smoke

**Per-case (observed from `phase8_single_agent_smoke.json`):**

| question_id | n_evidence | top score | latency (s) | error |
| --- | --- | --- | --- | --- |
| finqa_test_1000 | 4 | 0.8718 | ~79.8 | none |
| finqa_test_1012 | 4 | 0.7765 | ~20.2 | none |
| finqa_test_1017 | 4 | 0.8166 | ~21.0 | none |

**Notes:**

- Frozen 140 / calibration 40 **not modified**.
- Retrieval config unchanged (top_k=4, `finqa_source_pdfs`, BGE).
- Diagnosis of prior Colab failure: `project_record/evidence/phase8_colab_retrieval_diagnosis.md`

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 8 — Single-Agent RAG baseline
