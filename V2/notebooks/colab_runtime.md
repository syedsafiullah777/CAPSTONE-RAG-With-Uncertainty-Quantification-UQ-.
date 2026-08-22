# Colab Phase 7 smoke — instructions

Notebook: `notebooks/colab_phase7_smoke.ipynb`

## Before Colab

1. Copy the whole **`V2/`** folder to **Google Drive** (My Drive).
   - Example: `My Drive/V2/` or `My Drive/CAPSTONE (...)/V2/`

2. Commit/push the notebook from GitHub is optional; you can also upload the `.ipynb` directly to Colab.

## In Google Colab

1. Open [Google Colab](https://colab.research.google.com)
2. **File → Open notebook** → GitHub or upload `colab_phase7_smoke.ipynb`
3. **Runtime → Change runtime type → T4 GPU (or any GPU) → Save**
4. Open the **Setup instructions** cell and read the steps
5. In **cell 1 (Mount Drive and set V2 path)** edit this line to match your Drive folder:

```python
V2_ROOT = Path('/content/drive/MyDrive/V2')  # <-- change this
```

### How to find the correct path

1. Run the cell once with a guess, **or** mount Drive in a scratch cell:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
2. In Colab’s **file browser** (left panel), expand **drive → MyDrive**
3. Navigate to your `V2` folder
4. Right-click **V2** → **Copy path**
5. Paste into `V2_ROOT` (must start with `/content/drive/MyDrive/...`)

6. Re-run the setup cell. You should see:
   ```text
   OK — V2_ROOT: /content/drive/MyDrive/...
   ```

7. **Run all remaining cells** (install deps → smoke test → check results)

## If Drive mount fails

- Use a normal browser window (not incognito)
- Allow popups for Colab
- Click the link in the mount output and sign in to Google
- Re-run the setup cell

## Success criteria

- `results/config/phase7_smoke_test.json` shows `"status": "PASS"`
- `results/config/phase7_runtime_fingerprint.json` shows Colab GPU / CUDA info

Then update `project_record/evidence/phase7_validation.md` with the Colab run result.

## Before git commit

In Colab: **Edit → Clear all outputs** before saving the notebook back to git (avoids GitHub “invalid notebook” errors).
