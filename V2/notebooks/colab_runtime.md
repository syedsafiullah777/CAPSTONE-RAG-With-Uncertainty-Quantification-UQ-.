# Colab Phase 7 smoke — instructions

Notebook: `notebooks/colab_phase7_smoke.ipynb`

## Workflow: GitHub → Colab (no Drive upload for code)

1. **Commit and push** your latest V2 changes to GitHub.
2. Open the notebook in Colab with **GPU** runtime.
3. Check **`REPO_URL`** and **`BRANCH`** in cell 1 (defaults point to your GitHub repo).
4. **Run all cells.**

The setup cell clones the repo to `/content/capstone-rag/` and uses `/content/capstone-rag/V2`.

## Default clone settings

```python
REPO_URL = 'https://github.com/syedsafiullah777/CAPSTONE--RAG-WITH-UNCERTAINITY-QUANTIFICATION-.git'
BRANCH = 'main'  # change if your work is on another branch
```

If smoke fails with “branch not found”, set `BRANCH` to the branch you pushed (e.g. `cursor/empty-v2-workspace`).

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

Run **section 5** in the notebook to copy JSON outputs to `My Drive/MSc-RAG/configs/phase7/` (Drive is for **results backup**, not for syncing source code).

## Before git commit

Colab: **Edit → Clear all outputs** before saving the notebook to avoid GitHub “invalid notebook” errors.
