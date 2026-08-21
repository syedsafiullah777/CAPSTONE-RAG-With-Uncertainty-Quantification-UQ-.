"""Factory for selecting an LLM backend from experiment config."""

from __future__ import annotations

from typing import Any

from src.models.llama_cpp_backend import LlamaCppBackend
from src.models.mock_backend import MockBackend
from src.models.ollama_backend import OllamaBackend
from src.models.transformers_backend import TransformersBackend
from src.models.types import LLMBackend


def create_backend(model_cfg: dict[str, Any] | None = None) -> LLMBackend:
    """Create a backend.

    Preferred Colab order when ``backend: auto``:
    1. llama_cpp (GGUF) if importable
    2. transformers if importable
    3. ollama_dev if a local model is present (dev only)
    """
    cfg = dict(model_cfg or {})
    backend = str(cfg.get("backend") or "auto").lower()

    if backend in {"mock", "test"}:
        return MockBackend()

    if backend in {"ollama", "ollama_dev"}:
        return OllamaBackend(model=str(cfg.get("ollama_model") or "qwen3:8b"))

    if backend in {"llama_cpp", "llamacpp", "gguf", "colab"}:
        return LlamaCppBackend(
            model_path=cfg.get("model_path"),
            hf_repo_id=str(cfg.get("hf_repo_id") or "bartowski/Qwen_Qwen3-8B-GGUF"),
            gguf_filename=str(cfg.get("gguf_filename") or "Qwen3-8B-Q4_K_M.gguf"),
            quantisation=str(cfg.get("quantisation") or "Q4_K_M"),
            n_ctx=int(cfg.get("n_ctx") or 4096),
            n_gpu_layers=int(cfg.get("n_gpu_layers") if cfg.get("n_gpu_layers") is not None else -1),
            model_name=str(cfg.get("name") or "Qwen3-8B"),
        )

    if backend in {"transformers", "hf", "huggingface"}:
        return TransformersBackend(
            model_id=str(cfg.get("hf_model_id") or "Qwen/Qwen3-8B"),
            quantisation=str(cfg.get("quantisation") or "bitsandbytes-4bit"),
            load_in_4bit=bool(cfg.get("load_in_4bit", True)),
        )

    if backend == "auto":
        llama = LlamaCppBackend(
            model_path=cfg.get("model_path"),
            hf_repo_id=str(cfg.get("hf_repo_id") or "bartowski/Qwen_Qwen3-8B-GGUF"),
            gguf_filename=str(cfg.get("gguf_filename") or "Qwen3-8B-Q4_K_M.gguf"),
            quantisation=str(cfg.get("quantisation") or "Q4_K_M"),
            model_name=str(cfg.get("name") or "Qwen3-8B"),
        )
        try:
            import llama_cpp  # noqa: F401

            return llama
        except ImportError:
            pass

        transformers = TransformersBackend(
            model_id=str(cfg.get("hf_model_id") or "Qwen/Qwen3-8B"),
        )
        if transformers.is_available():
            # Prefer transformers only when CUDA is present for 8B practicality.
            try:
                import torch

                if torch.cuda.is_available():
                    return transformers
            except Exception:
                pass

        ollama = OllamaBackend(model=str(cfg.get("ollama_model") or "qwen3:8b"))
        if ollama.is_available():
            return ollama

        raise RuntimeError(
            "No LLM backend available. On Colab install llama-cpp-python (CUDA) or "
            "transformers+bitsandbytes. For local smoke only, install/start Ollama with qwen3:8b."
        )

    raise ValueError(f"Unknown model backend: {backend}")
