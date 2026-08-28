# Phase 16 validation evidence

| Field | Value |
| --- | --- |
| Phase | 16 — Evaluation + metrics + post-hoc LLM-as-judge |
| Evidence file | `project_record/evidence/phase16_validation.md` |
| Last updated | 2026-08-28 |
| Phase 16 status | CPU **PASS** (2026-08-26). Official Colab 420-case LLM-as-judge **PASS** (locally verified 2026-08-28). Phase 17 not started. |

Earlier (2026-08-27) this file recorded official Colab 420 as **not launched** / **NEEDS VERIFICATION**. That was the implementation state. It is superseded by the verified run below. CPU metric numbers in §3–4 are unchanged.

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Phase 16 unit tests | **PASS** | `tests/test_phase16_evaluation.py` |
| 2 | Full pytest suite | **PASS** | 124 passed (2026-08-27) |
| 3 | CPU evaluation of 420 saved cases | **PASS** | `results/config/phase16_smoke_test.json` |
| 4 | Completeness / no new generation | **PASS** | raw SHA unchanged; 420 unique keys |
| 5 | LLM-as-judge unit tests + mock n=3 | **PASS** | `tests/test_phase16_judge.py` |
| 6 | Official 420-case Colab judge | **PASS** (verified 2026-08-28) | `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl` |
| 7 | Phase 17 statistics | **not started** | — |

Locked T=0.65 unchanged. Frozen 140/40 CSVs unchanged (SHA recorded). V1 unmodified. No architecture runners imported.

---

## Test records

