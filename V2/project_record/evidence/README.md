# Phase validation evidence

Persistent validation/evidence reports for every major V2 phase.

## Rules

1. Run relevant tests/smoke/benchmark steps for the phase.
2. Save **actual** output to this directory (and machine-readable JSON under `results/` where useful).
3. Record date/time, phase, test name, command/notebook, environment, expected, **actual**, PASS/FAIL, errors, output paths.
4. Update `PROJECT_MASTER_RECORD.md` with a concise reference to this file.
5. **Do not fabricate PASS.** Record FAIL with the actual error.
6. Do not mark a phase complete until approved completion criteria are met.

## Layout

```text
project_record/evidence/
├── README.md
├── _TEMPLATE.md
├── artifacts/          # pytest captures, small logs (not raw benchmark dumps)
├── phase1_validation.md
├── phase2_validation.md
...
```

For large benchmark runs: keep raw outputs in `results/raw/` and `checkpoints/`; evidence files are **concise summaries** pointing to those paths.

Machine-readable smoke/validation JSON: `results/config/phaseN_*_test.json`

Phase 16 evaluation summary: `results/config/phase16_evaluation_summary.json` (CPU scoring of saved Phase 15 cases; no RAG/Qwen).

## Capture commands

```bash
# Full pytest evidence (from V2/ with venv active)
PYTHONPATH=. python scripts/capture_pytest_evidence.py --phase N

# Phase 7 LLM smoke (writes results/config/phase7_smoke_test.json)
PYTHONPATH=. python scripts/smoke_generate.py --backend ollama_dev
```
