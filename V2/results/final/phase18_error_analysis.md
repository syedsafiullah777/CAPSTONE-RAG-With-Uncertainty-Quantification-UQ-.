# Phase 18 — Qualitative error analysis

CPU analysis of frozen Phase 15/16/17 artefacts. **No RAG rerun. No Qwen generation. No LLM-as-judge calls. No change to T=0.65 or the frozen 140/40.**

**Judge metric:** `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` — **not official RAGAS.**

**Locked T:** 0.65 (DEV 40 only).

## Sampling

- Method: Stratified sample with random.Random(18). Both false-abstention questions are included in full (all three architectures). Other strata sample without replacement after sorting IDs. A case may belong to more than one stratum.
- Seed: 18
- Qualitative sample: **81 cases** on **42 questions**.
- Rule-based taxonomy is applied to **all 420 cases**; percentages below use the full frozen set.
- The sample is for narrative inspection, not a second test set.

## Taxonomy (primary, mutually exclusive)

| Category | Meaning (recorded-field rule) | Layer |
| --- | --- | --- |
| `correct_answer` | Displayed numeric match to FinQA `program_answer`. | numeric_correct |
| `appropriate_abstention` | UQ ABSTAIN and draft/claim is numerically incorrect. | abstention |
| `incorrect_abstention` | UQ ABSTAIN and draft/claim is numerically correct (false abstention). | abstention |
| `retrieval_failure` | Displayed incorrect and `context_recall=0` (gold file/context_id not in top-k). | retrieval |
| `non_numeric_answer` | ANSWER with no parseable number in the displayed text. | answer_format |
| `incorrect_numerical_reasoning` | Gold number is in evidence text but displayed number does not match. | numeric_error |
| `unsupported_claim` | ANSWER incorrect, gold number not in evidence, LLM-as-judge faithfulness < 0.5. | unsupported_emission |
| `incorrect_despite_partial_evidence` | Residual ANSWER error with gold file retrieved but gold number not in chunk text. | numeric_error |

Numeric incorrectness is **not** called hallucination. `unsupported_emitted` remains answered-and-numerically-wrong, not a labelled hallucination corpus.

The 0.5 faithfulness cut is a **taxonomy split** only. It is not a new operating threshold and was not tuned on the frozen 140.

## Full-set category counts (n=140 per architecture)

| Category | Single-Agent | Multi-Agent | Multi-Agent + UQ |
| --- | ---: | ---: | ---: |
| `correct_answer` | 32 | 29 | 32 |
| `appropriate_abstention` | 0 | 0 | 60 |
| `incorrect_abstention` | 0 | 0 | 2 |
| `retrieval_failure` | 13 | 13 | 4 |
| `non_numeric_answer` | 5 | 5 | 0 |
| `incorrect_numerical_reasoning` | 11 | 11 | 3 |
| `unsupported_claim` | 55 | 52 | 10 |
| `incorrect_despite_partial_evidence` | 24 | 30 | 29 |

### Single-Agent
| Category | n | % of 140 |
| --- | ---: | ---: |
| correct_answer | 32 | 22.86 |
| appropriate_abstention | 0 | 0.00 |
| incorrect_abstention | 0 | 0.00 |
| retrieval_failure | 13 | 9.29 |
| non_numeric_answer | 5 | 3.57 |
| incorrect_numerical_reasoning | 11 | 7.86 |
| unsupported_claim | 55 | 39.29 |
| incorrect_despite_partial_evidence | 24 | 17.14 |

### Multi-Agent
| Category | n | % of 140 |
| --- | ---: | ---: |
| correct_answer | 29 | 20.71 |
| appropriate_abstention | 0 | 0.00 |
| incorrect_abstention | 0 | 0.00 |
| retrieval_failure | 13 | 9.29 |
| non_numeric_answer | 5 | 3.57 |
| incorrect_numerical_reasoning | 11 | 7.86 |
| unsupported_claim | 52 | 37.14 |
| incorrect_despite_partial_evidence | 30 | 21.43 |

### Multi-Agent + UQ
| Category | n | % of 140 |
| --- | ---: | ---: |
| correct_answer | 32 | 22.86 |
| appropriate_abstention | 60 | 42.86 |
| incorrect_abstention | 2 | 1.43 |
| retrieval_failure | 4 | 2.86 |
| non_numeric_answer | 0 | 0.00 |
| incorrect_numerical_reasoning | 3 | 2.14 |
| unsupported_claim | 10 | 7.14 |
| incorrect_despite_partial_evidence | 29 | 20.71 |

## Architecture comparison

Retrieval (`context_precision` / `context_recall`) is identical across architectures by design (shared index). A retrieval miss is therefore a **question-level** failure, not an architecture effect.

Multi-Agent verification is informational: it does not rewrite the draft. VERIFIED + numerically wrong cases are verification false positives, not proof of a Multi-Agent accuracy gain.

## Interpretation

### RQ1

Displayed correctness is 32/140 (Single-Agent) vs 29/140 (Multi-Agent); McNemar was not significant in Phase 17. Shared retrieval and a large both-incorrect cell (98/140) dominate. Multi-Agent verification often agrees with a wrong number (verification false positives). The qualitative sample of discordant pairs should be read as case illustrations, not as a new significance test.

