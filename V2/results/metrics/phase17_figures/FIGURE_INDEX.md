# Phase 17 figures — canonical index

One directory, six figures, two files each: high-resolution PNG (viewing) and vector PDF (dissertation).

Directory: `V2/results/metrics/phase17_figures/`

Redraw: `PYTHONPATH=. python scripts/render_phase17_figures.py` (does **not** recompute statistics).

Architecture labels: **Single-Agent**, **Multi-Agent**, **Multi-Agent + UQ**.

Faithfulness wording: `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS**.

Locked threshold: **T = 0.65** from the separate 40-question FinQA DEV calibration set (not the frozen 140).

---

## Main body (primary)

| Figure | RQ | Placement | What it shows | Source result file | Canonical PNG | Canonical PDF |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | RQ1 | Main body | Displayed numeric correctness (%) with Wilson 95% CI; n=140. Single-Agent 32/140 = 22.86%; Multi-Agent 29/140 = 20.71%; Multi-Agent + UQ 32/140 = 22.86%. Does not mark statistical significance. | `results/metrics/phase17_descriptive.csv` | `rq1_answer_correctness_95ci.png` | `rq1_answer_correctness_95ci.pdf` |
| 2 | RQ2 | Main body | UQ confidence vs LLM-as-judge faithfulness for all 140 UQ cases; ANSWER vs ABSTAIN; locked T=0.65; Spearman ρ = 0.6988 and Holm-adjusted p. | `results/metrics/phase17_tests.csv` (ρ, Holm p); `results/processed/phase16_cases.jsonl` + official judge JSONL (points) | `rq2_confidence_vs_faithfulness.png` | `rq2_confidence_vs_faithfulness.pdf` |
| 3 | RQ3 | Main body | Coverage vs selective accuracy (%) at locked T=0.65, with always-answer baselines. UQ coverage 78/140 = 55.71%; UQ selective accuracy 32/78 = 41.03%. | `results/metrics/phase17_descriptive.csv` | `rq3_coverage_vs_selective_accuracy.png` | `rq3_coverage_vs_selective_accuracy.pdf` |

## Appendix (supporting)

| Figure | RQ | Placement | What it shows | Source result file | Canonical PNG | Canonical PDF |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | RQ1 | Appendix | Paired McNemar counts: both correct 19; Single-Agent only 13; Multi-Agent only 10; both incorrect 98. | `results/metrics/phase17_tests.csv` (`rq1_mcnemar_displayed_sa_vs_ma`) | `rq1_mcnemar_counts.png` | `rq1_mcnemar_counts.pdf` |
| 5 | RQ2 | Appendix | LLM-as-judge faithfulness distribution by architecture (n=140 each), including UQ abstained drafts. | Official Phase 16 judge JSONL joined to `results/processed/phase16_cases.jsonl` | `rq2_faithfulness_distribution.png` | `rq2_faithfulness_distribution.pdf` |
| 6 | RQ3 | Appendix | UQ outcomes at locked T=0.65: ANSWER correct 32; ANSWER incorrect 46; ABSTAIN incorrect draft 60; ABSTAIN correct draft 2. | `results/config/phase17_statistics_summary.json` (`rq3_abstention_outcomes`) | `rq3_uq_outcomes.png` | `rq3_uq_outcomes.pdf` |

No SVG copies. No `*_1`, `final`, `new`, `revised`, or `copy` filenames.