### 1. Unit tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T23:51:41Z |
| Phase | 16 |
| Test name | `test_phase16_evaluation` |
| Command | `PYTHONPATH=. pytest tests/test_phase16_evaluation.py tests/test_config_loads.py tests/test_phase13_calibration.py -q` |
| Environment | Local Mac; `V2/.venv`; CPU |
| Expected | Numeric/context metrics; evaluation modules do not import RAG/LLM; canonical JSONL SHA stable |
| Actual (observed) | **18 passed** (5 Phase 16 + config + Phase 13) |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase16_evaluation.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T23:51Z |
| Phase | 16 |
| Test name | full suite |
| Command | `PYTHONPATH=. pytest -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | Existing phases still pass after evaluation code is added |
| Actual (observed) | **116 passed** |
| Status | **PASS** |
| Error | — |
| Output path | — |

### 3. CPU evaluation (420 saved cases)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-26T23:51:41Z |
| Phase | 16 |
| Test name | `phase16_evaluation` |
| Command | `PYTHONPATH=. python scripts/run_evaluation.py` |
| Environment | Local Mac CPU; `used_llm_inference=false`; `used_gpu=false`; `used_rag_rerun=false` |
| Expected | Score all 420 Phase 15 cases; no RAG/Qwen; T=0.65 unchanged |
| Actual (observed) | `status=PASS n_cases=420 used_llm=False raw_unchanged=True`; run_id `phase16_20260826T235141Z_73fdbf58` |
| Status | **PASS** |
| Error | — |
| Output path | `results/processed/phase16_cases.jsonl`; `results/metrics/phase16_summary.csv` |

Source raw SHA-256 (before and after): `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa`.

Frozen 140 SHA-256: `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087`  
Calibration 40 SHA-256: `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845`  
`threshold.lock.json` SHA-256: `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88` (T=0.65, `used_frozen_test_140=false`)

Processed JSONL: **420** lines; **140** per architecture; **4** evidence chunks each (count only; chunk text not copied); all rows `used_llm_inference=false` / `used_gpu=false`; `run_id` remains `phase15_20260826T203744Z_dae9c3a4`.

### 4. Observed metrics (not official RAGAS)

CPU numeric match to FinQA `program_answer` (rel_tol=0.01). Faithfulness = token-overlap of the model claim vs retrieved text. Context P/R = gold `file_name` / `context_id` match. Retrieval is identical across architectures, so context P/R are identical.

| Architecture | n | ANSWER | ABSTAIN | Displayed correct | Claim correct | Selective acc. | Faithfulness | Context P | Context R | Unsupported emitted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `single_agent` | 140 | 140 | 0 | 32 (0.2286) | 32 (0.2286) | 0.2286 | 0.5619 | 0.4304 | 0.9000 | 0.7714 |
| `multi_agent` | 140 | 140 | 0 | 29 (0.2071) | 29 (0.2071) | 0.2071 | 0.5553 | 0.4304 | 0.9000 | 0.7929 |
| `multi_agent_uq` | 140 | 78 | 62 | 32 (0.2286) | 34 (0.2429) | 0.4103 | 0.5539 | 0.4304 | 0.9000 | 0.3286 |

Additional observed values:

| Item | `single_agent` | `multi_agent` | `multi_agent_uq` |
| --- | ---: | ---: | ---: |
| Coverage | 1.0 | 1.0 | 0.5571 |
| Abstention rate | 0.0 | 0.0 | 0.4429 |
| Context recall (numeric in evidence) | 0.1286 | 0.1286 | 0.1286 |
| Stored verification score (mean) | — | 0.5417 | 0.5587 |
| Mean confidence | — | 0.5417 | 0.6440 |
| Mean latency (s, from Phase 15) | 20.29 | 22.85 | 22.86 |

UQ detail: 32 ANSWER correct, 46 ANSWER incorrect, 2 ABSTAIN with a numerically correct **draft**. Displayed UQ correctness counts the abstention template as incorrect.

**Honest reading (no significance tests — Phase 17 not run):**

- Displayed answer correctness is **not** higher for Multi-Agent (29/140) than Single-Agent (32/140).
- UQ displayed correctness (32/140) equals Single-Agent because ABSTAIN text does not match the gold number. Claim correctness is 34/140.
- UQ selective accuracy is 32/78 ≈ 0.4103 at coverage 78/140 ≈ 0.5571.
- `unsupported_emitted_rate` is lower for UQ (46/140) because 62 cases abstain. This is “answered and numerically wrong”, not a labelled hallucination.
- Context precision 0.4304 and recall 0.9000 are the same for all three architectures (shared retrieval).
- Faithfulness values are a CPU token-overlap proxy, **not** RAGAS LLM-as-judge.

Source tables: `results/metrics/phase16_summary.csv`, `results/metrics/phase16_by_architecture.json`.

---

## Constraints checked

| Constraint | Observed |
| --- | --- |
| Phase 15 JSONL is the sole generation input | SHA matched expected canonical hash; not rewritten |
| No RAG / Qwen rerun | `used_rag_rerun=false`; evaluation import graph excludes architecture runners and `llama_cpp` |
| Frozen 140 unmodified | SHA unchanged during scoring |
| Calibration 40 unmodified | SHA unchanged during scoring |
| T not retuned | lock still 0.65; SHA unchanged |
| All 420 cases scored | 420 unique keys; 0 missing; 0 extra; 0 errors |
| V1 unmodified | no V1 paths edited |
| Phase 17 not started | no statistical tests |

### 5. LLM-as-judge implementation (2026-08-27)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-27 |
| Phase | 16 |
| Test name | `test_phase16_judge` + mock n=3 |
| Command | `PYTHONPATH=. pytest tests/test_phase16_judge.py -q` |
| Environment | Local Mac CPU; mock backend; no Colab GPU |
| Expected | UQ uses draft; prompt omits gold; mock n=3 resume; Phase 15 SHA stable; CPU JSONL unchanged; official mock-420 refused |
| Actual (observed) | **8 passed** in `test_phase16_judge.py`; mock n=3 resume skipped 3; Phase 15 SHA unchanged; CPU JSONL unchanged; official mock-420 refused. Full suite **124 passed**. |
| Status | **PASS** (implementation + mock). Official 420 was **not launched** on this date |
| Error | — |
| Output path | `notebooks/colab_phase16_judge.ipynb`; `scripts/run_judge.py` |

Metric label: `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)`. Not official RAGAS. Token-overlap kept as secondary. Phase 16 CPU tables not rewritten.

### 6. Official 420-case Colab judge (verified 2026-08-28)

Historical (2026-08-27): this row was **not launched** / **NEEDS VERIFICATION**. Notebook and runner existed; the GPU job had not been run.

| Field | Value |
| --- | --- |
| Date/time (UTC) | Colab ended 2026-08-28T15:39:49Z; local JSONL inspect 2026-08-28 |
| Phase | 16 |
| Test name | `phase16_judge_faithfulness` (official 420) |
| Command / notebook | `notebooks/colab_phase16_judge.ipynb`; `PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp` |
| Environment | Colab GPU; Tesla T4; `llama_cpp`; Qwen3-8B Q4_K_M; git `e4a6b375cea16a9628a6e0db63b03ca56fa33660` |
| Expected | 420 post-hoc judge cases on frozen Phase 15 JSONL; SHA `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa`; no RAG rerun; no gold context/answer |
| Actual (observed) | **PASS**; run_id `phase16_judge_20260828T152623Z_06661255`; 420/420 unique keys; 140 per architecture; 0 duplicates; 0 missing; 0 errors; 0 parse failures; all `COMPLETED`; `used_rag_rerun=false`; UQ claim_source `draft_answer` (140); UQ 78 ANSWER / 62 ABSTAIN |
| Status | **PASS** |
| Error | — |
| Output path | `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl` |

Metric label (exact): **LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)**. **Not official RAGAS.** Not the RAGAS library. CPU token-overlap remains secondary. Numeric answer correctness and context P/R stay CPU-only and were **not** rewritten.

Observed mean scores from the official JSONL (rounded to 4 d.p.; source `results/metrics/phase16_judge_summary.csv`):

| Architecture | n | LLM faithfulness (all) | LLM faithfulness (ANSWER only) |
| --- | ---: | ---: | ---: |
| `single_agent` | 140 | 0.3241 | 0.3241 |
| `multi_agent` | 140 | 0.3484 | 0.3484 |
| `multi_agent_uq` | 140 | 0.3749 | **0.6548** (78 ANSWER) |

`judge.jsonl` SHA-256: `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3`. Phase 15 source SHA unchanged. T=0.65 lock SHA unchanged. Frozen 140/40 SHA unchanged.

**Judge-call settings (JSONL is source of truth):** every official row records `temperature=0.0`, `max_new_tokens=32`, `n_ctx=4096`. Do **not** treat `results/config/phase16_judge_runtime_fingerprint.json` `model_config` values (`temperature=0.1`, `max_new_tokens=512`) as the judge-call settings; those are experiment.yaml defaults captured in the fingerprint, not the post-hoc judge job.

Machine-readable: `results/config/phase16_judge_summary.json`, `results/config/phase16_judge_smoke_test.json`. Log: `results/logs/phase16_judge_20260828T152554Z.log` (420 COMPLETED + `status=PASS completed=420 failed=0 pending=0`).

---

## Master record reference

> Validation evidence: `project_record/evidence/phase16_validation.md`
