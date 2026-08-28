# Phase 20 validation evidence — final live artefact

| Field | Value |
| --- | --- |
| Phase | 20 |
| Phase name | Final live-artefact and reproducibility validation |
| Evidence file | `project_record/evidence/phase20_live_artefact_validation.md` |
| Last updated | 2026-08-28 |

**Do not treat local mock answers or Mac Streamlit as the official Colab T4 / Qwen3-8B demonstration.** Official GPU live answers remain **NEEDS VERIFICATION**.

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Unit tests (`test_phase20_live_artefact.py`) | **PASS** | 7 passed |
| 2 | Full pytest excluding `analyse()` | **PASS** | **144 passed**, 1 deselected |
| 3 | Frozen 140 / cal 40 / lock / Phase 15–16 hashes | **PASS** | SHA-256 match Phase 19 pins |
| 4 | Live code does not look up Phase 15 JSONL | **PASS** | `live.py` / `streamlit_app.py` AST + string checks |
| 5 | Streamlit UI source exposes required fields | **PASS** | `app/streamlit_app.py` |
| 6 | Streamlit HTTP start (local Mac) | **PASS** | `http://127.0.0.1:8502/` → 200 |
| 7 | Local mock live demo — three questions × three architectures | **PASS** (plumbing only) | `results/config/phase20_live_demo_summary.json` |
| 8 | Insufficient-evidence UQ ABSTAIN at locked T=0.65 (mock) | **PASS** (mock) | confidence 0.5351 < 0.65 |
| 9 | Documented launch command | **PASS** | `PYTHONPATH=. streamlit run app/streamlit_app.py` |
| 10 | No secrets in live artefact source | **PASS** | no API keys / tokens in `app/` + `src/rag/live.py` |
| 11 | Official Colab T4 + Qwen3-8B + `llama_cpp` live demo | **NEEDS VERIFICATION** | `notebooks/colab_phase11_live.ipynb` |
| 12 | Known-good FinQA Qwen answer at T=0.65 on T4 | **NEEDS VERIFICATION** | mock UQ also ABSTAINED (0.6185) — not Qwen |
| 13 | Fresh KB Qwen answer on T4 | **NEEDS VERIFICATION** | mock UQ ABSTAINED (0.6212) — not Qwen |
| 14 | Colab Streamlit UI click-through (proxy, not 127.0.0.1) | **NEEDS VERIFICATION** | this Mac cannot open Colab GPU |
| 15 | Frozen 140 catalogue page (read-only load, unique IDs, pagination, no Phase 15 lookup) | **PASS** | `src/rag/benchmark_catalogue.py`; SHA-256 unchanged |

---

## Test records

### 1. Unit tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 20 |
| Test name | `test_phase20_live_artefact` |
| Command | `PYTHONPATH=. pytest tests/test_phase20_live_artefact.py` |
| Environment | Local Mac; `.venv`; Python 3.13.4 |
| Expected | Locked T=0.65 even if `threshold=0.55` passed; no Phase 15 lookup; Streamlit has no smoke `number_input`; frozen hashes unchanged after a live comparison |
| Actual (observed) | **7 passed** in 0.83s |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase20_live_artefact.py` |

### 2. Full pytest suite (excluding `analyse()`)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 20 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -q -k "not test_analyse_paired_140"` |
| Environment | Local Mac; `.venv` |
| Expected | Existing suite plus Phase 20 tests pass; `analyse()` not re-run |
| Actual (observed) | **144 passed**, 1 deselected |
| Status | **PASS** |
| Error | — |

### 3. Frozen artefacts unchanged

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 20 |
| Test name | frozen_hash_pins |
| Command | `sha256_file` vs Phase 19 pins in `src/statistics/constants.py` |
| Environment | Local Mac |
| Expected | Six scientific artefacts unchanged |
| Actual (observed) | All six **PASS** (see table below) |
| Status | **PASS** |
| Error | — |

