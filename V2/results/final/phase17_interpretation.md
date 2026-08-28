# Phase 17 statistical results

CPU analysis of frozen Phase 15/16 artefacts. No RAG rerun. No Qwen generation. No new judge calls.

**Statistical unit:** The statistical unit is the frozen FinQA test question (n=140). The same 140 questions were evaluated independently on three architectures (no RAG1→RAG2→RAG3 chaining). Between-architecture tests are paired on question_id. Do not treat 420 cases as independent samples for architecture comparisons.

**Locked T:** 0.65 (DEV 40 only; not retuned on the frozen 140).

**RQ2 metric label:** `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS.**

## Descriptive rates (Wilson 95% CI)

| Architecture | Displayed correct | Displayed acc. | 95% CI low | 95% CI high | Coverage | Selective acc. | Unsupported emitted | LLM faithfulness mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Single-Agent | 32 | 0.2286 | 0.1668 | 0.3048 | 1.0000 | 0.2286 | 0.7714 | 0.3241 |
| Multi-Agent | 29 | 0.2071 | 0.1483 | 0.2817 | 1.0000 | 0.2071 | 0.7929 | 0.3484 |
| Multi-Agent + UQ | 32 | 0.2286 | 0.1668 | 0.3048 | 0.5571 | 0.4103 | 0.3286 | 0.3749 |

## Hypothesis tests

Holm–Bonferroni adjustment is within each family. Do not claim significance unless `significant_holm_0.05` is true.

| ID | RQ | Role | Test | n | Statistic | p | p Holm | Sig. Holm 0.05 | Effect |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rq1_mcnemar_displayed_sa_vs_ma | RQ1 | confirmatory | McNemar exact (binomial, two-sided) | 140 | 10 | 0.6776 | 0.6776 | false | -0.0652 |
| rq1_mcnemar_displayed_sa_vs_uq | RQ1 | exploratory | McNemar exact (binomial, two-sided) | 140 | 14 | 1.0000 | 1.0000 | false | 0.0000 |
| rq1_mcnemar_displayed_ma_vs_uq | RQ1 | exploratory | McNemar exact (binomial, two-sided) | 140 | 4 | 0.3750 | 1.0000 | false | 0.3000 |
| rq1_mcnemar_claim_sa_vs_ma | RQ1 | exploratory | McNemar exact (binomial, two-sided) | 140 | 10 | 0.6776 | 1.0000 | false | -0.0652 |
| rq1_mcnemar_claim_sa_vs_uq | RQ1 | exploratory | McNemar exact (binomial, two-sided) | 140 | 15 | 0.8506 | 1.0000 | false | 0.0357 |
| rq1_mcnemar_claim_ma_vs_uq | RQ1 | exploratory | McNemar exact (binomial, two-sided) | 140 | 6 | 0.1250 | 0.6250 | false | 0.3571 |
| rq2_spearman_uq_confidence_vs_llm_faithfulness | RQ2 | confirmatory | Spearman rank correlation (two-sided) | 140 | 0.6988 | 8.01117e-22 | 2.40335e-21 | true |  |
| rq2_mannwhitney_uq_llm_answer_vs_abstain | RQ2 | confirmatory | Mann–Whitney U (two-sided, unpaired) | 78 | 4033.0000 | 8.83348e-15 | 1.7667e-14 | true |  |
| rq2_wilcoxon_llm_ma_vs_uq | RQ2 | confirmatory | Wilcoxon signed-rank (two-sided, zeros discarded) | 140 | 154.5000 | 0.4032 | 0.4032 | false |  |
| rq2_wilcoxon_llm_sa_vs_ma | RQ2 | exploratory | Wilcoxon signed-rank (two-sided, zeros discarded) | 140 | 482.5000 | 0.5236 | 0.5236 | false |  |
| rq2_wilcoxon_llm_sa_vs_uq | RQ2 | exploratory | Wilcoxon signed-rank (two-sided, zeros discarded) | 140 | 349.0000 | 0.1327 | 0.2654 | false |  |
| rq2_spearman_uq_confidence_vs_claim_correctness | RQ2 | exploratory | Spearman rank correlation (two-sided) | 140 | 0.3297 | 6.93785e-05 | 0.0003 | true |  |
| rq2_spearman_uq_confidence_vs_llm_among_answered | RQ2 | exploratory | Spearman rank correlation (two-sided) | 78 | 0.3190 | 0.0044 | 0.0133 | true |  |
| rq3_mcnemar_unsupported_sa_vs_uq | RQ3 | confirmatory | McNemar exact (binomial, two-sided) | 140 | 7 | 6.41797e-14 | 6.41797e-14 | true | -0.4079 |
| rq3_mcnemar_unsupported_ma_vs_uq | RQ3 | confirmatory | McNemar exact (binomial, two-sided) | 140 | 1 | 9.21572e-19 | 1.84314e-18 | true | -0.4851 |
| sec_overlap_sa_vs_ma | secondary | secondary | Wilcoxon signed-rank (two-sided, zeros discarded) | 140 | 3199.0000 | 0.9509 | 1.0000 | false |  |
| sec_overlap_sa_vs_uq | secondary | secondary | Wilcoxon signed-rank (two-sided, zeros discarded) | 140 | 3126.0000 | 0.7866 | 1.0000 | false |  |
| sec_overlap_ma_vs_uq | secondary | secondary | Wilcoxon signed-rank (two-sided, zeros discarded) | 140 | 1522.0000 | 0.6383 | 1.0000 | false |  |

## RQ1 interpretation

Confirmatory McNemar (exact binomial) on displayed FinQA numeric correctness, Single-Agent vs Multi-Agent, n=140 paired questions: SA 32/140 (Wilson 95% CI 0.1668–0.3048) vs MA 29/140 (Wilson 95% CI 0.1483–0.2817); discordant pairs 23 (SA-only 13, MA-only 10); exact p=0.6776; Holm-adjusted p=0.6776 (family size 1); Cohen's g=-0.0652. This is not statistically significant at α=0.05. The data do not support a Multi-Agent accuracy improvement over Single-Agent.

## RQ2 interpretation

UQ confidence is positively associated with LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired) (Spearman ρ=0.6988, df=138, p=8.011e-22, Holm p=2.403e-21). ANSWER cases have higher judge faithfulness than ABSTAIN cases (means 0.6548 vs 0.0229; Mann–Whitney U=4033.0, p=8.833e-15, Holm p=1.767e-14). Paired Wilcoxon of the same judge score, Multi-Agent vs UQ on all 140 questions, is not significant (W=154.5, p=0.4032, Holm p=0.4032). Holm family size=3. Confidence therefore tracks support/abstention within UQ, but UQ does not significantly raise mean faithfulness versus always-answer Multi-Agent on the full paired set (abstained drafts pull the UQ mean down). Not official RAGAS.

## RQ3 interpretation

At locked T=0.65, UQ coverage is 78/140=0.5571 (Wilson 95% CI 0.4744–0.6368); selective displayed accuracy 32/78=0.4103 (Wilson 95% CI 0.3078–0.5211). Abstention outcomes on the draft: true abstain (incorrect draft) 60; false abstain (correct draft withheld) 2. Unsupported-emitted rate falls from SA 108/140 and MA 111/140 to UQ 46/140; confirmatory McNemar Holm p=6.418e-14 vs SA and 1.843e-18 vs MA (both significant at α=0.05). Bootstrap 95% CI for (UQ selective accuracy − SA accuracy) is 0.0755 to 0.2901 (observed 0.1817). Abstention therefore reduces emitted numeric errors at the cost of coverage; this is not a labelled hallucination corpus.

## Retrieval control

Context precision and recall are identical across architectures by design (shared retrieval). They are retrieval-control metrics, not architecture tests.

## Limitations

- Same-model Qwen3-8B judge; not official RAGAS Faithfulness.
- unsupported_emitted is answered-and-numerically-wrong, not a labelled hallucination corpus.
- Selective accuracy uses a selected subset (UQ ANSWER); it is not a paired accuracy on all 140.
- T=0.65 was locked on DEV 40 only; it was not retuned on the frozen 140.
- Questions are a frozen sample of FinQA test; company repeats may induce weak dependence.
- Phase 17 does not rerun RAG, Qwen generation, or the judge.

