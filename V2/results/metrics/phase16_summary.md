# Phase 16 metric summary

CPU scoring of saved Phase 15 cases. No RAG/Qwen rerun. Not official RAGAS LLM metrics.

| Architecture | n | ANSWER | ABSTAIN | Answer correctness (displayed) | Claim correctness | Selective acc. | Faithfulness | Context P | Context R | Unsupported emitted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| single_agent | 140 | 140 | 0 | 0.2286 | 0.2286 | 0.2286 | 0.5619 | 0.4304 | 0.9000 | 0.7714 |
| multi_agent | 140 | 140 | 0 | 0.2071 | 0.2071 | 0.2071 | 0.5553 | 0.4304 | 0.9000 | 0.7929 |
| multi_agent_uq | 140 | 78 | 62 | 0.2286 | 0.2429 | 0.4103 | 0.5539 | 0.4304 | 0.9000 | 0.3286 |
