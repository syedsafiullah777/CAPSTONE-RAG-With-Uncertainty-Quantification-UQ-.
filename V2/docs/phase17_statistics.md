# Phase 17 — Statistics (frozen Phase 15/16 only)

Paired statistical analysis of the official 140 × 3 = 420 evaluation. **No RAG rerun. No Qwen generation. No new LLM-as-judge calls.**

Entrypoint: `PYTHONPATH=. python scripts/run_statistics.py`

Evidence: `project_record/evidence/phase17_validation.md`  
Tables: `results/metrics/phase17_*.csv`  
Figures (primary + appendix): `docs/phase17_figures.md` and `results/metrics/phase17_figures/`  
Machine-readable: `results/config/phase17_statistics_summary.json`

Figure-only redraw (no new tests): `PYTHONPATH=. python scripts/render_phase17_figures.py`

## Statistical unit

The unit is the **frozen FinQA test question** (**n = 140**).

The same 140 questions were evaluated independently on `single_agent`, `multi_agent`, and `multi_agent_uq` (no chaining). Between-architecture tests are **paired on `question_id`**. Do not treat 420 cases as independent samples for architecture comparisons.

Locked **T = 0.65** (DEV 40 only). Frozen 140/40 SHAs are verified before analysis proceeds.

## Evaluation layers (do not collapse)

| Layer | Role |
| --- | --- |
| Numeric FinQA displayed correctness | **Primary RQ1** |
| Numeric claim correctness (UQ draft) | RQ1 exploratory |
| `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` | **Primary RQ2** — **not official RAGAS** |
| Coverage / selective accuracy / abstention / `unsupported_emitted` | **RQ3** at T=0.65 |
| Context precision / recall | Retrieval control (identical across architectures) |
| CPU token-overlap | Secondary faithfulness only |

## Tests

α = 0.05, two-sided. Holm–Bonferroni within each family.

| Family | Primary method | Why |
| --- | --- | --- |
| RQ1 confirmatory | Exact McNemar (binomial on discordant pairs) | Paired binary correctness |
| RQ2 confirmatory | Spearman; Mann–Whitney U; Wilcoxon signed-rank | Association / unpaired groups / paired continuous |
| RQ3 confirmatory | Exact McNemar on `unsupported_emitted` | Paired binary emitted-error indicator |
| Continuous paired | Wilcoxon (Shapiro on differences) | Differences are non-normal |
| Rates | Wilson 95% CI; question-level bootstrap (seed 42, 10 000) | Coverage / selective accuracy trade-off |

Assumptions: McNemar needs paired binary outcomes and discordant-pair binomial; Wilcoxon needs symmetric continuous differences (reported; Shapiro fails, so Wilcoxon is used rather than paired t as primary). Spearman assumes monotonic association.

## Official inputs (read-only)

| Artefact | SHA-256 |
| --- | --- |
| Phase 15 `cases.jsonl` | `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` |
| Phase 16 processed | `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91` |
| Official judge JSONL | `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3` |
| Frozen 140 CSV | `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087` |
| Calibration 40 CSV | `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845` |
| `threshold.lock.json` | `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88` |

## Key findings (observed)

**RQ1:** Single-Agent 32/140 vs Multi-Agent 29/140 displayed correct. Exact McNemar p = 0.6776 (Holm p = 0.6776). **Not significant.** The data do **not** support a Multi-Agent accuracy gain.

**RQ2:** UQ confidence vs LLM-as-judge faithfulness Spearman ρ = 0.6988, Holm p = 2.4×10⁻²¹. ANSWER vs ABSTAIN faithfulness Mann–Whitney Holm p = 1.8×10⁻¹⁴. Paired Wilcoxon Multi-Agent vs UQ on all 140 is **not** significant (Holm p = 0.4032). Not official RAGAS.

**RQ3:** At T=0.65, coverage 78/140 = 0.5571; selective accuracy 32/78 = 0.4103; 60 true abstains / 2 false abstains (correct draft withheld). Unsupported-emitted McNemar vs SA and vs MA both Holm-significant. Bootstrap 95% CI for (selective − SA accuracy) 0.0755 to 0.2901.

Full interpretation: `results/metrics/phase17_summary.md`.

Dissertation figures (presentation only; statistics unchanged): `docs/phase17_figures.md`.

Phase 18 is **not started**.