### RQ2

UQ confidence tracks `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` in Phase 17 (Spearman ρ=0.6988). Abstentions are mostly drafts with weak recorded support. UQ **ANSWER** errors still often have high judge faithfulness: abstention filters low-support cases; it does not reliably fix numerical reasoning. This is not official RAGAS and is not a labelled hallucination study.

### RQ3

At locked T=0.65, UQ answers 78/140 and abstains 62/140, including **2 false abstentions** (correct drafts withheld). Appropriate abstention is the main UQ behaviour among abstains. Selective accuracy rises because low-confidence errors are withheld, at the cost of coverage. T was not retuned on the frozen 140.

## Representative sampled cases

### multi_agent_uq:finqa_test_1039 — `incorrect_abstention`

Multi-Agent + UQ; decision=ABSTAIN; displayed_correct=0; claim_correct=1. Gold program_answer=0.6787663948954271; gold file=pdf/K/2006/page_52.pdf. Retrieved files (4 chunks, scores=[0.7393469214439392, 0.694770336151123, 0.6922944784164429, 0.6830730438232422]): pdf/K/2006/page_52.pdf, pdf/BLL/2010/page_37.pdf, pdf/ZBH/2003/page_40.pdf. context_recall=1.00 (gold file/context_id in top-k); context_precision=0.50; gold number in evidence=False. LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)=0.0000 (not official RAGAS). Verification status=VERIFIED. Confidence=0.6464; locked T=0.65. Category rule: UQ ABSTAIN at locked T=0.65 but the withheld draft matches the gold number. This is a false abstention (correct draft withheld). Question: What percentage of Kellanova's net cash provided by operating activities in 2006 was retained as cash flow after accounting for additions to properties? Displayed answer: I cannot answer reliably because supporting evidence is insufficient. UQ draft: The final answer is 64.0%. To determine the percentage of Kellanova's net cash provided by operating activities in 2006 that was retained as cash flow after accounting for additions to properties, we start by identifyin…

### multi_agent_uq:finqa_test_1059 — `appropriate_abstention`

Multi-Agent + UQ; decision=ABSTAIN; displayed_correct=0; claim_correct=0. Gold program_answer=0.09404507113181418; gold file=pdf/ADI/2010/page_80.pdf. Retrieved files (4 chunks, scores=[0.7804912328720093, 0.7499426603317261, 0.6888538599014282, 0.6751288175582886]): pdf/ADI/2010/page_80.pdf, pdf/ADI/2011/page_81.pdf, pdf/ADI/2010/page_60.pdf. context_recall=1.00 (gold file/context_id in top-k); context_precision=0.25; gold number in evidence=False. LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)=0.0000 (not official RAGAS). Verification status=VERIFIED. Confidence=0.6118; locked T=0.65. Category rule: UQ ABSTAIN at locked T=0.65 and the withheld draft is numerically incorrect, so abstention is appropriate on the recorded claim. Question: What was the annual percent return for Analog Devices' investments in the deferred compensation plan, considering the total value of these investments increased from $7,943 in 2009 to $8,690 in 2010? Displayed answer: I cannot answer reliably because supporting evidence is insufficient. UQ draft: Evidence is insufficient. The question asks for the annual percent return, which is a percentage change. The evidence provides the total value of the investments in 2009 as $7,943 and in 2010 as $8,690. However, the evi…

### single_agent:finqa_test_157 — `retrieval_failure`

Single-Agent; decision=ANSWER; displayed_correct=0; claim_correct=0. Gold program_answer=349.0; gold file=pdf/BLK/2014/page_120.pdf. Retrieved files (4 chunks, scores=[0.7628732919692993, 0.7501853704452515, 0.7401494979858398, 0.7149816155433655]): pdf/BLK/2017/page_121.pdf, pdf/BLK/2015/page_124.pdf, pdf/PNC/2014/page_111.pdf. context_recall=0.00 (gold file/context_id in top-k); context_precision=0.00; gold number in evidence=False. LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)=0.0000 (not official RAGAS). Verification status=not recorded (Single-Agent has no verifier). Confidence=n/a; locked T=0.65. Category rule: Displayed answer is numerically incorrect and context_recall=0, so the gold file/context_id was not in the retrieved top-k. Shared retrieval is identical across architectures. Question: What percentage of BlackRock's future notes, as outlined in the company's 2014 financial report, mature by the end of 2017? Displayed answer: Evidence is insufficient. The question asks about the percentage of BlackRock's future notes maturing by the end of 2017, but the provided evidence does not include the 2014 financial report's details on future notes or…

### single_agent:finqa_test_235 — `incorrect_numerical_reasoning`

