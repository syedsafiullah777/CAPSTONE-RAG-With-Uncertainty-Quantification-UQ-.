# Colab GPU notebooks — instructions

## Phase 7 — model smoke only

Notebook: `notebooks/colab_phase7_smoke.ipynb`

Verifies Qwen3-8B `llama_cpp` generation on Colab GPU. Does **not** build the knowledge base.

## Phase 8 — Single-Agent RAG smoke (recommended)

Notebook: `notebooks/colab_phase8_smoke.ipynb`

Includes **Option B** retrieval fix:

1. Clone V2 from GitHub
2. Install dependencies
3. Run `scripts/build_index.py --distractors 50` — downloads FinQA source PDFs from Hugging Face and rebuilds Chroma on Colab (does **not** copy the Mac database)
4. Run `scripts/validate_kb_index.py` — preflight: manifest chunk count vs `collection.count()`
5. Run `scripts/smoke_single_agent.py --backend llama_cpp --limit 3`

Success: `results/config/phase8_smoke_test.json` → `"status": "PASS"` and each case has `n_evidence=4`.

## Phase 9 — Multi-Agent RAG smoke

Notebook: `notebooks/colab_phase9_smoke.ipynb`

1. Clone → install → restore KB from Drive (or rebuild)
2. Preflight → `smoke_multi_agent.py --backend llama_cpp --limit 3`
3. Save to `MyDrive/MSc-RAG/configs/phase9/`

## Phase 10 — Multi-Agent + UQ / abstention smoke

Notebook: `notebooks/colab_phase10_smoke.ipynb`

1. Clone → install → restore KB from Drive (or rebuild)
2. Preflight → `smoke_multi_agent_uq.py --backend llama_cpp --limit 3`
3. Save to `MyDrive/MSc-RAG/configs/phase10/`

Uses `uncertainty.smoke_threshold` (0.55) for verification only — not the locked benchmark threshold.

## Phase 11 — Live artefact (`llama_cpp`, one fresh question)

Notebook: `notebooks/colab_phase11_live.ipynb`

1. Clone → install → restore KB from Drive (or rebuild)
2. Preflight → `smoke_live_artefact.py --backend llama_cpp --fresh-only`
3. Save to `MyDrive/MSc-RAG/configs/phase11/`

Uses the same `run_live_comparison()` as Streamlit. Does **not** run the 140-question benchmark.

Manual browser demo (sections 8–10): starts `app/streamlit_app.py` with `V2_LIVE_BACKEND=llama_cpp` and prints a temporary `*.trycloudflare.com` URL. Do not use mock. Run section 10 only after the manual test.

## Phase 14 — 9-case benchmark validation (`llama_cpp`, T=0.65 locked)

Notebook: `notebooks/colab_phase14_benchmark_validation.ipynb`

1. Clone → install → restore KB from Drive (or rebuild) → restore `threshold.lock.json` if needed
2. Preflight → `run_benchmark.py --backend llama_cpp --n-questions 3`
3. Incremental Drive sync via `V2_DRIVE_ROOT=/content/drive/MyDrive/MSc-RAG`
4. Save to `MyDrive/MSc-RAG/results/raw/phase14_benchmark/` and `configs/phase14/`

Uses locked T=0.65. Does **not** launch the 420-case benchmark. Resume with `--resume-latest`. Keep this notebook as engineering evidence; do not re-run it instead of Phase 15.

## Phase 15 — Final 420-case benchmark (`llama_cpp`, T=0.65 locked)

Notebook: `notebooks/colab_phase15_full_benchmark.ipynb`

1. Clone → install → restore KB from Drive (or rebuild) → restore `threshold.lock.json` if needed
2. Preflight → lock check T=0.65 → `run_full_benchmark.py --backend llama_cpp`
3. Incremental Drive sync via `V2_DRIVE_ROOT=/content/drive/MyDrive/MSc-RAG`
4. If interrupted: `--resume-latest` (do not start from question 1)
5. Save to `MyDrive/MSc-RAG/results/raw/phase15_benchmark/` and `configs/phase15/`

Official evaluation: **140 × 3 = 420** cases. Mock refused. Do not re-run the Phase 14 9-case notebook instead of this job.

---

## Workflow: GitHub → Colab (no Drive upload for code)

1. **Commit and push** your latest V2 changes to GitHub.
2. Open the notebook in Colab with **GPU** runtime.
3. Check **`REPO_URL`** and **`BRANCH`** in cell 1 (defaults point to your GitHub repo).
4. **Run all cells.**

The setup cell clones the repo to `/content/capstone-rag/` and uses `/content/capstone-rag/V2`.

## GitHub repo layout

```text
repository-root/
└── V2/                     ← clone target for all Colab work
```

Current submission branch: **`main`**. Historical Colab clones used a previous development workspace (legacy launch configuration).

## Workflow

1. Push V2 source from the repository root:
   ```bash
   git add V2/
   git commit -m "your message"
   git push
   ```
2. Colab clones the repo → enters **`V2/`** automatically
3. Run smoke cells

These Phase 7–10, 12, and 14 notebooks are **historical engineering / smoke / pilot / 9-case validation** artefacts. They are **not** the official 420-case evaluation. Official evaluation: Phase 15 (benchmark) and Phase 16 (judge).

## Clone settings (in notebook)

```python
BRANCH = 'main'
V2_ROOT = /content/capstone-rag/V2
```

## Private repo

If the repo is private, use a GitHub personal access token:

```python
REPO_URL = 'https://<TOKEN>@github.com/syedsafiullah777/CAPSTONE--RAG-WITH-UNCERTAINITY-QUANTIFICATION-.git'
```

Do not commit tokens to git.

## Success

- `results/config/phase7_smoke_test.json` → `"status": "PASS"`
- `results/config/phase7_runtime_fingerprint.json` → GPU/CUDA details

Update `project_record/evidence/phase7_validation.md` with the Colab result.

## Optional: save results to Drive

- Phase 7: section 5 in `colab_phase7_smoke.ipynb` → `My Drive/MSc-RAG/configs/phase7/`
- Phase 8: section 7 in `colab_phase8_smoke.ipynb` → `My Drive/MSc-RAG/configs/phase8/`

Drive is for **results backup**, not for syncing source code or the Chroma index.

## Phase 16 — post-hoc LLM-as-judge (no RAG rerun)

Notebook: `notebooks/colab_phase16_judge.ipynb`

Scores frozen Phase 15 `cases.jsonl` only. Metric: **LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)** — not official RAGAS.

```bash
PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp
PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp --resume-latest
```

Drive: `MyDrive/MSc-RAG/results/raw/phase16_judge/`

## Before git commit

Colab: **Edit → Clear all outputs** before saving the notebook to avoid GitHub “invalid notebook” errors.
