# Phase 11 validation evidence

| Field | Value |
| --- | --- |
| Phase | 11 — Streamlit live artefact |
| Evidence file | `project_record/evidence/phase11_validation.md` |
| Last updated | 2026-08-24 |
| Phase 11 status | **Implementation complete**; Colab T4 live-demo launch **not yet verified**. Latest observed UI was Mac Streamlit (`llama_cpp` + `mps_capable_host` + `127.0.0.1:8501`). |

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Unit/integration (live runner, independence, frozen loader, failure display) | **PASS** | `tests/test_phase11_live_artefact.py` |
| 2 | Full pytest suite | **PASS** | 73 passed (2026-08-24) |
| 3 | Live artefact smoke — frozen + fresh questions | **PASS** | `results/config/phase11_smoke_test.json` |
| 4 | Streamlit HTTP start | **PASS** | `http://127.0.0.1:8501` returned 200 |
| 5 | Live failure display (empty evidence / ProxyError) | **PASS** | `tests/test_phase11_live_artefact.py` |
| 6 | Colab live comparison — T4 `llama_cpp` (fresh question) | **NEEDS VERIFICATION** | `notebooks/colab_phase11_live.ipynb` |
| 7 | Runtime guard (no silent mock; macOS rejected) | **PASS** | `tests/test_runtime_guard.py` |
| 8 | Observed Streamlit live-demo connection (first report) | **FAIL** (Mac mock, not Colab T4) | `backend=mock`, `device=mps_capable_host`, `ProxyError: 403 Forbidden` |
| 9 | Observed Streamlit live-demo launch (second report) | **FAIL** (Mac Streamlit, not Colab T4) | `backend=llama_cpp`, `device=mps_capable_host`, `gpu=null`, latency ~0.01s, URL `127.0.0.1:8501` |

---

## Test records

### 1. Unit/integration tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T22:35:00 |
| Phase | 11 |
| Test name | `test_phase11_live_artefact` |
| Command | `PYTHONPATH=. pytest tests/test_phase11_live_artefact.py -v` |
| Environment | Local Mac; `.venv` |
| Expected | Three independent architectures; same original question; frozen CSV readable; fresh question IDs; schema fields; failed retrieval/generation → ERROR/UNAVAILABLE (not ANSWER) |
| Actual (observed) | **10 passed** |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_phase11_live_artefact.py` |

### 2. Full pytest suite

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T22:35:00 |
| Phase | 11 |
| Test name | full_pytest_suite |
| Command | `PYTHONPATH=. pytest -q` |
| Environment | Local Mac; `.venv` |
| Expected | All V2 tests pass |
| Actual (observed) | **65 passed** |
| Status | **PASS** |
| Error | — |

### 3. Live artefact smoke — frozen + fresh (n=2 comparisons × 3 architectures)

| Field | Value |
| --- | --- |
| Date/time (UTC) | **2026-08-23T22:26:46Z** |
| Phase | 11 |
| Test name | `phase11_live_artefact_smoke` |
| Command | `PYTHONPATH=. python scripts/smoke_live_artefact.py --backend mock` |
| Environment | Local Mac; Phase 6 Chroma KB (preflight PASS 1239/1239); mock LLM |
| Expected | 1 frozen + 1 fresh question; each architecture returns evidence + answer; no chaining |
| Actual (observed) | **PASS** — 2/2 comparisons; 6/6 architecture cases; run_id `phase11_20260823T222633Z_90aab3d6` |
| Status | **PASS** |
| Error | — |
| Output path | `results/config/phase11_live_smoke.json`, `phase11_smoke_test.json` |

**Per comparison (observed):**

| source | question_id | architectures | n_evidence each | decisions |
| --- | --- | --- | --- | --- |
| frozen | finqa_test_1000 | single_agent, multi_agent, multi_agent_uq | 4 | ANSWER / ANSWER / ANSWER |
| fresh | live_fresh_f1cc80e228 | single_agent, multi_agent, multi_agent_uq | 4 | ANSWER / ANSWER / ANSWER |

### 4. Streamlit app start

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T22:27:01Z |
| Phase | 11 |
| Test name | streamlit_http_start |
| Command | `PYTHONPATH=. streamlit run app/streamlit_app.py --server.headless true --server.port 8501` |
| Environment | Local Mac |
| Expected | App serves on localhost |
| Actual (observed) | HTTP **200** at `http://127.0.0.1:8501` |
| Status | **PASS** |
| Error | — |
| Note | Click-through of Run button in a browser was **not** executed in this environment |

### 5. Live failure display (empty evidence / retrieval exception)

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-23T22:35:00 |
| Phase | 11 |
| Test name | empty_evidence_and_proxy_error_not_answer |
| Command | `PYTHONPATH=. pytest tests/test_phase11_live_artefact.py -k "empty_evidence or retrieval_exception or normalize_live" -v` |
| Environment | Local Mac; `.venv`; mock backend |
| Expected | Empty evidence → UNAVAILABLE, no answer, no confidence; ProxyError → ERROR with actual message; never ANSWER |
| Actual (observed) | **3 passed** |
| Status | **PASS** |
| Error | — |

### 6. Colab live comparison — T4 `llama_cpp` (fresh question) — official GPU validation

