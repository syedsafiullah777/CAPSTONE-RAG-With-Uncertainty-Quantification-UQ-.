# V2 Project Complete Handover

**Document type:** Technical / research project handover and source-of-truth index.  
**Created:** 2026-08-29  
**Scope:** V2 repository as implemented. V1 is reference-only and was not modified for this document.  
**Rule:** Numbers below are copied from named artefacts. Nothing was recalculated. Where sources conflict, both are shown and the authoritative file is named. Missing items are marked **NEEDS VERIFICATION**.

**Authoritative chronology:** `V2/project_record/PROJECT_MASTER_RECORD.md`  
**Authoritative frozen research chain:** `V2/results/final/phase19_artefact_manifest.md` plus pinned SHA-256 values in `V2/src/statistics/constants.py`

This document did **not** rerun RAG, Qwen3-8B, the LLM-as-judge, calibration, the 420-case benchmark, or statistical tests. It did **not** modify datasets, lock files, raw JSONL, or metric tables.

---

## How to read conflicts

| Topic | Authoritative source |
| --- | --- |
| Chronology, phase status, run IDs | `project_record/PROJECT_MASTER_RECORD.md` |
| Frozen hashes | `src/statistics/constants.py` (pins) vs actual files |
| Threshold T | `results/config/threshold.lock.json` |
| Phase 15 420-case run | `results/config/phase15_benchmark_summary.json` |
| Phase 16 CPU metrics | `results/metrics/phase16_summary.csv` / `phase16_by_architecture.json` |
| Phase 16 judge | `results/metrics/phase16_judge_summary.csv` / `results/config/phase16_judge_summary.json` |
| Phase 17 tests | `results/metrics/phase17_tests.csv` / `phase17_summary.md` |
| RQ wording | **Conflict — see §2.** Master record wording is used as the working locked set. No proposal or dissertation file is in this repository. |
| Official university marking rubric | **Not in repository** — see §26. |

---

## 1. Project identity

### Title variants (all present in V2)

| Source | Exact title string |
| --- | --- |
| `project_record/PROJECT_MASTER_RECORD.md` | Multi-Agent RAG with Uncertainty Quantification for Financial Document QA *(Working title)* |
| `config/experiment.yaml` → `project.title` | Multi-Agent RAG with Uncertainty Quantification for Financial Document QA |
| `PROJECT_CONTEXT.md` | Design and Evaluation of a Multi-Agent Retrieval-Augmented Generation Framework with Uncertainty Quantification for Financial Document Question Answering *(Working title; may be refined later without changing the three RQs.)* |
| `README.md` | No dissertation title. Describes V2 as “the revised MSc AI capstone artefact.” |

**Conflict:** Two working titles exist. Neither is marked as the final submitted title. **NEEDS VERIFICATION** which string is on the university submission form.

### Programme / module

| Source | Wording |
| --- | --- |
| `README.md` | “revised MSc AI capstone artefact” |
| `IMPLEMENTATION_PLAN.md` | “MSc RAG V2 rebuild” |
| `.cursor/rules/02-research-constraints.mdc` | “MSc controlled RAG research prototype” |
| `config/experiment.yaml` | `project.name: msc-rag-v2` |

**Exact programme name, module code, credits, supervisor:** **NEEDS VERIFICATION** — not stated in V2 files.

### Project purpose (closest verified statements)

From `README.md`:

> A controlled research prototype comparing three RAG architectures over a financial document corpus (T²-RAGBench FinQA), with uncertainty quantification and confidence-based abstention.

From `.cursor/rules/02-research-constraints.mdc`: three locked RQs; 140 × 3 = 420 independent architecture–question evaluations; primary experimental variable = RAG architecture.

### Problem statement

**No dedicated problem-statement heading** exists in V2. Closest documented problem (from `docs/v1_audit.md` and `docs/dataset_profile.md`):

- Financial document QA over source PDFs rather than oracle gold context.
- Need a controlled comparison of Single-Agent vs Multi-Agent vs Multi-Agent + UQ/abstention.
- FinQA has no native hallucination / insufficient-evidence labels; those must be pre-registered from retrieval/verification/confidence signals.
- Wrong numeric answer must not be equated with hallucination.

**Formal problem statement for a proposal/dissertation:** **NEEDS VERIFICATION** (no proposal file in repo).

### Research aim

**Not explicitly labelled “aim”** in requested project documents. **NEEDS VERIFICATION.**

### Measurable objectives

**No numbered research-objective list** in V2. Closest documented examiner requirements (`PROJECT_CONTEXT.md`):

- Measurable RQs, controlled comparison, documented methods/prompts/settings
- Live artefact with real retrieval, generation, verification, confidence, abstention
- Resumable experiments; raw results preserved; honest statistics
- Calibration/test separation; frozen 140; no result-driven retuning of the sample or threshold

Per-phase engineering objectives exist in `PROJECT_MASTER_RECORD.md` (Phase 1–21 sections). Those are implementation objectives, not a dissertation objective list.

### Original contribution

**Not explicitly stated** in V2. **NEEDS VERIFICATION.**

### Project scope (verified)

- Dataset family: T²-RAGBench (`G4KMU/t2-ragbench`), subset **FinQA**
- Frozen evaluation: **140** FinQA **test** questions
- Threshold calibration: **40** FinQA **dev** questions
- Three independent architectures (no chaining): `single_agent`, `multi_agent`, `multi_agent_uq`
- Benchmark: **140 × 3 = 420** cases
- LLM: Qwen3-8B, GGUF Q4_K_M, `llama_cpp`, Colab Tesla T4
- Live Streamlit artefact using the same V2 RAG pipelines (not Phase 15 answer lookup)
- V1 remains unchanged

### Out of scope (verified from plan/phase docs)

- Colab CLI, gcloud, ADC, Kubernetes, paid inference APIs
- Tuning T on the frozen 140
- Official RAGAS library metrics (judge is custom/RAGAS-inspired)
- Rebuilding the knowledge base from gold FinQA `context`
- Modifying V1
- Using Phase 14’s 9-case run as the official evaluation

---

## 2. Research questions

**No proposal PDF/DOCX and no dissertation manuscript** were found in this repository. Wording therefore comes from V2 project documents. They are **not identical**.

### Approved / locked wording by source

**A. `PROJECT_MASTER_RECORD.md` (authoritative chronology; used as the working locked set)**

1. **RQ1:** Does Multi-Agent RAG improve answer accuracy vs Single-Agent RAG on a financial document corpus?
2. **RQ2:** Does uncertainty quantification reduce hallucinated/unsupported responses in Multi-Agent RAG?
3. **RQ3:** Does confidence-based abstention improve reliability when supporting evidence is insufficient?

**B. `.cursor/rules/02-research-constraints.mdc` (longest form)**

1. **RQ1:** Does a Multi-Agent Retrieval-Augmented Generation architecture improve answer accuracy compared with a traditional Single-Agent RAG system over a financial document corpus?
2. **RQ2:** Does uncertainty quantification reduce hallucinated or unsupported responses in a Multi-Agent RAG system?
3. **RQ3:** Does confidence-based abstention improve the reliability of financial document RAG systems when supporting evidence is insufficient?

**C. `PROJECT_CONTEXT.md`**

- RQ1 is not phrased as a question: “Multi-Agent RAG vs Single-Agent RAG — answer accuracy on a financial document corpus.”
- RQ2/RQ3 match the master record.

**D. `docs/IMPLEMENTATION_PLAN.md`**

1. RQ1: “Multi-Agent RAG vs Single-Agent RAG — answer accuracy on FinQA financial documents.”
2. RQ2 matches the master record.
3. RQ3: “Does confidence-based abstention improve reliability when evidence is insufficient?” *(drops “supporting”)*

**Conflict flag:** Proposal vs dissertation wording cannot be compared because **neither file is in the repository**. Intra-V2 wording differs as above. Do not alter RQs to favour results.

### Hypothesis

**None documented.** **NEEDS VERIFICATION.**

### Per-RQ operationalisation (from Phase 16–17 artefacts)

| | RQ1 | RQ2 | RQ3 |
| --- | --- | --- | --- |
| Objective it addresses | Architecture accuracy comparison | Whether UQ reduces unsupported/unfaithful emissions | Whether confidence abstention improves reliability when evidence is weak |
| Independent variable | RAG architecture (SA vs MA; exploratory SA/MA vs UQ) | UQ confidence / ANSWER vs ABSTAIN; architecture for paired faithfulness | UQ abstention gate at locked T vs always-answer SA/MA |
| Dependent variable | Displayed numeric FinQA correctness | `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)` | coverage, selective accuracy, `unsupported_emitted` |
| Primary metric | Displayed numeric match to `program_answer` (rel_tol=0.01) | LLM-as-judge faithfulness (**not official RAGAS**) | `unsupported_emitted` + coverage/selective accuracy at T=0.65 |
| Confirmatory test | Exact McNemar, SA vs MA, n=140 paired | Spearman; Mann–Whitney; Wilcoxon (Holm family of 3) | Exact McNemar on `unsupported_emitted` vs SA and vs MA |
| Result (verbatim from `phase17_summary.md`) | SA 32/140 vs MA 29/140; p=0.6776; **not significant** | Spearman ρ=0.6988 Holm-significant; Wilcoxon MA vs UQ **not** significant | Unsupported-emitted McNemar Holm-significant; coverage 78/140; selective 32/78 |
| Conclusion | Data do **not** support a Multi-Agent accuracy gain | Confidence tracks judge faithfulness; UQ does not significantly raise mean faithfulness vs always-answer MA on all 140 | Abstention reduces emitted numeric errors at the cost of coverage |

