# Phase 19 — Final reproducibility and research-integrity audit

Read-only audit of the frozen research chain. **No RAG rerun. No Qwen generation. No LLM-as-judge calls. No calibration. No statistical recomputation. No change to T=0.65 or the frozen 140/40.**

Entrypoint: `PYTHONPATH=. python scripts/run_reproducibility_audit.py`

Outputs:

- `project_record/evidence/phase19_reproducibility_audit.md`
- `results/final/phase19_artefact_manifest.md`
- `results/config/phase19_audit.json`

Phase 20 (dissertation evidence pack) is **not started**.

Correction (2026-08-28): numbered Phase 20 was implemented as **live-artefact validation**, not a dissertation pack. See `docs/phase20_live_artefact.md`. No Phase 21 started.
