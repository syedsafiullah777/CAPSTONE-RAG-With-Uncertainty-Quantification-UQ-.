# Phase 21 validation evidence — canonical final live-demo launcher

| Field | Value |
| --- | --- |
| Phase | 21 |
| Phase name | Canonical Colab final live-demo launcher (not a research experiment) |
| Evidence file | `project_record/evidence/phase21_validation.md` |
| Last updated | 2026-08-29 |

**No GPU run during notebook creation.** Official Colab T4 viva launch remains **NEEDS VERIFICATION** until the notebook is executed on Colab.

## Summary

| # | Test name | Status | Evidence path |
| --- | --- | --- | --- |
| 1 | Notebook JSON valid; Streamlit entrypoint; GPU guard; no mock/Ollama fallback; no benchmark scripts invoked | **PASS** | `tests/test_phase21_final_live_demo.py` (3 passed) |
| 2 | Frozen 140/40, lock T=0.65, Phase 15/16 hashes | **PASS** (unchanged; not rewritten) | Phase 19 pins |
| 3 | Official Colab T4 viva launch | **NEEDS VERIFICATION** | `notebooks/colab_phase21_final_live_demo.ipynb` |

## Test records

### 1. Static notebook checks

| Field | Value |
| --- | --- |
| Date/time (UTC) | 2026-08-29 |
| Command | `PYTHONPATH=. pytest tests/test_phase21_final_live_demo.py -v` |
| Environment | Local Mac; `.venv`; no GPU job |
| Expected | Valid ipynb; `streamlit run app/streamlit_app.py`; `proxyPort(8501)`; `verify_live_llama_cpp_runtime`; Tesla T4; T=0.65 LOCKED; no `python scripts/run_*` benchmark/calibration/judge/stats/live_demo/build_index |
| Actual (observed) | **3 passed** |
| Status | **PASS** |

### 2. Research artefacts

Notebook creation did not write Phase 15 JSONL, judge JSONL, metrics, lock file, or frozen CSVs.

## Master record reference

Validation evidence: `project_record/evidence/phase21_validation.md`