`unsupported_emitted` = ANSWER **and** displayed numeric incorrect. It is **not** a labelled hallucination corpus (`phase17_summary.md`).

---

## 3. Literature / research gap

**Do not treat this section as a literature review.** V2 does not contain a bibliography or citation database.

### What the repository establishes (from `docs/v1_audit.md`)

V1 compared three workflows (Single-Agent, Multi-Agent draft+verify, Multi-Agent+UQ) on multi-subset **RAGBench**, not T²-RAGBench FinQA, using local Ollama. Useful *shape*: three independent architectures, shared retriever, raw per-case records, live UI showing evidence/verification/confidence.

**Gaps V2 was required to close (quoted issues not to carry forward):**

- Gold `context` as retrieval corpus → privileged / oracle leak
- Token-overlap as the only faithfulness operationalisation
- Hardcoded thresholds 0.80 / 0.50 without a separate calibration set
- Non-resumable experiments
- Self-consistency ×3 UQ (V1 confidence nearly constant)
- Duplicate questions in the evaluation sample
- Local Mac/Ollama as the official benchmark backend
- Dashboard replay of frozen CSVs as a “live” artefact
- Equating a wrong answer with hallucination (**methodologically invalid for RQ2**)

### Dataset-side gap (`docs/dataset_profile.md`)

- RQ2: FinQA has **no native hallucination/unsupported label**. Definition must be pre-registered from retrieved evidence + verification. Wrong ≠ hallucination.
- RQ3: **No insufficient_evidence label.** Gold context is oracle. Abstention criteria must come from retrieval/verify signals.
- All RQs: feeding gold context to the generator would invalidate RAG claims. KB must use source PDFs.

### Methods/tools chosen (implemented, not invented citations)

| Choice | Where recorded |
| --- | --- |
| T²-RAGBench FinQA | `config/experiment.yaml`, Phase 2–3 docs |
| Source-PDF Chroma index, BGE-small | Phase 6 / `index_manifest.json` |
| Qwen3-8B Q4_K_M `llama_cpp` on Colab T4 | Phase 7 fingerprint |
| Combined retrieval+verification mean confidence | `src/rag/uncertainty.py`, `prompts.yaml` `method: mean_retrieval_verification` |
| DEV-40 lock, coverage ≥ 0.50, max selective accuracy, lowest-T tie-break | `src/calibration/select.py`, `threshold.lock.json` |
| Custom LLM-as-judge faithfulness | `config/prompts.yaml` `judge`; **not official RAGAS** |

**Published literature citations:** **NEEDS VERIFICATION** — not stored as a V2 evidence pack.

---

## 4. Datasets

### Source dataset

| Item | Value | Authoritative file |
| --- | --- | --- |
| Family | T²-RAGBench (`T2-RAGBench` in yaml) | `config/experiment.yaml` |
| Hugging Face id | `G4KMU/t2-ragbench` | same |
| Subset | FinQA | same |
| Splits | train **6251**, dev **883**, test **1147**, total **8281** | `data/processed/finqa_profile.json` / master record |
| PDF path template | `data/FinQA/{split}/{file_name}` | `experiment.yaml`, Phase 3 |
| Test PDFs in HF repo | **380/380** resolved | master record / `docs/dataset_profile.md` |
| Unique `file_name` across splits | **2789** | `docs/dataset_profile.md` |

### Frozen 140 TEST (final held-out evaluation)

| Item | Value | File |
| --- | --- | --- |
| Path | `data/final/selected_140_questions.csv` | Phase 4 |
| n | 140 | `sampling_manifest.json` |
| Split | **test** | same |
| Seed | **42** | same |
| Frozen at UTC | 2026-08-21T16:01:49.714375+00:00 | same |
| Companies / files | 77 / 140 | same |
| Caps | max 3 per company, max 1 per file | `docs/phase4_sampling.md` |
| Procedure | essential fields → dedupe normalised question (keep lowest id) → seeded shuffle → greedy diversity | same |
| Filter stats | input 1147; dropped_not_essential 1; dropped_duplicate_question 2; eligible 1144 | `sampling_manifest.json` |
| ID-list SHA-256 (JSON-array fingerprint) | `1a69d93e412097a076e8ec836253b8fff53366aefc5ea5f8998020984f6bbd8a` | `sampling_manifest.json` |
| **File SHA-256** | `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087` | `src/statistics/constants.py` |

**Conflict (hash convention, not ID-set):** `sampling_manifest.selected_ids_sha256` hashes a JSON array of IDs. Phase 15 summary `question_ids_sha256` = `8b7061d445b27ef640d613740c94bf663020f0b7dedbf027bd5b64b0c9b02f93` uses newline-joined IDs (`src/run/subset.py`). Phase 19 check 11: **ID sets match the CSV**; hash *conventions* differ.

### Frozen 40 DEV (threshold calibration only)

| Item | Value | File |
| --- | --- | --- |
| Path | `data/calibration/calibration_questions.csv` | Phase 5 |
| n | 40 | `calibration_manifest.json` |
| Split | **dev** | same |
| Purpose | `confidence_threshold_calibration_only` | same |
| Seed | 42 | same |
| Frozen at UTC | 2026-08-21T16:05:05.753226+00:00 | same |
| Companies / files | 32 / 40 | same |
| Caps | max 2 per company, max 1 per file | `docs/phase5_calibration.md` |
| Overlap with frozen 140 | none (ids and questions) | same |
| ID-list SHA-256 | `b229d45331fc18dd7c784175abd37cee3550775f268c843b2417d3f9d2e3aeca` | manifest |
| **File SHA-256** | `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845` | constants.py |
| `threshold_locked` in Phase 5 manifest | **false** | leftover; official T is the lock file |

### Separation (mandatory)

- **40 DEV = threshold calibration only.** Used to lock T=0.65.  
- **140 TEST = final held-out evaluation.** Used in Phase 15/16/17.  
- Lock field `used_frozen_test_140: false` in `threshold.lock.json`.  
- The frozen 140 was **not** used to select T=0.65.

Train split: prototype / distractor PDFs only (50 distractors in the KB). Train questions are not in the 140 or 40.

---

## 5. Knowledge base

| Item | Value | Source |
| --- | --- | --- |
| Source | FinQA **source page PDFs only** — gold `context` not ingested | `index_manifest.json` note; `src/retrieval/index.py` |
| Coverage | frozen test 140 files + calibration 40 files + **50 train distractors** | manifest `roles` |
| Docs requested / indexed | **230 / 230** | manifest |
| Download failures | 0 | manifest |
| Empty-text docs | 0 | manifest |
| Chunks | **1239** | manifest |
| Chunk size / overlap | **900 / 150** characters | `src/retrieval/chunking.py`, yaml, manifest |
| Embedding | `BAAI/bge-small-en-v1.5`, `normalize_embeddings=True`, `batch_size=32` | `src/retrieval/embeddings.py` |
| Vector DB | Chroma, `hnsw:space=cosine` | `src/retrieval/index.py` |
| Collection | `finqa_source_pdfs` | same |
| Persist path (local manifest) | `V2/knowledge_base/index` | manifest `persist_dir` |
| Documents dir | `V2/knowledge_base/documents` | manifest |
| Built at UTC | 2026-08-21T16:20:26.044802+00:00 | manifest |
| Build CLI | `scripts/build_index.py` | Phase 6 |
| Load | `load_collection(persist_dir)` | `src/retrieval/index.py` |
| Query | `retrieve()` | `src/retrieval/retriever.py` |
| Extraction | `src/retrieval/extract.py` (PyMuPDF) | Phase 6 |
| PDF fetch | `src/retrieval/pdf_fetch.py` | Phase 6 |

**Single source of truth for index construction:** `src/retrieval/index.py` + `scripts/build_index.py`, with the written manifest at `knowledge_base/index/index_manifest.json`.

**Conflict:** Master record: “Mac local manifest is stale” vs Colab rebuild on Drive (`MyDrive/MSc-RAG/artifacts/knowledge_base/`). Local manifest still records 230/1239, matching yaml `phase6_*`. **Which copy is the viva runtime index is NEEDS VERIFICATION** (Phase 21 notebook restores Drive KB). Chunk counts in Phase 20 mock preflight also report 1239.

Hugging Face embedding **revision pin:** `experiment.yaml` `embeddings.version: null` — **NEEDS VERIFICATION** if a paper pin is required.

---

## 6. Retrieval

| Item | Value | Source |
| --- | --- | --- |
| Implementation | `src/retrieval/retriever.py` → `retrieve()` | all three RAG modules |
| top-k | **4** | `experiment.yaml` `retrieval.top_k` |
| Embedding model | `BAAI/bge-small-en-v1.5` | yaml / embeddings.py |
| Similarity | `max(0.0, 1.0 - distance)` from Chroma cosine distance | `retriever.py` |
| Metadata stored | file_name, company, year, role, split, context_id, page, etc. | index build |
| Shared across architectures | **Yes** — identical `retrieve()` call and config | `single_agent.py`, `multi_agent.py`, `multi_agent_uq.py` |

