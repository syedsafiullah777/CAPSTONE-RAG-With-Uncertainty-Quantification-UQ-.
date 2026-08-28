# Phase 17 figures — dissertation use

Canonical set of **six** figures in `results/metrics/phase17_figures/`. Index: `results/metrics/phase17_figures/FIGURE_INDEX.md`.

Presentation only. **No RAG rerun. No Qwen generation. No LLM-as-judge calls. No recomputation of statistical tests.**

Entrypoint: `PYTHONPATH=. python scripts/render_phase17_figures.py`

Each figure has exactly two files: **PNG** (300 dpi) and **PDF** (vector). No SVG.

Architecture labels: **Single-Agent**, **Multi-Agent**, **Multi-Agent + UQ**.

Faithfulness wording: `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS**.

Locked threshold: **T = 0.65** from the separate 40-question FinQA DEV calibration set (not the frozen 140).

---

## Primary figures (dissertation main body)

| Figure | Filename stem | What it shows | Source |
| --- | --- | --- | --- |
| **Figure 1** | `rq1_answer_correctness_95ci` | Displayed numeric correctness (%) with Wilson 95% CI; n=140. 32/140 = 22.86%; 29/140 = 20.71%; 32/140 = 22.86%. Does **not** mark statistical significance. | `results/metrics/phase17_descriptive.csv` |
| **Figure 2** | `rq2_confidence_vs_faithfulness` | UQ confidence vs LLM-as-judge faithfulness, 140 UQ cases; ANSWER vs ABSTAIN; locked T=0.65; Spearman ρ = 0.6988 and Holm p. | `results/metrics/phase17_tests.csv`; `phase16_cases.jsonl` + official judge JSONL |
| **Figure 3** | `rq3_coverage_vs_selective_accuracy` | Coverage vs selective accuracy at locked T=0.65. UQ 78/140 = 55.71% coverage; 32/78 = 41.03% selective accuracy. | `results/metrics/phase17_descriptive.csv` |

## Supporting figures (dissertation appendix)

| Figure | Filename stem | What it shows | Source |
| --- | --- | --- | --- |
| Appendix RQ1 | `rq1_mcnemar_counts` | McNemar cells: 19 / 13 / 10 / 98 | `results/metrics/phase17_tests.csv` |
| Appendix RQ2 | `rq2_faithfulness_distribution` | Faithfulness distribution by architecture, n=140 | Official judge JSONL + `phase16_cases.jsonl` |
| Appendix RQ3 | `rq3_uq_outcomes` | UQ outcomes at T=0.65: 32 / 46 / 60 / 2 | `results/config/phase17_statistics_summary.json` |

## What was not changed

Phase 17 statistical tables, p-values, CIs, effect sizes, T=0.65, frozen 140/40, Phase 15/16 JSONL, RAG code, and V1.

Phase 18 is **not started**.
