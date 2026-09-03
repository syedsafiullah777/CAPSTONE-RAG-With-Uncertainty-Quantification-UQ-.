# Phase 18 — Qualitative error analysis

CPU-only inspection of the frozen 420-case benchmark. **No RAG rerun. No Qwen generation. No LLM-as-judge calls. No change to T=0.65 or the frozen 140/40.**

Entrypoint: `PYTHONPATH=. python scripts/run_error_analysis.py`

Outputs:

- `results/analysis/phase18_error_cases.csv` (all 420 cases + sample flag)
- `results/analysis/phase18_error_summary.csv` (category × architecture on the full 420)
- `results/final/phase18_error_analysis.md`
- Evidence: `project_record/evidence/phase18_validation.md`

## Sampling

`random.Random(18)`. Stratified by architecture, correctness, UQ ANSWER/ABSTAIN, false abstention (census of both cases), retrieval miss, gold-number-in-evidence errors, high-confidence Multi-Agent verification errors, and low/near-threshold UQ abstentions.

A case may appear in more than one stratum. Percentages in the summary use **all 420** rule-based labels, not the sample.

## Rules

Numeric incorrectness is not called hallucination.  
`LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` is **not official RAGAS**.  
Faithfulness &lt; 0.5 is a taxonomy split only, not a new operating threshold.

At the time of this earlier entry, Phase 20 had not yet started. Phase 20 (live artefact) and Phase 21 (live-demo launcher) were completed subsequently; they do not rerun this error analysis.