**Why held constant:** Primary experimental variable is architecture, not retrieval (`02-research-constraints.mdc`). Phase 17: context precision and recall are **identical** across architectures by design and are retrieval-control metrics, not architecture tests (`phase17_summary.md`).

| Control metric | Value (all three architectures) | Definition |
| --- | --- | --- |
| Context precision | **0.4304** | Fraction of top-k chunks whose `file_name` or `context_id` matches gold freeze (`metrics.py`) |
| Context recall | **0.9000** | 1 if any retrieved chunk matches gold file or context_id, else 0 |
| Context recall (numeric) | **0.1286** | Gold `program_answer` number present in concatenated evidence |

Evidence handling: chunks passed into prompts as `[i] file=… score=…` plus text (`src/rag/prompts.py`). Live UI expands retrieved chunks (`app/streamlit_app.py` `render_evidence`).

---

## 7. Three RAG architectures

All three take the **same original question independently**. There is **no** RAG1→RAG2→RAG3 chaining (`phase15_benchmark_summary.json`: `independent_architectures: true`, `chained: false`).

IDs (`src/rag/schema.py`): `single_agent`, `multi_agent`, `multi_agent_uq`.

### A. Single-Agent RAG (Phase 8)

| Item | Fact |
| --- | --- |
| Flow | retrieve → `build_baseline_prompt` → `llm.generate` → `clean_generated_answer` |
| Module | `src/rag/single_agent.py` |
| Entry | `run_single_agent()` |
| Agents | One generation agent |
| Prompts | `config/prompts.yaml` `baseline` via `src/rag/prompts.py` |
| Retrieval | shared `retrieve()`, top-k=4 |
| Generation | temperature **0.1**, max_new_tokens **512** (yaml / runner) |
| Verification | none (`verification_result=None`) |
| Confidence | none (`confidence=None`) |
| Decision | always `"ANSWER"` |
| Abstention | none |
| Threshold | n/a |
| Docs | `docs/phase8_single_agent.md` |

### B. Multi-Agent RAG (Phase 9)

| Item | Fact |
| --- | --- |
| Flow | retrieve → draft generate → verify |
| Module | `src/rag/multi_agent.py` |
| Entry | `run_multi_agent()` |
| Agents | (1) draft/generation (2) verification |
| Prompts | `multi_agent.generation` and `multi_agent.verification` |
| Verification | `src/rag/verification.py` `compute_verification_result()`: lexical `token_overlap` + LLM score (temp **0.0**, max_new_tokens **32**); if LLM parses, `verification_score = mean(lexical, llm)` else lexical; status `VERIFIED` if score ≥ **0.5** else `WEAK_EVIDENCE` |
| Confidence | set to `verification_score` (not combined UQ) |
| Decision | always `"ANSWER"` |
| Threshold | `threshold=None` (no abstention gate) |
| Docs | `docs/phase9_multi_agent.md` |

### C. Multi-Agent + UQ / Abstention RAG (Phase 10)

| Item | Fact |
| --- | --- |
| Flow | retrieve → draft → verify → `compute_combined_confidence` → `apply_abstention_decision` |
| Module | `src/rag/multi_agent_uq.py` + `src/rag/uncertainty.py` |
| Entry | `run_multi_agent_uq()` |
| Agents | draft + verification + UQ gate (no self-consistency) |
| Retrieval / generation / verification | same as Multi-Agent |
| Confidence | see §9 |
| Decision rule | `if confidence >= threshold: ANSWER else ABSTAIN` |
| Abstention message | `I cannot answer reliably because supporting evidence is insufficient.` |
| Threshold (official) | **T = 0.65** from lock file (benchmark + live). Yaml `confidence_threshold` is **null**; smoke fallback 0.55 is **NOT LOCKED**. |
| Draft preservation | `configuration.draft_answer`; displayed `answer` becomes abstention text on ABSTAIN |
| Docs | `docs/phase10_multi_agent_uq.md` |

Master-record snapshot still lists “whether Arch3 reuses Arch2 draft/verify” as **NEEDS VERIFICATION**. **Code fact:** UQ reuses the same draft/verify helpers as Phase 9. Treat the snapshot line as **stale** relative to `multi_agent_uq.py`.

---

## 8. Prompts

Configured in `V2/config/prompts.yaml` (`version: 0.3.1-phase11-output`). Builders in `src/rag/prompts.py`. Defaults in `prompts.py` match yaml if yaml keys are missing. Text below is copied from yaml (not rewritten).

### Generation — Single-Agent (`baseline`)

**System:**

```text
Answer the financial question using only the evidence below.
Write the final answer once, in one short sentence or one number with its unit.
Do not repeat the answer. Do not repeat these instructions. Do not write reasoning.
Distinguish the quantity the question asks for:
final/ending/cumulative value is not the same as absolute change,
and neither is the same as percentage change or ROI.
If the question asks for ROI or percentage change, do not report the ending investment value.
If the evidence does not contain the answer, write exactly:
Evidence is insufficient.
```

**User template:** `Evidence: {evidence}` / `Question: {question}` / `Final answer (once only):`

### Generation — Multi-Agent / UQ draft (`multi_agent.generation`)

**System:** same constraints as baseline, opening verb “Draft a financial answer…”.  
**User template:** same evidence/question/final-answer slots.

### Verification (`multi_agent.verification`)

**System:**

```text
Score how well the draft answer is supported by the evidence and
whether it reports the quantity the question asked for
(final value vs absolute change vs percentage change/ROI).
Reply with only one number from 0.00 to 1.00.
Do not repeat these instructions and do not write words before or after the number.
```

**User template:** Evidence / Question / Draft answer / `Support score:`

### UQ (`uncertainty`)

No extra LLM prompt. Method: `mean_retrieval_verification`. Abstention message as in §7C.

### Judge (`judge`) — post-hoc Phase 16 only

**Metric label:** `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)`  
**Notes in yaml:** “Not official RAGAS. Does not use gold context or gold answers.”

**System:**

```text
You are scoring whether a model claim is supported by retrieved evidence.
Use only the retrieved evidence below. Do not use outside knowledge.
Reply with only one number from 0.00 to 1.00.
0.00 means the claim is not supported. 1.00 means the claim is fully supported.
Do not repeat these instructions and do not write words before or after the number.
```

**User template:** Retrieved evidence / Question / Claim / `Faithfulness score:`

Implemented: `src/evaluation/judge.py` `build_judge_prompt` (via yaml).

---

## 9. Confidence and threshold

### Confidence definition (code)

From `src/rag/uncertainty.py`:

- `retrieval_score` = mean of top-k retrieval similarities (`average(retrieval_scores)`; 0 if empty).
- `verification_score` = Phase 9 verification score (mean of lexical overlap and parsed LLM support, or lexical only).
- `confidence` = `average([retrieval_score, verification_score])` when `method == "mean_retrieval_verification"`.

`average` = `sum / len` (`src/rag/text_utils.py`).

Single-Agent: no confidence. Multi-Agent: confidence = verification_score only (not the combined formula).

### Decision rule (research)

```text
if confidence >= T: ANSWER
else: ABSTAIN
```

Locked **T = 0.65**. Equivalent: **confidence < 0.65 → ABSTAIN**; **confidence ≥ 0.65 → ANSWER**.

### Threshold selection (DEV 40 only)

| Item | Value | File |
| --- | --- | --- |
| Method | Maximise selective accuracy among T with coverage ≥ 0.50; tie → **lowest T** | `src/calibration/select.py` |
| Rule string | `max_selective_accuracy_coverage_ge_0.50` | lock + yaml |
| Coverage floor | 0.50 | lock |
| Architecture scored | `multi_agent_uq` | lock |
| n | 40 DEV | lock |
| Resulting T | **0.65** | lock |
| Coverage at lock | **0.55** (22 ANSWER / 18 ABSTAIN) | lock |
| Selective accuracy at lock | **12/22 = 0.545454…** | lock |
| `used_frozen_test_140` | **false** | lock |
| Run ID | `phase13_20260826T192003Z_7bcd6ed3` | lock |
| Backend / GPU | `llama_cpp` / Tesla T4 | lock |
| Recorded at UTC | 2026-08-26T19:36:59.876900+00:00 | lock |
| Lock file SHA-256 | `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88` | constants.py |
| Applied to frozen 140 | Phase 15 `threshold: 0.65`, `threshold_locked: true` | phase15 summary |

At T=0.66 on the DEV curve, selective accuracy **falls** to 0.5238 (11/21) — recorded in the lock `curve`. That is calibration-set behaviour, **not** a second research threshold.

### UI-only near-threshold warning (NOT a research threshold)

From `src/rag/live.py` `uq_ui_confidence_overlay` / `_confidence_in_lock_hundredths`:

| Condition | UI |
| --- | --- |
| ABSTAIN | heading `ABSTAIN — Low confidence` |
| ANSWER and `0.65 ≤ confidence < 0.66` | `Moderate confidence — verify supporting evidence.` |
| ANSWER and confidence ≥ 0.66 | ANSWER, no extra warning |
| Missing confidence | `n/a`, no warning |