| Artefact | SHA-256 |
| --- | --- |
| `data/final/selected_140_questions.csv` | `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087` |
| `data/calibration/calibration_questions.csv` | `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845` |
| `results/config/threshold.lock.json` | `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88` |
| Phase 15 `cases.jsonl` | `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` |
| Phase 16 processed JSONL | `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91` |
| Phase 16 judge JSONL | `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3` |

Lock file still records **T = 0.65**. Phase 15/16/17/18 result files were not rewritten.

### 4. Live pipelines are not Phase 15 lookup

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 20 |
| Test name | no_precomputed_benchmark_lookup |
| Command | `test_live_and_streamlit_do_not_lookup_phase15` + mock demo flag |
| Expected | `run_live_comparison()` calls Phase 8–10 modules; `used_precomputed_benchmark_lookup=false` |
| Actual (observed) | Source forbids `phase15_benchmark` / judge JSONL paths; demo JSON records `used_precomputed_benchmark_lookup: false` for all three questions |
| Status | **PASS** |
| Error | — |

### 5. UI fields (source inspection)

Observed in `app/streamlit_app.py` (not a Colab browser click-through):

| UI requirement | Present? |
| --- | --- |
| Retrieved evidence, scores, metadata | Yes (`Retrieved evidence / scores / metadata`) |
| Generated answer | Yes |
| Multi-Agent verification | Yes (`Verification` + status / scores) |
| UQ confidence | Yes (`Confidence` + `Uncertainty`) |
| Locked threshold T=0.65 | Yes (sidebar read-only `Locked threshold T = {locked_t:.2f}`; display `0.6500 (locked)`) |
| ANSWER / ABSTAIN | Yes |
| Runtime / backend / GPU | Yes (`backend`, `device`, `gpu`) |
| ERROR / UNAVAILABLE without fabricated answers | Yes (`No answer (run failed). Nothing was fabricated.`) |
| Smoke T=0.55 `number_input` | **Removed** |

### 6. Streamlit HTTP start (local)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 20 |
| Test name | streamlit_http_start |
| Command | `PYTHONPATH=. streamlit run app/streamlit_app.py --server.headless true --server.port 8502` then `curl http://127.0.0.1:8502/` |
| Environment | Local Mac (not Colab T4) |
| Expected | HTTP 200; app process starts |
| Actual (observed) | HTTP **200**; HTML length 11141; Streamlit shell present. Browser click-through of Run was **not** executed (SPA). Process stopped after the check. |
| Status | **PASS** (launch plumbing) |
| Error | — |
| Notes | Do **not** treat `127.0.0.1` as the examiner GPU demo. Official demo is the Colab notebook proxy. |

### 7–8. Local mock live demo (plumbing; real Phase 6 KB)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28T18:06:58Z |
| Phase | 20 |
| Test name | `phase20_live_artefact` mock demo |
| Command | `PYTHONPATH=. python scripts/run_live_demo.py --backend mock` |
| Environment | Darwin arm64; device `mps_capable_host`; GPU none; `llama_cpp` package **null**; backend **mock**; KB preflight **1239 chunks PASS** |
| Expected | Three independent architectures on each of: known-good frozen, fresh KB, insufficient-evidence; locked T=0.65; no 420 rerun |
| Actual (observed) | Run ID `phase20_20260828T180650Z_36ed9b1a`. `n_comparisons=3`. `independent_same_question=true` for all three. Displayed threshold `0.6500 (locked)`. Hashes unchanged. Official status in JSON: **NEEDS_VERIFICATION** because backend is mock. |
| Status | **PASS** for plumbing; **NEEDS VERIFICATION** for Qwen/T4 answers |
| Output path | `results/config/phase20_live_demo_summary.json`, `results/config/phase20_smoke_test.json` |

**Observed mock decisions (not Qwen):**