| Field | Value |
| --- | --- |
| Date/time (UTC) | **NEEDS VERIFICATION** |
| Phase | 11 |
| Test name | `phase11_colab_live_llama_cpp` |
| Command | `notebooks/colab_phase11_live.ipynb` → restore KB → `smoke_live_artefact.py --backend llama_cpp --fresh-only` |
| Environment | Google Colab GPU Tesla T4; `llama_cpp`; Qwen3-8B Q4_K_M (expected — same as Phases 8–10) |
| Expected | One fresh question; three independent architectures; n_evidence>0; non-empty answers or explicit ERROR/UNAVAILABLE; backend `llama_cpp` not mock |
| Actual (observed) | **Not run from this environment** — Colab GPU notebook must be executed manually |
| Status | **NEEDS VERIFICATION** |
| Error | — |

**Runbook (user action required after this launch fix is on GitHub):**

1. Push the launch-fix files to `cursor/empty-v2-workspace` (Colab clones this branch).
2. Open `notebooks/colab_phase11_live.ipynb` on Google Colab with **GPU (T4)**.
3. Run all cells. Section 5 runs frozen `finqa_test_1000` through all three architectures and must print `device=cuda` and a GPU name (not `mps_capable_host`).
4. Section 8 starts Streamlit **inside Colab** and prints Colab `proxyPort` URL + an iframe. Do **not** open `http://127.0.0.1:8501` on the Mac.
5. Copy `phase11_colab_live_demo.json` from Drive/`results/config/` and request an evidence update with observed values.

### 7. Runtime guard unit tests

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-24 |
| Phase | 11 |
| Test name | `test_runtime_guard` |
| Command | `PYTHONPATH=. pytest tests/test_runtime_guard.py tests/test_phase11_live_artefact.py tests/test_phase7_model_backend.py -q` then `PYTHONPATH=. pytest -q` |
| Environment | Local Mac; `V2/.venv` |
| Expected | Guard rejects macOS; factory forces `llama_cpp` when mock is forbidden; factory still allows mock without the env; live runner refuses a MockBackend instance when forbidden |
| Actual (observed) | Guard file tests **23 passed**; full suite **73 passed** (2026-08-24 re-run) |
| Status | **PASS** |
| Error | — |
| Output path | `tests/test_runtime_guard.py` |

### 8. Observed Streamlit live-demo connection (user report) — not a Colab T4 result

| Field | Value |
| --- | --- |
| Date/time | 2026-08-24 (user report) |
| Phase | 11 |
| Test name | `phase11_colab_live_demo_connection` |
| Command / notebook | User-facing Streamlit live demo (reported as still connected to the local host) |
| Environment / device / GPU | **Observed:** `backend=mock`, `device=mps_capable_host` — this fingerprint is the local Mac, not Colab CUDA/T4 |
| Expected | Streamlit inside Colab; `llama_cpp`; Qwen3-8B GGUF; CUDA/T4; non-empty Chroma; tunnel URL; one fresh-question smoke |
| Actual (observed) | **`backend=mock`**, **`device=mps_capable_host`**, **`ProxyError: 403 Forbidden`**. Streamlit was not using the Colab T4/`llama_cpp` runtime. |
| Status | **FAIL** for the Colab T4 live-demo connection. Code fix is in V2 (notebook + `runtime_guard` + factory + Streamlit lock). Re-run on Colab GPU after push is **NEEDS VERIFICATION**. |
| Error | `ProxyError: 403 Forbidden` (reported with the Mac mock/MPS fingerprint) |

### 9. Observed Streamlit live-demo launch (second user report) — still the Mac process

| Field | Value |
| --- | --- |
| Date/time | 2026-08-24 (user report) |
| Phase | 11 |
| Test name | `phase11_colab_live_demo_launch` |
| Command / notebook | Streamlit page the user opened after the first connection fix |
| Environment / device / GPU | **Observed:** `backend=llama_cpp`, `device=mps_capable_host`, `gpu=null`, latency ~0.01s, URL `127.0.0.1:8501` |
| Expected | Streamlit process on Colab T4; Colab `proxyPort` URL; displayed device `cuda` and the actual GPU name |
| Actual (observed) | Browser reached the **local Mac** Streamlit server. `llama_cpp` was selected on the Mac, so backend looked correct, but device/GPU/latency/URL prove it was not Colab. |
| Status | **FAIL** for the Colab live-demo launch. Notebook now uses Colab `proxyPort` + iframe; Streamlit refuses `llama_cpp` on Darwin; selecting localhost is called out as wrong. Re-run on Colab GPU after push is **NEEDS VERIFICATION**. |
| Error | — |

**Notes:**

- Shared existing Phase 6 KB; no rebuild.
- Frozen 140 / calibration 40 **not modified** (id SHA-256 unchanged).
- V1 **not modified**.
- Benchmark was **not** started.
- Mock is now forbidden when `V2_FORBID_MOCK=1` or `V2_LIVE_BACKEND=llama_cpp`. The live-demo notebook sets both and refuses Darwin/`mps_capable_host`.
- Live layer (`normalize_live_case`) maps failed retrieval/generation to ERROR/UNAVAILABLE, clears fabricated answers and confidence. Phase 8–10 pipeline modules unchanged.
- A Colab T4 `llama_cpp` live URL + `finqa_test_1000` result has **not** been observed from this Mac environment. Do not treat `127.0.0.1:8501` / `mps_capable_host` as GPU validation.
- Tunnel method is now Colab `google.colab.kernel.proxyPort(8501)` + iframe (no cloudflared).

---

## Master record reference

`PROJECT_MASTER_RECORD.md` → Phase 11 — Streamlit live artefact