Note shown on UQ panels: “Warning is a user-facing confidence indicator and does not alter the research decision rule.”

**0.66 is NOT a research threshold.** It is `locked_t + 0.01` (hundredths band) for display only. It is not stored in `threshold.lock.json`. It does not change stored decisions, Phase 15–18 results, or statistics.

---

## 10. Experimental controls

| Class | Values | Source |
| --- | --- | --- |
| Independent variable | RAG architecture | research constraints |
| Dependent variables | numeric correctness; LLM-judge faithfulness; coverage; selective accuracy; unsupported_emitted | Phase 16–17 |
| Controlled | same corpus/KB, embeddings, retrieval top-k=4, LLM, quantisation, generation settings, freeze | constraints + yaml |
| Baseline | Single-Agent RAG | Phase 8 |
| Model | Qwen3-8B | yaml / fingerprints |
| Backend (official GPU runs) | `llama_cpp` | Phase 15/16 judge fingerprints |
| Quantisation | Q4_K_M (`Qwen_Qwen3-8B-Q4_K_M.gguf` from `bartowski/Qwen_Qwen3-8B-GGUF`) | fingerprints |
| GPU | Tesla T4, 15360 MB, driver 580.82.07 | Phase 15 fingerprint |
| Generation temperature | **0.1** | yaml / Phase 15 fingerprint |
| Verification / judge temperature | **0.0** | verification.py / judge.py / yaml |
| max_new_tokens | **512** generation; **32** verify/judge | yaml |
| n_ctx | **4096** | yaml `model.n_ctx` / judge config |
| Random seed | **42** (sampling, stats bootstrap, execution yaml) | yaml / Phase 17 |
| Nondeterminism | llama.cpp GPU inference is not bit-identical across machines; official results are the saved JSONL, not a re-run | integrity rules |
| Checkpoint/resume | incremental JSONL, skip completed, retry failed, case key `{architecture}:{question_id}` | `experiment.yaml` `storage.benchmark` |
| Repeatability | freeze files + SHA pins + lock file + raw JSONL | constants.py |

**Conflict:** `phase16_judge_runtime_fingerprint.json` `model_config.temperature` is **0.1 / max_new_tokens 512** (RAG defaults). Judge **call** settings in `phase16_judge_summary.json` and yaml are **0.0 / 32 / n_ctx 4096**. Phase 19 check: fingerprint is GPU/runtime only; **JSONL/summary is source of truth for judge-call settings**. Status: documented **NEEDS VERIFICATION** mismatch, not a silent reconciliation.

---

## 11. Phase 15 — Final 420-case benchmark

**Do not confuse with Phase 14** (3 questions × 3 architectures = **9** cases, engineering validation only, run_id `phase14_20260826T200828Z_e91e588d`).

| Item | Value | File |
| --- | --- | --- |
| Run ID | `phase15_20260826T203744Z_dae9c3a4` | `phase15_benchmark_summary.json` |
| Recorded at UTC | 2026-08-26T23:11:58.779926+00:00 | same |
| Fingerprint captured | 2026-08-26T20:37:24.223220+00:00 | `phase15_runtime_fingerprint.json` |
| n | 140 × 3 = **420** | summary |
| Completeness | n_completed **420**, n_failed **0**, n_pending **0**, status **PASS** | summary |
| Per architecture | 140 each (completed keys list all three prefixes) | summary |
| Duplicates / missing / errors | 0 / 0 / 0 (Phase 16 completeness block) | `phase16_evaluation_summary.json` |
| Model / backend / quant | Qwen3-8B / `llama_cpp` / Q4_K_M | fingerprint |
| GPU | Tesla T4 CUDA | fingerprint |
| Threshold | 0.65 locked; `used_frozen_test_140_for_lock: false` | summary |
| Random seed | 42 | summary |
| Git commit (Colab) | `e3c6094f267100f13471db7fc8091a7a926bb42b` | fingerprint |
| Raw path | `results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl` | summary |
| SHA-256 | `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` | constants.py |
| Checkpoint (Colab path) | `/content/capstone-rag/V2/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/checkpoint.json` | summary |
| Drive archive (from summary) | `synced: true` → `/content/drive/MyDrive/MSc-RAG/results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4` | summary |
| Drive from this Mac | **NEEDS VERIFICATION** (Phase 19 listing found no local Drive folder) | phase19 audit |
| Notebook | `notebooks/colab_phase15_full_benchmark.ipynb` | master record |
| Entrypoint | `scripts/run_full_benchmark.py` (mock refused) | same |

**Stale docs:** `README.md` still says Phase 15 “Execution **not launched** during notebook creation.” **Authoritative:** summary JSON 420/420 PASS. `PROJECT_CONTEXT.md` still says “No Phase 21 started.” **Authoritative:** master record Phase 21 complete (static checks).

---

## 12. Phase 16 — CPU evaluation

| Item | Value |
| --- | --- |
| Run ID | `phase16_20260826T235141Z_73fdbf58` |
| Mode | CPU scoring of saved Phase 15 cases; **no RAG/Qwen** |
| n | 420 / 140 / 3 |
| Processed path | `results/processed/phase16_cases.jsonl` |
| SHA-256 | `e9e4f80dafffa0d0db970fb4426c9c0b81310717405389b2b7fd5ddb5b231e91` |

### Metric definitions (`phase16_evaluation_summary.json`)

| Metric | Definition (copied) |
| --- | --- |
| answer_correctness (displayed numerical correctness) | Numeric match of the **displayed** answer to FinQA `program_answer` (rel_tol=0.01). UQ ABSTAIN displayed text is usually incorrect. |
| answer_correctness_claim (claim correctness) | Numeric match of the UQ **draft** (or displayed answer) to `program_answer`. |
| selective_accuracy | Displayed numeric accuracy among **ANSWER** decisions only. |
| coverage | n_answer / n |
| abstention_rate | n_abstain / n |
| unsupported_emitted_rate | Fraction of cases that **ANSWERED** and failed displayed numeric match |
| context_precision | Fraction of top-k chunks whose file_name or context_id matches the gold freeze |
| context_recall | 1 if any retrieved chunk matches gold file_name or context_id, else 0 |
| faithfulness (token-overlap) | CPU token-overlap of the model claim vs concatenated retrieved chunk text. **Not official RAGAS.** |

Numeric match: `math.isclose(..., rel_tol=0.01, abs_tol=1e-4)` (`src/evaluation/numeric.py`).

### Exact values (`phase16_summary.csv` / `phase16_by_architecture.json`)

| Metric | Single-Agent | Multi-Agent | Multi-Agent + UQ |
| --- | ---: | ---: | ---: |
| n | 140 | 140 | 140 |
| n_answer / n_abstain | 140 / 0 | 140 / 0 | 78 / 62 |
| coverage | 1.0 | 1.0 | 0.5571428571428572 |
| abstention_rate | 0.0 | 0.0 | 0.44285714285714284 |
| displayed correctness | 0.22857142857142856 (32/140) | 0.20714285714285716 (29/140) | 0.22857142857142856 (32/140) |
| claim correctness | 0.22857142857142856 (32) | 0.20714285714285716 (29) | 0.24285714285714285 (34) |
| selective accuracy | 0.22857142857142856 | 0.20714285714285716 | 0.41025641025641024 (32/78) |
| unsupported_emitted_rate | 0.7714285714285715 | 0.7928571428571428 | 0.32857142857142857 |
| token-overlap faithfulness | 0.5618563773023016 | 0.5552848067268494 | 0.5539262406960617 |
| stored verification score | null | 0.5416947096520864 | 0.5587243834300339 |
| context precision | 0.4303571428571429 | 0.4303571428571429 | 0.4303571428571429 |
| context recall | 0.9 | 0.9 | 0.9 |
| context_recall_numeric | 0.12857142857142856 | 0.12857142857142856 | 0.12857142857142856 |
| mean_confidence | null | 0.5416947096520864 | 0.6440412914408424 |
| mean_latency_seconds | 20.289951890849913 | 22.85057138682142 | 22.855708307164324 |

**Internal distinction (not a conflict of files):** UQ displayed 32/140 vs claim 34/140 because two correct drafts were abstained (false abstentions). Both numbers are in the same CSV.

---

## 13. Phase 16 — LLM-as-judge

**Label (mandatory):** `LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)`  
**Explicitly: NOT official RAGAS.**

| Item | Value | File |
| --- | --- | --- |
| Run ID | `phase16_judge_20260828T152623Z_06661255` | `phase16_judge_summary.json` |
| n | 420 (140 per architecture) | same |
| Completeness | 420 completed, 0 failed, 0 pending, 0 parse failures | same |
| JSONL | `results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl` | same |
| SHA-256 | `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3` | constants.py |
| Model / backend / GPU | Qwen3-8B / `llama_cpp` / Tesla T4 | summary |
| Quantisation | Q4_K_M | summary |
| Temperature | **0.0** | summary / yaml |
| max_new_tokens | **32** | same |
| n_ctx | **4096** | same |
| Gold context / gold answer in prompt | **false / false** | summary |
| RAG rerun | false | summary |
| Drive sync (from summary) | `MyDrive/MSc-RAG/results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255` | summary |
| Updated at UTC | 2026-08-28T15:39:49.448295+00:00 | summary |

