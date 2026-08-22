# Colab Phase 7 smoke — instructions

Notebook: `notebooks/colab_phase7_smoke.ipynb`

## Workflow: GitHub → Colab (no Drive upload for code)

1. **Commit and push** your latest V2 changes to GitHub.
2. Open the notebook in Colab with **GPU** runtime.
3. Check **`REPO_URL`** and **`BRANCH`** in cell 1 (defaults point to your GitHub repo).
4. **Run all cells.**

The setup cell clones the repo to `/content/capstone-rag/` and uses `/content/capstone-rag/V2`.

## GitHub repo layout

```text
CAPSTONE--RAG-WITH-UNCERTAINITY-QUANTIFICATION-/
├── .cursor/rules/          ← Cursor rules (not used in Colab)
└── V2/                     ← clone target for all Colab work
```

Branch: **`cursor/empty-v2-workspace`** (there is no `main` branch).

## Workflow

1. Push from Mac (repo root contains both `.cursor/` and `V2/`):
   ```bash
   git add V2/ .cursor/
   git commit -m "your message"
   git push origin cursor/empty-v2-workspace
   ```
2. Colab clones repo → enters **`V2/`** automatically
3. Run smoke cells

## Clone settings (in notebook)

```python
BRANCH = 'cursor/empty-v2-workspace'
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

Run **section 5** in the notebook to copy JSON outputs to `My Drive/MSc-RAG/configs/phase7/` (Drive is for **results backup**, not for syncing source code).

## Before git commit

Colab: **Edit → Clear all outputs** before saving the notebook to avoid GitHub “invalid notebook” errors.
