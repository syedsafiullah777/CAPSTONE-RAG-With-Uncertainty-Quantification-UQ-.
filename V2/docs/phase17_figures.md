# Phase 17 figures — dissertation use

Presentation-only redraw of the Phase 17 figures. **No RAG rerun. No Qwen generation. No LLM-as-judge calls. No recomputation of statistical tests, p-values, confidence intervals, or effect sizes.**

Entrypoint: `PYTHONPATH=. python scripts/render_phase17_figures.py`

Renderer: `src/statistics/figures.py` (reads saved tables + JSONL; SHA-gates frozen artefacts)

Evidence: `project_record/evidence/phase17_validation.md`  
Render log: `results/config/phase17_figure_render.json`

Architecture labels (locked): **Single-Agent**, **Multi-Agent**, **Multi-Agent + UQ**.

Faithfulness axis/legend wording (locked): `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS**.

Locked threshold: **T = 0.65** from the separate 40-question FinQA DEV calibration set (not the frozen 140).

---

## Primary figures (dissertation main body)

| Figure | File stem | RQ | What it shows | Source result files |
| --- | --- | --- | --- | --- |
| **Figure 1** | `rq1_accuracy_wilson_ci` | RQ1 | Displayed numeric correctness (%) for the three architectures, Wilson 95% CI, n=140. Labels: 32/140 = 22.86%; 29/140 = 20.71%; 32/140 = 22.86%. Does **not** mark statistical significance. | `results/metrics/phase17_descriptive.csv` |
| **Figure 2** | `rq2_confidence_vs_faithfulness` | RQ2 | Scatter of UQ confidence vs LLM-as-judge faithfulness for all 140 UQ cases; ANSWER vs ABSTAIN; vertical locked T=0.65; Spearman ρ = 0.6988 and Holm-adjusted p. | `results/metrics/phase17_tests.csv` (ρ, Holm p); `results/processed/phase16_cases.jsonl` + official judge JSONL (points) |
| **Figure 3** | `rq3_coverage_selective` | RQ3 | Coverage vs selective accuracy (%) at locked T=0.65, including always-answer baselines. UQ coverage 78/140 = 55.71%; UQ selective accuracy 32/78 = 41.03%. | `results/metrics/phase17_descriptive.csv` |

Formats written for each stem: `.png` (300 dpi), `.pdf`, `.svg` under `results/metrics/phase17_figures/`.

---

## Supporting figures (dissertation appendix)

| Figure | File stem | RQ | What it shows | Source result files |
| --- | --- | --- | --- | --- |
| Appendix RQ1 | `rq1_mcnemar_counts` | RQ1 | Paired McNemar cell counts: both correct 19; Single-Agent only 13; Multi-Agent only 10; both incorrect 98. | `results/metrics/phase17_tests.csv` (`rq1_mcnemar_displayed_sa_vs_ma`) |
| Appendix RQ2 | `rq2_llm_faithfulness_box` | RQ2 | Distribution of LLM-as-judge faithfulness by architecture (n=140 each), including UQ abstained drafts. | Official Phase 16 judge JSONL joined to `results/processed/phase16_cases.jsonl` |
| Appendix RQ3 | `rq3_uq_outcomes` | RQ3 | UQ outcome counts at T=0.65: ANSWER correct 32; ANSWER incorrect 46; ABSTAIN incorrect draft 60; ABSTAIN correct draft 2. | `results/config/phase17_statistics_summary.json` (`rq3_abstention_outcomes`) |

These three supporting figures keep the same data as the original Phase 17 plots. Only titles, axis labels, legends, and captions were refined.

---

## What was not changed

- Phase 17 CSV/JSON/Markdown statistical tables
- p-values, confidence intervals, effect sizes
- Locked T = 0.65
- Frozen 140/40 datasets
- RAG architectures
- Phase 15 raw JSONL
- Phase 16 processed JSONL and official judge JSONL
- V1

Do **not** run `scripts/run_statistics.py` to refresh figures. Use `scripts/render_phase17_figures.py`.

Phase 18 is **not started**.