**Claim source** (`src/evaluation/judge.py`): SA and MA use displayed `answer`; UQ uses `configuration.draft_answer` so abstention text is not judged as the claim.

**Parse:** `parse_unit_score` — last decimal in [0,1], or scaled integer ≤100.

### Means (`phase16_judge_summary.csv`)

| Architecture | n scored | parse fail | LLM faithfulness (all) | LLM faithfulness (ANSWER only) | Token-overlap (secondary) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Single-Agent | 140 | 0 | **0.32411357142857145** | 0.32411357142857145 | 0.5618563773023016 |
| Multi-Agent | 140 | 0 | **0.348425** | 0.348425 | 0.5552848067268494 |
| Multi-Agent + UQ | 140 | 0 | **0.3749207142857143** | **0.6547564102564102** (n=78) | 0.5539262406960617 |

Rounded in markdown tables: SA **0.3241**, MA **0.3484**, UQ **0.3749**, UQ ANSWER-only **0.6548**.

---

## 14. Phase 17 — Statistics

CPU analysis of frozen Phase 16 rows joined to official judge JSONL. **Not recalculated here.**

| Parameter | Value | File |
| --- | --- | --- |
| n | 140 questions (paired); 420 cases are **not** independent for arch tests | `phase17_summary.md` |
| α | 0.05, two-sided | `src/statistics/constants.py` |
| Holm | within each RQ family | `phase17_summary.md` |
| Bootstrap | seed **42**, **10,000** resamples, question-level | constants.py / summary JSON |
| Wilson | 95% CI on rates | descriptive CSV |

Shapiro–Wilk on paired differences: **normality not met** (all `normality_ok=false`). Wilcoxon/McNemar used (`phase17_assumptions.csv`).

### Confirmatory tests (`phase17_tests.csv` / `phase17_summary.md` / `phase17_effect_sizes.csv`)

**RQ1 McNemar displayed SA vs MA:** n=140; SA 32/140 vs MA 29/140; cells 19 / 13 / 10 / 98; n_discordant 23; p=**0.6776**; Holm p=**0.6776**; significant=**false**; Cohen's g=**−0.0652**; Haldane OR=0.7778; Wilson SA 0.1668–0.3048; Wilson MA 0.1483–0.2817.

**RQ2 Spearman confidence vs LLM faithfulness:** n=140; ρ=**0.6988**; df=138; p=8.01117×10⁻²²; Holm p=2.40335×10⁻²¹; significant=**true**.

**RQ2 Mann–Whitney ANSWER vs ABSTAIN faithfulness:** n=78/62; means 0.6548 vs 0.0229; U=4033.0; p=8.83348×10⁻¹⁵; Holm p=1.7667×10⁻¹⁴; rank-biserial=0.6679; significant=**true**.

**RQ2 Wilcoxon MA vs UQ faithfulness (all 140):** n=140; n_nonzero_diff=27; means 0.3484 vs 0.3749; W=154.5; p=0.4032; Holm p=0.4032; Cohen's dz=0.0743; rank-biserial=−0.1595; 95% CI diff −0.0331 to 0.0861; significant=**false**.

**RQ3 McNemar unsupported SA vs UQ:** rates 0.7714 vs 0.3286; p=6.41797×10⁻¹⁴; Holm p=6.41797×10⁻¹⁴; Cohen's g=−0.4079; significant=**true**.

**RQ3 McNemar unsupported MA vs UQ:** rates 0.7929 vs 0.3286; p=9.21572×10⁻¹⁹; Holm p=1.84314×10⁻¹⁸; Cohen's g=−0.4851; significant=**true**.

Exploratory rows (not confirmatory): see full table in `results/metrics/phase17_summary.md` (McNemar SA/UQ displayed p=1.0000; claim comparisons; secondary token-overlap Wilcoxon all n.s.).

### RQ3 descriptive + bootstrap (`phase17_statistics_summary.json`)

- Coverage 78/140 = 0.5571 (Wilson 0.4744–0.6368)
- Selective accuracy 32/78 = 0.4103 (Wilson 0.3078–0.5211)
- True abstain (incorrect draft) **60**; false abstain (correct draft) **2**
- UQ outcomes: ANSWER correct **32**; ANSWER incorrect **46**; ABSTAIN incorrect draft **60**; ABSTAIN correct draft **2**
- Bootstrap 95% CI (selective − SA accuracy): observed 0.1817; **0.0755–0.2901**
- Bootstrap 95% CI (selective − MA accuracy): observed 0.2031; **0.1363–0.2783**

Interpretation text is copied in `results/metrics/phase17_summary.md` sections “RQ1/RQ2/RQ3 interpretation”. **Not official RAGAS.**

---

## 15. Phase 18 — Error analysis

| Item | Value | File |
| --- | --- | --- |
| Full population | **420** rule-based labels | `phase18_error_cases.csv` (420 data rows) |
| Qualitative sample | **81 cases / 42 questions** | `docs/phase18_error_analysis.md` |
| Seed | `random.Random(18)` | same |
| Sampling | stratified; a case may appear in multiple strata; percentages use **all 420** | same |
| False abstentions in sample | census of both questions (2) | same |
| Faithfulness split in taxonomy | `< 0.5` is a **taxonomy split only**, not an operating threshold | taxonomy.py `FAITHFULNESS_LOW = 0.5` |

### Taxonomy (`src/error_analysis/taxonomy.py`) — order matters

| Category | Rule | Layer |
| --- | --- | --- |
| incorrect_abstention | UQ ABSTAIN and claim **correct** | abstention |
| appropriate_abstention | UQ ABSTAIN and claim **incorrect** | abstention |
| correct_answer | displayed numeric match | numeric_correct |
| retrieval_failure | incorrect and context_recall=0 | retrieval |
| non_numeric_answer | ANSWER, no parseable number | answer_format |
| incorrect_numerical_reasoning | gold number **in** evidence, displayed wrong | numeric_error |
| unsupported_claim | incorrect, gold number not in evidence, LLM faithfulness **< 0.5** | unsupported_emission |
| incorrect_despite_partial_evidence | residual (gold file retrieved, gold number not in chunk, or faithfulness ≥ 0.5) | numeric_error |

**Numeric error is never labelled hallucination** (module docstring).

### Full-420 counts (`phase18_error_summary.csv`)

| Category | SA | MA | UQ |
| --- | ---: | ---: | ---: |
| correct_answer | 32 (22.86%) | 29 (20.71%) | 32 (22.86%) |
| appropriate_abstention | 0 | 0 | 60 (42.86%) |
| incorrect_abstention | 0 | 0 | 2 (1.43%) |
| retrieval_failure | 13 (9.29%) | 13 (9.29%) | 4 (2.86%) |
| non_numeric_answer | 5 (3.57%) | 5 (3.57%) | 0 |
| incorrect_numerical_reasoning | 11 (7.86%) | 11 (7.86%) | 3 (2.14%) |
| unsupported_claim | 55 (39.29%) | 52 (37.14%) | 10 (7.14%) |
| incorrect_despite_partial_evidence | 24 (17.14%) | 30 (21.43%) | 29 (20.71%) |

Per-architecture findings (`docs/phase18_error_analysis.md`): SA largest bucket unsupported_claim 55/140; MA similar retrieval to SA, verification can be VERIFIED on wrong numbers; UQ 60 appropriate abstentions, 2 false abstentions, unsupported_claim drops to 10/140. Displayed correctness 32/140 same as SA via abstention + selective answering.

**Stale line in that doc:** “Phase 20 is **not started**.” Later Phase 20 is the live artefact. Treat master record as chronology.

Limitations: qualitative sample is not a random 420-case census; taxonomy is rule-based from recorded fields; 0.5 faithfulness cut is not T.

---

## 16. Phase 20 — Live Streamlit artefact

| Item | Value |
| --- | --- |
| App | `V2/app/streamlit_app.py` |
| Launch | `cd V2 && PYTHONPATH=. streamlit run app/streamlit_app.py` |
| Official GPU | Colab CUDA Tesla T4, `llama_cpp`, Qwen3-8B Q4_K_M |
| Canonical viva launcher | Phase 21 notebook (below). Phase 20 notes historically cited `notebooks/colab_phase11_live.ipynb`. |
| Locked T | 0.65 from lock file |
| Execution | `run_live_comparison()` calls Phase 8–10 modules independently |
| Precomputed Phase 15 lookup | **forbidden** (`used_precomputed_benchmark_lookup=false`) |
| Logging | optional append to `results/raw/live_sessions.jsonl` |
| Error handling | live layer maps failed retrieval/generation to ERROR/UNAVAILABLE; does not show a fabricated ANSWER |

### Pages (sidebar radio `key="app_page"`)

1. **Live RAG Demo** — three architectures; evidence; verification; confidence; T; ANSWER/ABSTAIN; UI-only warning; runtime/GPU.
2. **Benchmark Results** — read-only frozen Phase 16/17 metric tables. No per-question system answers. No LLM.
3. **Benchmark Questions** — read-only frozen 140 catalogue (`data/final/selected_140_questions.csv` only). Search, company filter, pagination 20/page. Expander shows **full question text**. Gold `program_answer` is labelled dataset reference, not a V2 RAG output.