| Label | question_id | UQ decision | UQ confidence | SA / MA | n_evidence each |
| --- | --- | --- | --- | --- | --- |
| known_good | `finqa_test_1000` | **ABSTAIN** | 0.6185 | ANSWER / ANSWER | 4 |
| fresh_kb | `live_fresh_aa4c046eaf` | **ABSTAIN** | 0.6212 | ANSWER / ANSWER | 4 |
| insufficient | `live_insufficient_evidence` | **ABSTAIN** | 0.5351 | ANSWER / ANSWER | 4 |

Insufficient-evidence question (SpaceX FY2025 GAAP net income / Starship launches) produced a **genuine UQ ABSTAIN** under the locked rule (`confidence < T=0.65`). Single-Agent and Multi-Agent still **ANSWER** (they have no abstention gate) — that is the designed architecture difference, not a forced UQ label.

Mock known-good and fresh questions also fell just below 0.65. That is **mock calibration**, not the official Qwen live result. Phase 11 Colab historically reported UQ confidence **0.7688** at smoke T=0.55 (ANSWER) for `finqa_test_1000`; that Qwen figure was **not** re-measured at T=0.65 in this phase.

### 9. Launch command and documentation

Documented in `README.md`, `docs/phase20_live_artefact.md`, `PROJECT_CONTEXT.md`, and `config/experiment.yaml` → `storage.live_artefact.app_entrypoint`:

```bash
cd V2
PYTHONPATH=. streamlit run app/streamlit_app.py
```

Official GPU path: `notebooks/colab_phase11_live.ipynb` (same app; locked T=0.65; no new benchmark notebook).

### 10. Secrets

Grep of `app/streamlit_app.py` and `src/rag/live.py`: no API keys, `.env` secrets, or Hugging Face tokens. Live artefact does not require a paid inference API.

### 11–14. Official Colab T4 live validation

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 20 |
| Test name | colab_t4_qwen3_llama_cpp_live |
| Command / notebook | `notebooks/colab_phase11_live.ipynb` on GPU Runtime |
| Environment | **Not executed from this Mac.** Colab CLI / gcloud are not used. |
| Expected | Tesla T4; `llama_cpp`; Qwen3-8B Q4_K_M; shared Phase 6 KB; four live checks at T=0.65 |
| Actual (observed) | No Colab T4 fingerprint from this Phase 20 session. `phase20_live_demo_summary.json` records `official_colab_t4_llama_cpp: false`, `backend: mock`. |
| Status | **NEEDS VERIFICATION** |
| Error | — |
| Notes | User must run the existing Phase 11 live notebook on a GPU runtime, restore the Phase 6 KB, execute the Phase 20 question cell, and open Streamlit via the Colab proxy — not `127.0.0.1` on the Mac. |

### 15. Frozen 140 Benchmark Questions page

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-28 |
| Phase | 20 (UI enhancement; not a new phase) |
| Test name | `test_frozen_catalogue_loads_140_unique_matching_csv` |
| Command | `PYTHONPATH=. pytest tests/test_phase20_live_artefact.py` |
| Environment | Local Mac; `.venv` |
| Expected | 140 unique IDs matching `selected_140_questions.csv`; no duplicates; pagination 21–40 of 140; live prefill copies question text only; CSV SHA-256 unchanged; no Phase 15 lookup |
| Actual (observed) | **PASS** — n=140, unique_ids=140, IDs match CSV order, page 2 = 21–40 of 140, page 7 = 121–140. Frozen SHA-256 unchanged for 140/40/lock/Phase 15/16. Full suite **144 passed**, 1 deselected. |
| Status | **PASS** |
| Error | — |
| Output path | `src/rag/benchmark_catalogue.py`, `app/benchmark_ui.py` |

---

## Master record reference

Validation evidence: `project_record/evidence/phase20_live_artefact_validation.md`  
Machine-readable: `results/config/phase20_live_demo_summary.json`
