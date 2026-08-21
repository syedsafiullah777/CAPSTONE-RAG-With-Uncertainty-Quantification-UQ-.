# V2 Phase 7 — Colab GPU smoke (Qwen3-8B)

This notebook is the **primary remote** entrypoint when Colab CLI is unavailable.

## Steps

1. Runtime → Change runtime type → **GPU**
2. Upload / mount this `V2/` project (Drive or zip)
3. Run the cells below

```python
# Optional: mount Drive if V2 lives there
# from google.colab import drive
# drive.mount('/content/drive')
# %cd /content/drive/MyDrive/path/to/V2
```

```python
import sys
from pathlib import Path
V2 = Path('.').resolve()
# If needed: V2 = Path('/content/V2')
sys.path.insert(0, str(V2))
%cd {V2}
```

```python
!pip -q install -r requirements.txt
# Prefer CUDA llama-cpp on Colab (install wheel matching CUDA if needed):
# !pip -q install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu122
```

```python
!PYTHONPATH=. python scripts/smoke_generate.py --backend llama_cpp
# Fallback:
# !PYTHONPATH=. python scripts/smoke_generate.py --backend transformers
```

Outputs:
- `results/config/phase7_runtime_fingerprint.json`
- `results/config/phase7_smoke_generate.json`

Do **not** use local Mac Ollama for the final 420-case benchmark. Ollama is optional for development smoke only.