**Use this question in Live Demo:** `on_click` queues `_pending_app_page` + question text only (`src/rag/benchmark_catalogue.py`). `main()` applies pending page **before** the sidebar radio (avoids `StreamlitAPIException` on `st.session_state.app_page`). Does not copy FinQA gold or Phase 15 answers. Sets live input `fresh_question_text` and source “Fresh question”.

Official Colab T4 Qwen live answers: **NEEDS VERIFICATION** (local mock plumbing PASS).

---

## 17. Phase 21 / final audit

### Phase 19 reproducibility audit (2026-08-28)

| Item | Value |
| --- | --- |
| Evidence | `project_record/evidence/phase19_reproducibility_audit.md` |
| Result | **17 PASS / 0 FAIL / 4 NEEDS VERIFICATION** |
| Scientific chain | PASS |
| Dataset/result hashes | match `src/statistics/constants.py` (see §25) |
| Threshold | T=0.65; `used_frozen_test_140=false` |
| Judge completeness | 420/420 |
| Benchmark completeness | 420/420 |
| Figure set | six PNG+PDF in `results/metrics/phase17_figures/` |

**NEEDS VERIFICATION remaining from that audit:**

1. Judge fingerprint JSON vs judge-call settings (JSONL is source of truth: 0.0 / 32 / 4096)
2. `experiment.yaml` `phase5_threshold_locked: false` leftover; yaml `confidence_threshold` null **by design**
3. Google Drive `MSc-RAG` folder **not listed from the audit Mac**
4. GitHub commit completeness of Phase 15–19 artefacts (user action)

### Phase 21 launcher (2026-08-29)

| Item | Value |
| --- | --- |
| Notebook | `notebooks/colab_phase21_final_live_demo.ipynb` |
| Tests | `tests/test_phase21_final_live_demo.py` — 3 passed (static) |
| Does not rerun | 420, calibration, judge, statistics, `run_live_demo.py`, KB rebuild |
| Env | `V2_LIVE_BACKEND=llama_cpp`, `V2_FORBID_MOCK=1`, `V2_REQUIRE_CUDA=1` |
| Browser | Colab `proxyPort(8501)` only — not Mac `127.0.0.1:8501` |
| Official T4 viva launch | **NEEDS VERIFICATION** |

Git remote observed 2026-08-29: `https://github.com/syedsafiullah777/CAPSTONE--RAG-WITH-UNCERTAINITY-QUANTIFICATION-.git`, branch `cursor/empty-v2-workspace`. Whether all V2 phases are pushed: **NEEDS VERIFICATION**.

---

## 18. Final numerical master table

Sources: `phase16_summary.csv`, `phase16_judge_summary.csv`, `phase17_descriptive.csv`. Wilson CIs from Phase 17 descriptive. n_correct from Phase 16 JSON.

| Metric | Single-Agent | Multi-Agent | Multi-Agent + UQ |
| --- | ---: | ---: | ---: |
| n questions | 140 | 140 | 140 |
| n_answer / n_abstain | 140 / 0 | 140 / 0 | 78 / 62 |
| Displayed correct (k) | 32 | 29 | 32 |
| Displayed correctness | 0.2286 | 0.2071 | 0.2286 |
| Wilson 95% CI (displayed) | 0.1668–0.3048 | 0.1483–0.2817 | 0.1668–0.3048 |
| Claim correct (k) | 32 | 29 | 34 |
| Claim correctness | 0.2286 | 0.2071 | 0.2429 |
| Coverage | 1.0000 | 1.0000 | 0.5571 |
| Coverage Wilson CI | 0.9733–1.0000 | 0.9733–1.0000 | 0.4744–0.6368 |
| Abstention rate | 0.0000 | 0.0000 | 0.4429 |
| Selective accuracy | 0.2286 | 0.2071 | 0.4103 |
| Selective Wilson CI | 0.1668–0.3048 | 0.1483–0.2817 | 0.3078–0.5211 |
| unsupported_emitted | 0.7714 | 0.7929 | 0.3286 |
| unsupported Wilson CI | 0.6952–0.8332 | 0.7183–0.8517 | 0.2563–0.4100 |
| LLM-as-judge faithfulness (all) | 0.3241 | 0.3484 | 0.3749 |
| Judge faithfulness SD | 0.4544 | 0.4543 | 0.4715 |
| Judge faithfulness Wilson-style mean CI (descriptive file) | 0.2482–0.4000 | 0.2725–0.4243 | 0.2961–0.4537 |
| Judge faithfulness ANSWER-only | 0.3241 | 0.3484 | 0.6548 |
| Token-overlap faithfulness | 0.5619 | 0.5553 | 0.5539 |
| Context precision | 0.4304 | 0.4304 | 0.4304 |
| Context recall | 0.9000 | 0.9000 | 0.9000 |
| Mean confidence | n/a (null) | 0.5417 | 0.6440 |
| Confidence SD | n/a | 0.2849 | 0.1442 |
| Mean verification (stored) | n/a | 0.5417 | 0.5587 |
| Mean latency (s) | 20.29 | 22.85 | 22.86 |

Judge metric label remains: **LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)**. Not official RAGAS.

---

## 19. RQ-by-RQ final findings

### RQ1

- **Tested:** Multi-Agent vs Single-Agent displayed numeric accuracy on the same 140 FinQA test questions.
- **Dataset:** frozen 140 FinQA test.
- **Primary metric:** displayed numeric match to `program_answer`.
- **Test:** exact McNemar, n=140 paired.
- **Result:** 32/140 vs 29/140; p=0.6776; Holm p=0.6776; Cohen's g=−0.0652.
- **Significance:** **not significant**.
- **Interpretation:** Multi-Agent did **not** show a significant accuracy improvement over Single-Agent.
- **Limitation:** both-incorrect cell 98/140; numeric FinQA is hard; shared retrieval already high-recall.
- **Conclusion:** Do not claim an RQ1 accuracy gain.

### RQ2

- **Tested:** whether UQ confidence relates to (and whether UQ changes) LLM-as-judge faithfulness.
- **Dataset:** frozen 140; judge on 420 cases.
- **Primary metric:** LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired) — **not official RAGAS**.
- **Tests:** Spearman ρ=0.6988 (Holm significant); Mann–Whitney ANSWER vs ABSTAIN (Holm significant); Wilcoxon MA vs UQ on all 140 (Holm p=0.4032, **not** significant).
- **Interpretation:** UQ confidence had a **strong relationship** with LLM-judge faithfulness. UQ did **not** significantly raise mean faithfulness versus always-answer Multi-Agent on the full paired set (abstained drafts pull the UQ mean).
- **Limitation:** same-model judge; custom metric; unsupported ≠ labelled hallucination.
- **Conclusion:** Support the confidence–faithfulness association; do not claim a significant paired faithfulness gain vs Multi-Agent on all 140.

### RQ3

- **Tested:** confidence-based abstention at locked T=0.65 vs always-answer systems.
- **Primary metrics:** coverage, selective accuracy, unsupported_emitted.
- **Tests:** McNemar on unsupported_emitted vs SA and MA (both Holm-significant).
- **Result:** coverage 78/140=0.5571; selective accuracy 32/78=0.4103; 60 true / 2 false abstains; unsupported_emitted 0.3286 vs 0.7714 / 0.7929.
- **Interpretation:** UQ **traded coverage for selective accuracy** and reduced emitted numeric errors. This is not a labelled insufficient-evidence corpus.
- **Limitation:** selective accuracy is on the ANSWER subset, not paired accuracy on all 140; T locked on n=40 DEV.
- **Conclusion:** Abstention improves emitted-error rate at the cost of coverage; do not over-claim “reliability” beyond the pre-registered metrics.

### Cross-cutting findings (required)

- High retrieval quality (context recall 0.90) does **not** guarantee correct numerical reasoning (displayed correctness ~23%).
- Verification does **not** guarantee numerical correctness (MA verification can be VERIFIED on wrong numbers; Phase 18).
- Negative/non-significant findings are retained.

---

## 20. Figures

Canonical directory: `V2/results/metrics/phase17_figures/`  
Index: `FIGURE_INDEX.md`  
Each figure: **PNG (300 dpi) + PDF**. No SVG.

| # | Filename stem | Format | RQ | Placement | Source data | Interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `rq1_answer_correctness_95ci` | PNG+PDF | RQ1 | **Main body** | `phase17_descriptive.csv` | Displayed correctness % + Wilson 95% CI; does **not** mark significance |
| 2 | `rq2_confidence_vs_faithfulness` | PNG+PDF | RQ2 | **Main body** | tests.csv + processed JSONL + judge JSONL | UQ confidence vs judge faithfulness; Spearman ρ=0.6988 |
| 3 | `rq3_coverage_vs_selective_accuracy` | PNG+PDF | RQ3 | **Main body** | descriptive.csv | Coverage vs selective accuracy at T=0.65 |
| 4 | `rq1_mcnemar_counts` | PNG+PDF | RQ1 | Appendix | tests.csv | Cells 19 / 13 / 10 / 98 |
| 5 | `rq2_faithfulness_distribution` | PNG+PDF | RQ2 | Appendix | judge JSONL + processed JSONL | Distribution by architecture, n=140 including UQ drafts |
| 6 | `rq3_uq_outcomes` | PNG+PDF | RQ3 | Appendix | statistics_summary.json | 32 / 46 / 60 / 2 |