Single-Agent; decision=ANSWER; displayed_correct=0; claim_correct=0. Gold program_answer=19.666666666666668; gold file=pdf/CDW/2015/page_93.pdf. Retrieved files (4 chunks, scores=[0.7035987377166748, 0.7014197111129761, 0.7010098695755005, 0.6959965229034424]): pdf/CDW/2015/page_93.pdf, pdf/CDW/2014/page_93.pdf, pdf/CDW/2017/page_80.pdf, pdf/EMR/2017/page_78.pdf. context_recall=1.00 (gold file/context_id in top-k); context_precision=0.25; gold number in evidence=True. LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)=1.0000 (not official RAGAS). Verification status=not recorded (Single-Agent has no verifier). Confidence=n/a; locked T=0.65. Category rule: The gold number is present in the retrieved evidence text, but the displayed numeric answer does not match. This indicates incorrect numerical reasoning or extraction, not a retrieval miss. Question: What was the average amount expensed by CDW for company contributions to the profit sharing and other savings plans from 2013 to 2015 in millions? Displayed answer: The average amount expensed by CDW for company contributions to the profit sharing and other savings plans from 2013 to 2015 was $19.4 million. The average amount expensed

### single_agent:finqa_test_1000 — `unsupported_claim`

Single-Agent; decision=ANSWER; displayed_correct=0; claim_correct=0. Gold program_answer=0.4550999999999999; gold file=pdf/SNA/2013/page_34.pdf. Retrieved files (4 chunks, scores=[0.8717727661132812, 0.7975850105285645, 0.7922802567481995, 0.7861218452453613]): pdf/SNA/2013/page_34.pdf, pdf/INTC/2013/page_31.pdf, pdf/GS/2013/page_220.pdf, pdf/MAS/2012/page_26.pdf. context_recall=1.00 (gold file/context_id in top-k); context_precision=0.25; gold number in evidence=False. LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)=0.0000 (not official RAGAS). Verification status=not recorded (Single-Agent has no verifier). Confidence=n/a; locked T=0.65. Category rule: ANSWER is numerically incorrect, the gold number is not in the evidence text, and LLM-as-judge faithfulness is below 0.5. Treated as unsupported emission (not called hallucination unless independent evidence showed fabrication). Question: What is the return on investment if $100 are invested in the S&P 500 at the end of 2008 and sold at the end of 2010, based on the cumulative total shareholder return data provided for Snap-on Incorporated's five-year st… Displayed answer: Evidence is insufficient. The question asks for the return on investment (ROI) for the S&P 500 based on Snap-on's data, but the evidence only provides Snap-on's cumulative returns and not the S&P 500's actual ROI figure…

### single_agent:finqa_test_1039 — `correct_answer`

Single-Agent; decision=ANSWER; displayed_correct=1; claim_correct=1. Gold program_answer=0.6787663948954271; gold file=pdf/K/2006/page_52.pdf. Retrieved files (4 chunks, scores=[0.7393469214439392, 0.694770336151123, 0.6922944784164429, 0.6830730438232422]): pdf/K/2006/page_52.pdf, pdf/BLL/2010/page_37.pdf, pdf/ZBH/2003/page_40.pdf. context_recall=1.00 (gold file/context_id in top-k); context_precision=0.50; gold number in evidence=False. LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)=0.0000 (not official RAGAS). Verification status=not recorded (Single-Agent has no verifier). Confidence=n/a; locked T=0.65. Category rule: Displayed text matches the gold number within the FinQA numeric tolerance. Question: What percentage of Kellanova's net cash provided by operating activities in 2006 was retained as cash flow after accounting for additions to properties? Displayed answer: The final answer is 67.2%. The final answer is 6

### multi_agent:finqa_test_1039 — `incorrect_despite_partial_evidence`

Multi-Agent; decision=ANSWER; displayed_correct=0; claim_correct=0. Gold program_answer=0.6787663948954271; gold file=pdf/K/2006/page_52.pdf. Retrieved files (4 chunks, scores=[0.7393469214439392, 0.694770336151123, 0.6922944784164429, 0.6830730438232422]): pdf/K/2006/page_52.pdf, pdf/BLL/2010/page_37.pdf, pdf/ZBH/2003/page_40.pdf. context_recall=1.00 (gold file/context_id in top-k); context_precision=0.50; gold number in evidence=False. LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)=1.0000 (not official RAGAS). Verification status=VERIFIED. Confidence=0.7449; locked T=0.65. Category rule: ANSWER is numerically incorrect. The gold file/context was retrieved (recall=1) but the gold number is not in the chunk text; judge faithfulness is not low. Residual numeric error with partial document match — not labelled hallucination. Question: What percentage of Kellanova's net cash provided by operating activities in 2006 was retained as cash flow after accounting for additions to properties? Displayed answer: The final answer is 64.0%. To determine the percentage of Kellanova's net cash provided by operating activities in 2006 that was retained as cash flow after accounting for additions to properties, we start by identifyin…

## Limitations

- Categories use recorded metrics (numeric match, gold file/`context_id` overlap, judge score). They cannot see unpublished gold table cells that were not chunked.
- LLM-as-judge is same-model Qwen3-8B, custom/RAGAS-inspired, **not official RAGAS**.
- Sample percentages must not be treated as population rates; use the full-420 tables for that.
- Qualitative text excerpts are truncated.

## Source hashes (verified, unchanged)

- phase15: `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa`
- processed: `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91`
- judge: `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3`
- frozen140: `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087`
- cal40: `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845`
- lock: `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88`

