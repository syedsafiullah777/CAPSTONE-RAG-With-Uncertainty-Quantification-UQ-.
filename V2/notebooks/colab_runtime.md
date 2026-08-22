# V2 Phase 7 — Google Colab GPU notebook (primary remote path)

**Remote strategy:** standard Google Colab notebooks with a GPU runtime.  
**Not used:** Colab CLI / `gcloud` / remote Colab CLI sessions.

## Primary notebook

`notebooks/colab_phase7_smoke.ipynb`

## Setup cell options

| Option | Default | Purpose |
| --- | --- | --- |
| `MOUNT_DRIVE` | `True` | Mount Google Drive, then auto-search MyDrive for V2 |
| `MANUAL_V2_ROOT` | `""` | Force exact path if you already know it |
| `ALLOW_ZIP_UPLOAD` | `False` | Optional last-resort zip upload |

Auto-detect looks for folders that contain both:

- `config/experiment.yaml`
- `scripts/smoke_generate.py`

**Recommended:** copy/sync the `V2` folder (or whole CAPSTONE project) into Google Drive → open the notebook → run the setup cell with `MOUNT_DRIVE = True`.

## Steps

1. Runtime → **GPU**
2. Run setup cell (Drive mount + auto-detect)
3. Install deps + smoke generate

## Expected outputs

- `results/config/phase7_runtime_fingerprint.json`
- `results/config/phase7_smoke_generate.json`

## Next validation step

**Colab GPU verification (NEEDS VERIFICATION)** via this notebook.