**Three primary dissertation figures:** 1, 2, 3 (main body).

Redraw command (does not recompute statistics): `PYTHONPATH=. python scripts/render_phase17_figures.py`

---

## 21. Error / limitation summary

| Area | Limitation (from recorded docs) |
| --- | --- |
| Numerical accuracy | Displayed correctness 22.86% / 20.71% / 22.86%; FinQA numerical reasoning remains hard |
| Retrieval | Context recall 0.90 but context_recall_numeric 0.13; gold number often absent from chunks |
| Verification | False positives (VERIFIED + wrong claim) documented in Phase 18 |
| UQ conservativeness | Coverage 55.71%; 62/140 abstain; 2 false abstentions |
| Threshold selection | Locked on **n=40 DEV**; coverage floor 0.50; not retuned on test |
| DEV sample size | 40 is small; lock curve is noisy |
| Same-model LLM judge | Qwen3-8B judges Qwen3-8B outputs |
| Custom/RAGAS-inspired evaluation | **Not official RAGAS** |
| Judge limitations | parse-to-scalar; no gold context; fingerprint file does not store judge-call temperature |
| Benchmark limitations | Frozen 140 is a sample of FinQA test; company repeats may induce weak dependence; GPU nondeterminism |
| Qualitative analysis | 81/42 sample; rule-based taxonomy; 0.5 split is not T |
| Live demo | Official T4 Qwen answers **NEEDS VERIFICATION**; mock plumbing is not official |

---

## 22. Ethics / legal / social / professional

**No ethics application, GDPR assessment, licence file, or professional-issues section** was found under V2 (search over `*.md`/`*.yaml` for ethics/licence/GDPR).

| Topic | Status |
| --- | --- |
| University ethics approval | **NEEDS VERIFICATION** |
| Privacy | FinQA is public financial filings via T²-RAGBench; no additional privacy analysis in V2 |
| Data licensing | Hugging Face `G4KMU/t2-ragbench` licence **NEEDS VERIFICATION** (not copied into V2) |
| Legal | **NEEDS VERIFICATION** |
| Social implications | **NEEDS VERIFICATION** |
| Professional / responsible AI | Closest: honest reporting of non-significant RQ1; abstention when evidence is weak; live artefact must not hide failures as ANSWER. Not a formal responsible-AI report. |

Do not invent an ethics narrative.

---

## 23. Project management

Development timeline (from master record; GPU as recorded):

| Phase | Date | Purpose | GPU? | Changed freeze/T/results? |
| --- | --- | --- | --- | --- |
| 1 | 2026-08-21 | V2 foundation | No | New V2 tree |
| 2 | 2026-08-21 | V1 audit + FinQA profile | No | profile JSON |
| 3 | 2026-08-21 | PDF resolvability | No | probe JSON |
| 4 | 2026-08-21 | Freeze 140 test | No | **created freeze** |
| 5 | 2026-08-21 | Freeze 40 DEV | No | **created cal freeze** |
| 6 | 2026-08-21 | KB | No | **created index** |
| 7 | 2026-08-21/22 | Qwen backend | Yes T4 | runtime fingerprints |
| 8–10 | 2026-08-22/23 | Three architectures | Yes T4 smokes | code; not 420 |
| 11 | 2026-08-23/24 | Live Streamlit | Colab reported | app |
| 12 | 2026-08-24/26 | 18-case pilot | Yes T4 | pilot JSONL |
| 13 | 2026-08-26 | Lock T | Yes T4 | **created lock T=0.65** |
| 14 | 2026-08-26 | 9-case runner validation | Yes T4 | 9-case JSONL only |
| 15 | 2026-08-26/27 | Official 420 | Yes T4 | **official raw JSONL** |
| 16 | 2026-08-26/28 | CPU metrics + judge | CPU + T4 judge | processed + judge JSONL |
| 17 | 2026-08-28 | Statistics + figures | CPU | stats tables + figures |
| 18 | 2026-08-28 | Error analysis | CPU | analysis CSVs |
| 19 | 2026-08-28 | Reproducibility audit | CPU | audit; no rewrite |
| 20 | 2026-08-28/29 | Live artefact at T=0.65 | mock local; T4 NV | app/UI |
| 21 | 2026-08-29 | Canonical Colab launcher | static tests | notebook |

Major decisions: listed in `DECISIONS.md` (dated 2026-08-21 through 2026-08-28) and numbered standing rules in the master-record decisions log.

Scope change: numbered Phase 20 was **redefined** from a “dissertation evidence pack” to **final live-artefact validation** (Decision 2026-08-28). Phase 18 in `IMPLEMENTATION_PLAN.md` table still says “Dissertation evidence pack / Not started” in one historical row — **conflict** with completed qualitative error analysis.

Problems/fixes of note: Colab retrieval required rebuilding the index on Colab (Phase 8 Option B); Streamlit `app_page` assignment after widget instantiation (fixed 2026-08-29 via pending-page callback); GGUF filename correction to `Qwen_Qwen3-8B-Q4_K_M.gguf`.

Evidence: `project_record/evidence/phaseN_validation.md`. Backup template: `PHASE_COMPLETION_BACKUP_TEMPLATE.md`. Version control: GitHub remote exists; uncommitted V2 work may remain — **NEEDS VERIFICATION**.

---

## 24. Repository structure

```text
V2/
├── app/                    Streamlit live artefact (source)
├── config/                 experiment.yaml, prompts.yaml (configuration)
├── data/
│   ├── processed/          FinQA profile (processed)
│   ├── calibration/        frozen 40 DEV (dataset freeze)
│   └── final/              frozen 140 TEST + manifests (dataset freeze)
├── docs/                   phase notes (documentation)
├── knowledge_base/         documents + Chroma index (artefact; large)
├── notebooks/              Colab GPU entrypoints (source)
├── project_record/         master record + evidence (evidence/documentation)
├── results/
│   ├── raw/                Phase 12–16 raw JSONL (raw; often gitignored)
│   ├── processed/          phase16_cases.jsonl (processed)
│   ├── metrics/            Phase 16–17 tables + figures (final tables)
│   ├── analysis/           Phase 18 CSVs (processed analysis)
│   ├── config/             lock, summaries, fingerprints (configuration/results)
│   ├── checkpoints/        resume state
│   └── final/              manifests, interpretations (final)
├── scripts/                CLI entrypoints (source)
├── src/                    Python package (source)
└── tests/                  pytest (source)
```

| Class | Examples |
| --- | --- |
| Source | `src/`, `app/`, `scripts/`, `notebooks/`, `tests/` |
| Configuration | `config/experiment.yaml`, `config/prompts.yaml` |
| Raw results | `results/raw/phase15_benchmark/…/cases.jsonl`, `results/raw/phase16_judge/…/judge.jsonl` |
| Processed | `results/processed/phase16_cases.jsonl` |
| Final metrics | `results/metrics/phase16_*.csv`, `phase17_*.csv`, figures |
| Evidence | `project_record/evidence/` |
| Documentation | `docs/`, `PROJECT_CONTEXT.md`, `DECISIONS.md`, this handover |

V1 (repository root outside `V2/`) is reference-only.

---

## 25. Source-of-truth map

| FACT | VALUE | AUTHORITATIVE FILE |
| --- | --- | --- |
| FinQA split counts | 6251 / 883 / 1147 / 8281 | `data/processed/finqa_profile.json` |
| Frozen 140 n / seed | 140 / 42 | `data/final/sampling_manifest.json` |
| Frozen 140 file SHA-256 | `88899ae9c66fb47bf4aa50e197d91aa171adcb882ae36f066bf614ff40fba087` | `src/statistics/constants.py` |
| Cal 40 n / seed | 40 / 42 / dev | `data/calibration/calibration_manifest.json` |
| Cal 40 file SHA-256 | `1325b595ae1f9404802879ad06f52be7f7b63d805ab1edf5b66c3b608a478845` | constants.py |
| KB docs / chunks | 230 / 1239 | `knowledge_base/index/index_manifest.json` |
| Chunking | 900 / 150 | same + yaml |
| Embeddings | BAAI/bge-small-en-v1.5 | same |
| Collection | finqa_source_pdfs | `src/retrieval/index.py` |
| top-k | 4 | `config/experiment.yaml` |
| Locked T | 0.65 | `results/config/threshold.lock.json` |
| Lock SHA-256 | `8981233604e64959386292d3d1fbdeebd4e983c0520fde3b4467772281687d88` | constants.py |
| Lock used frozen 140 | false | lock file |
| Phase 15 run ID | phase15_20260826T203744Z_dae9c3a4 | `phase15_benchmark_summary.json` |
| Phase 15 n | 420/420 PASS | same |
| Phase 15 SHA-256 | `f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa` | constants.py |
| Displayed correct SA/MA/UQ | 32 / 29 / 32 | `phase16_summary.csv` |
| UQ coverage / selective | 78/140 ; 32/78 | same |
| Judge means | 0.3241 / 0.3484 / 0.3749 ; UQ ANSWER 0.6548 | `phase16_judge_summary.csv` |
| Judge run ID | phase16_judge_20260828T152623Z_06661255 | `phase16_judge_summary.json` |
| Judge SHA-256 | `093c4699b68e9653125fcd08e3b25b0d10a3357be3a20bc817a5a71e8498ebe3` | constants.py |
| RQ1 McNemar p | 0.6776 n.s. | `phase17_tests.csv` |
| RQ2 Spearman ρ | 0.6988 Holm-sig | same |
| RQ3 McNemar Holm p | 6.418e-14 / 1.843e-18 | `phase17_summary.md` |
| Error sample | 81 cases / 42 questions / seed 18 | `docs/phase18_error_analysis.md` |
| UI warning band | 0.65 ≤ c < 0.66 | `src/rag/live.py` |
| Live app | `app/streamlit_app.py` | Phase 20/21 docs |

