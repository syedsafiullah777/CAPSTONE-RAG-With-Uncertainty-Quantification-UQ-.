"""Runtime fingerprint for reproducibility (device, packages, model config)."""

from __future__ import annotations

from datetime import datetime, timezone
import platform
import subprocess
from typing import Any


def _safe_import_version(module_name: str) -> str | None:
    try:
        mod = __import__(module_name)
        return getattr(mod, "__version__", None)
    except Exception:
        return None


def _nvidia_smi() -> dict[str, Any]:
    info: dict[str, Any] = {"available": False}
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free,driver_version",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
        if out:
            # Take first GPU line.
            line = out.splitlines()[0]
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 4:
                info = {
                    "available": True,
                    "name": parts[0],
                    "vram_total_mb": float(parts[1]),
                    "vram_free_mb": float(parts[2]),
                    "driver_version": parts[3],
                }
    except Exception:
        pass
    return info


def _torch_info() -> dict[str, Any]:
    info: dict[str, Any] = {"installed": False}
    try:
        import torch

        info = {
            "installed": True,
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            info["vram_total_gb"] = round(props.total_memory / (1024**3), 2)
    except Exception as exc:  # noqa: BLE001
        info["error"] = str(exc)
    return info


def _git_commit(cwd: str | None = None) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
    except Exception:
        return None


def collect_fingerprint(
    *,
    model_config: dict[str, Any] | None = None,
    project_root: str | None = None,
) -> dict[str, Any]:
    """Collect runtime/environment fingerprint for experiment logging."""
    model_config = model_config or {}
    gpu = _nvidia_smi()
    torch_info = _torch_info()

    device = "cpu"
    if gpu.get("available"):
        device = "cuda"
    elif torch_info.get("cuda_available"):
        device = "cuda"
    elif platform.system() == "Darwin" and "arm" in platform.machine().lower():
        device = "mps_capable_host"  # not necessarily used for inference

    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        },
        "cpu": {
            "count_logical": __import__("os").cpu_count(),
        },
        "device": device,
        "gpu": gpu,
        "torch": torch_info,
        "packages": {
            "transformers": _safe_import_version("transformers"),
            "llama_cpp": _safe_import_version("llama_cpp"),
            "accelerate": _safe_import_version("accelerate"),
            "sentence_transformers": _safe_import_version("sentence_transformers"),
            "chromadb": _safe_import_version("chromadb"),
            "datasets": _safe_import_version("datasets"),
        },
        "model_config": {
            "name": model_config.get("name"),
            "backend": model_config.get("backend"),
            "quantisation": model_config.get("quantisation"),
            "model_path": model_config.get("model_path"),
            "hf_repo_id": model_config.get("hf_repo_id"),
            "gguf_filename": model_config.get("gguf_filename"),
            "ollama_model": model_config.get("ollama_model"),
            "temperature": model_config.get("temperature"),
            "max_new_tokens": model_config.get("max_new_tokens"),
        },
        "git_commit": _git_commit(project_root),
    }
