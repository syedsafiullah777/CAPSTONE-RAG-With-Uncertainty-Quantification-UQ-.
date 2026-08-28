# Phase 16 LLM-as-judge faithfulness

LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired). Not official RAGAS Faithfulness. Token-overlap remains secondary.
Does not replace numeric answer correctness. Does not judge context precision/recall.

| Architecture | n | scored | parse fail | LLM faithfulness | LLM faithfulness (ANSWER) | Token-overlap (secondary) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| single_agent | 140 | 140 | 0 | 0.3241 | 0.3241 | 0.5619 |
| multi_agent | 140 | 140 | 0 | 0.3484 | 0.3484 | 0.5553 |
| multi_agent_uq | 140 | 140 | 0 | 0.3749 | 0.6548 | 0.5539 |