---

## 26. Rubric / feedback evidence map

**Official university marking rubric:** **not present in this repository** (`*rubric*`, `*EXAMINER*`, `*MARKING*` glob = empty).  
**Proposal/dissertation manuscript:** **not present.**

The table below maps **examiner-style requirements that *are* written in V2** (`PROJECT_CONTEXT.md`, implementation plan, research constraints). Status is about **repository evidence**, not a claim that a written dissertation chapter exists.

| # | Requirement (from V2 docs) | Supporting evidence | Path | Status |
| --- | --- | --- | --- | --- |
| 1 | Measurable RQs | Three RQs + confirmatory tests | master record; `phase17_tests.csv` | **ADEQUATE** in repo / **NEEDS REPORT EVIDENCE** in a dissertation |
| 2 | Controlled comparison | Shared KB/retrieval/LLM; architecture as IV | yaml; Phase 15 summary | **STRONG** in code+results |
| 3 | Documented methods/prompts/settings | yaml + prompts.yaml + fingerprints | `config/`, `results/config/` | **STRONG** |
| 4 | Live artefact with real pipelines | Streamlit + `run_live_comparison` | `app/streamlit_app.py`, `src/rag/live.py` | **STRONG** plumbing / Colab T4 answers **NOT VERIFIED** |
| 5 | Resumable experiments | checkpoint/resume in runner | `src/run/benchmark.py`, yaml storage | **STRONG** |
| 6 | Raw results preserved | Phase 15 JSONL SHA pin | `results/raw/…/cases.jsonl` | **STRONG** (file gitignored) |
| 7 | Honest statistics | RQ1 n.s. recorded | `phase17_summary.md` | **STRONG** in tables / **NEEDS REPORT EVIDENCE** in prose |
| 8 | Calibration/test separation | DEV 40 vs TEST 140; lock flag | lock file; manifests | **STRONG** |
| 9 | Frozen 140 not retuned | `used_frozen_test_140: false` | lock + Phase 15 summary | **STRONG** |
| 10 | Ethics / legal / social | — | — | **NOT VERIFIED** |
| 11 | Literature review | V1 audit + dataset gap only | `docs/v1_audit.md` | **NEEDS REPORT EVIDENCE** |
| 12 | Official marking rubric criteria 1–N | — | — | **NOT VERIFIED** (file missing) |

Do not claim report criteria are satisfied solely because code exists.

---

## 27. Viva / demonstration evidence

| Item | Recorded fact |
| --- | --- |
| Canonical notebook | `V2/notebooks/colab_phase21_final_live_demo.ipynb` |
| Streamlit | `PYTHONPATH=. python -m streamlit run app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true` (Colab) |
| Architectures | All three, independent, same question |
| Catalogue | Benchmark Questions page; frozen 140; Use this question in Live Demo copies **text only** |
| Known-good frozen ID | `finqa_test_1000` (`KNOWN_GOOD_QUESTION_ID`) |
| Fresh KB example | `FRESH_KB_QUESTION` — Snap-on 2013 cumulative TSR from $100 invested 31 Dec 2008 |
| Insufficient-evidence example | SpaceX FY2025 GAAP net income + Starship launches (`live_insufficient_evidence`) |
| Confidence | mean(retrieval, verification); T=0.65 research gate |
| Abstention | confidence < 0.65 → abstention message; 2 false abstains in the 420 |
| Negative findings | RQ1 McNemar n.s.; Wilcoxon MA vs UQ faithfulness n.s. |
| UI 0.66 band | display-only; not T |

Do not present mock backend outputs as Qwen3-8B results. Do not open Mac `127.0.0.1:8501` as the official demo.

---

## 28. Unresolved items

1. **Proposal vs dissertation RQ wording** — neither manuscript in repo; V2 sources already disagree (see §2).
2. **Final submitted title** — two working titles.
3. **Programme/module/supervisor/ethics** — not in V2.
4. **Official marking rubric** — not in repo.
5. **Literature citations** — not packaged as V2 evidence.
6. **Google Drive `MSc-RAG` from this Mac** — Phase 19 **NEEDS VERIFICATION**; Colab summaries *report* sync.
7. **GitHub** — remote exists; whether all phases are committed/pushed **NEEDS VERIFICATION**.
8. **Official Colab T4 live demo (Phase 20/21)** — **NEEDS VERIFICATION**.
9. **Which KB copy is viva runtime** — local vs Drive restore.
10. **Stale documentation:** `README.md` Phase 15 “not launched”; `PROJECT_CONTEXT.md` “No Phase 21 started”; `phase18_error_analysis.md` / `phase19_artefact_manifest.md` “Phase 20 not started”; `IMPLEMENTATION_PLAN.md` Phase 18 labelled as dissertation pack; yaml `phase5_threshold_locked: false`; master-record snapshot “Arch3 reuse NEEDS VERIFICATION”.
11. **Judge fingerprint vs judge-call hyperparameters** — documented mismatch.
12. **Embedding revision pin** — null in yaml.
13. **Hugging Face dataset licence text** — not copied in V2.

Do not resolve these by guessing.

---

## 29. Final project status

| Phase | Purpose | Status | Principal artefacts | Key result | GPU? | Changed research artefacts? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Foundation | Complete | V2 tree, yaml, tests | package loads | No | created V2 |
| 2 | Profile / V1 audit | Complete | `finqa_profile.json`, `v1_audit.md` | split counts | No | docs/profile |
| 3 | PDF verification | Complete | pdf probe | 380/380 | No | probe |
| 4 | Freeze 140 | Complete | selected_140 CSV | n=140 seed 42 | No | **freeze created** |
| 5 | Freeze 40 DEV | Complete | calibration CSV | n=40 seed 42 | No | **cal freeze created** |
| 6 | KB | Complete | index 230/1239 | source PDFs only | No | **index created** |
| 7 | Qwen backend | Complete | fingerprints | T4 llama_cpp PASS | Yes | fingerprints |
| 8 | Single-Agent | Complete | `single_agent.py` | smoke PASS | Yes | architecture 1 |
| 9 | Multi-Agent | Complete | `multi_agent.py` | smoke PASS | Yes | architecture 2 |
| 10 | UQ/abstention | Complete | `multi_agent_uq.py` | smoke PASS | Yes | architecture 3 |
| 11 | Live app | Complete | `streamlit_app.py` | plumbing; T4 user-reported | Partial | app |
| 12 | Pilot 18 | Complete | pilot JSONL | 18/18 T4 | Yes | pilot only |
| 13 | Lock T | Complete | `threshold.lock.json` | **T=0.65** | Yes | **lock created** |
| 14 | 9-case validation | Complete | 9-case JSONL | engineering only | Yes | not official 420 |
| 15 | Official 420 | Complete | cases.jsonl | **420/420 PASS** | Yes | **official raw** |
| 16 | CPU eval + judge | Complete | processed + judge JSONL | metrics + judge means | CPU + Yes | **official metrics/judge** |
| 17 | Statistics + figures | Complete | tests.csv + 6 figures | RQ1 n.s.; RQ2/RQ3 mixed | CPU | stats/figures |
| 18 | Error analysis | Complete | error CSVs | 420 labelled; 81/42 sample | CPU | analysis tables |
| 19 | Reproducibility audit | Complete | audit md/json | 17 PASS / 4 NV | CPU | none rewritten |
| 20 | Live artefact T=0.65 | Complete (plumbing) | Streamlit pages | navigation + lock T | mock local; T4 NV | UI only |
| 21 | Canonical launcher | Complete (static) | colab_phase21 notebook | 3 tests PASS | T4 NV | notebook only |

---

## 30. Final integrity rules

- No frozen dataset changes after lock.
- No test-set threshold tuning (`used_frozen_test_140: false`).
- No result fabrication.
- No replacement of negative findings (RQ1 McNemar n.s. stands).
- No mixing of mock results with official Qwen3-8B results.
- Official 420-case benchmark remains authoritative (`phase15_20260826T203744Z_dae9c3a4`).
- Official 420-case judge remains authoritative (`phase16_judge_20260828T152623Z_06661255`).
- **T=0.65** remains the locked research threshold.
- The UI 0.66 hundredths band is **not** a research threshold.
- V1 remains unchanged.

Phase 14 9-case and Phase 12 18-case runs are **engineering evidence only**.

---

## Document control

| Field | Value |
| --- | --- |
| Handover markdown | `V2/project_record/PROJECT_COMPLETE_HANDOVER.md` |
| Research artefacts modified while writing this file | **None** |
| Experiments rerun | **None** |
