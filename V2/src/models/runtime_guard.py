"""Guards for the Colab Streamlit live demo. Does not change RAG pipelines."""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any

from src.config import get_path, load_experiment_config, project_root
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import validate_index_preflight


class LiveRuntimeError(RuntimeError):
    """Raised when the live demo is not on Colab CUDA + llama_cpp."""


def mock_forbidden() -> bool:
    return os.environ.get("V2_FORBID_MOCK", "").strip() == "1" or (
        os.environ.get("V2_LIVE_BACKEND", "").strip().lower() == "llama_cpp"
    )


def assert_not_mock_backend(backend_name: str | None) -> None:
    name = str(backend_name or "").lower()
    if mock_forbidden() and name in {"mock", "test"}:
        raise LiveRuntimeError(
            "Mock backend is forbidden for this live demo. Use llama_cpp on Colab T4."
        )


def verify_live_llama_cpp_runtime(*, require_cuda: bool = True) -> dict[str, Any]:
    """Verify this process is a real Colab-style GPU + llama_cpp runtime.

    Refuses macOS/MPS, empty KB, missing llama_cpp, and missing GGUF.
    Never selects mock.
    """
    if platform.system() == "Darwin":
        raise LiveRuntimeError(
            "This process is running on macOS (device would be mps_capable_host), "
            "not the Colab T4 runtime. Open notebooks/colab_phase11_live.ipynb on Colab GPU "
            "and use the printed trycloudflare URL. Do not run Streamlit on the Mac for this demo."
        )

    gpu_name = None
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        raise LiveRuntimeError(f"PyTorch is required for the Colab live demo: {exc}") from exc

    if require_cuda:
        if not torch.cuda.is_available():
            raise LiveRuntimeError(
                "CUDA is not available. Runtime → Change runtime type → GPU (T4). "
                "Refusing to start Streamlit (no mock fallback)."
            )
        gpu_name = torch.cuda.get_device_name(0)

    try:
        import llama_cpp  # noqa: F401
    except ImportError as exc:
        raise LiveRuntimeError(
            "llama_cpp is not installed in this runtime. Install the CUDA wheel. "
            "Refusing mock fallback."
        ) from exc

    config = load_experiment_config()
    model_cfg = config.section("model")
    hf_repo_id = str(model_cfg.get("hf_repo_id") or "bartowski/Qwen_Qwen3-8B-GGUF")
    gguf_filename = str(model_cfg.get("gguf_filename") or "Qwen_Qwen3-8B-Q4_K_M.gguf")
    local_path = model_cfg.get("model_path")
    gguf_path: str | None = None
    if local_path and Path(str(local_path)).is_file():
        gguf_path = str(Path(str(local_path)).resolve())
    else:
        try:
            from huggingface_hub import hf_hub_download

            gguf_path = hf_hub_download(repo_id=hf_repo_id, filename=gguf_filename)
        except Exception as exc:  # noqa: BLE001
            raise LiveRuntimeError(
                f"Qwen3-8B GGUF is not available ({hf_repo_id}/{gguf_filename}): {exc}"
            ) from exc

    if not gguf_path or not Path(gguf_path).is_file():
        raise LiveRuntimeError(f"GGUF file missing after download check: {gguf_path}")

    retrieval_cfg = config.section("retrieval")
    index_dir = get_path(config, "kb_index")
    manifest = (
        project_root() / str(retrieval_cfg.get("index_manifest") or "knowledge_base/index/index_manifest.json")
    ).resolve()
    preflight = validate_index_preflight(
        index_dir,
        manifest_path=manifest,
        collection_name=str(retrieval_cfg.get("collection_name") or COLLECTION_NAME),
    )
    if int(preflight.get("actual_count") or 0) <= 0:
        raise LiveRuntimeError("Chroma index is empty. Restore the Phase 8 KB before the live demo.")

    return {
        "backend": "llama_cpp",
        "device": "cuda" if require_cuda else "cpu",
        "gpu": gpu_name,
        "gguf_path": gguf_path,
        "hf_repo_id": hf_repo_id,
        "gguf_filename": gguf_filename,
        "index_chunks": preflight.get("actual_count"),
        "mock_forbidden": True,
        "platform": platform.system(),
    }
