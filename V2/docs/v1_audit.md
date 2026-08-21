# V1 audit (reference only)

Phase 2 review of the original submitted project at the repository root.
**No V1 files were modified.** Concepts may inform V2; code must not be copied wholesale.

## What V1 is

- Controlled comparison of three workflows: Single-Agent RAG, Multi-Agent (draft + verification score), Multi-Agent + UQ (Answer / Warning / Abstain).
- Shared Chroma index, `BAAI/bge-small-en-v1.5`, local **Ollama** (`qwen3.5:9b` in root `config.py`).
- Historical artefact: 140 questions × 3 systems = 420 rows in `results/evaluation_results_final.csv`.
- Domain in V1: multi-subset **RAGBench** (techqa, emanual, cuad, finqa, expertqa) — **not** T²-RAGBench FinQA.

## Useful concepts to reuse (conceptually)

- Three independent architectures with shared retriever/LLM settings.
- Persist raw per-case records; analyse paired by question.
- Show retrieval evidence, verification, confidence, and decision in a live UI.
- Incremental result saving (without V1’s “delete file and restart” behaviour).
- Separate calibration / threshold analysis scripts as a *pattern* (V1’s threshold practice itself is flawed).

## Problems not to carry into V2

| Issue | Why it matters |
| --- | --- |
| Gold `context` exported as one `.txt` per question (`evaluation/build_knowledge_base.py`) | Privileged retrieval; not a realistic shared corpus; leaks oracle context |
| Token-overlap “metrics” (`evaluation/metrics.py`) | Weak operationalisation of correctness/faithfulness |
| Hardcoded thresholds 0.80 / 0.50 | Not locked from a separate calibration set |
| Experiment deletes results and restarts (`evaluation/experiment.py`) | Not resumable; unsafe for Colab |
| Self-consistency ×3 generations | High cost; V1 UQ confidence nearly constant (SD ≈ 0.018) |
| Duplicate questions in the 140-row sample | Breaks paired analysis |
| Local Mac/Ollama as benchmark backend | Violates V2 Colab/Qwen3-8B compute strategy |
| Dashboard replay of frozen CSVs for “results” | Live artefact must run real pipelines |
| Equating wrong answer with hallucination | Methodologically invalid for RQ2 |

## Relevance to FinQA / V2 RQs

- V1 proves the *shape* of the study (three arches, UQ, abstention) but **not** the FinQA corpus or Qwen3-8B/Colab stack.
- V2 must index **source documents**, use FinQA **test** for the frozen 140 and **dev** for threshold lock, and pre-register unsupported/insufficient-evidence rules.

## Checkpoint

- V1 remains untouched.
- Lessons captured for Phases 3+ (sampling, KB, metrics, resume).
