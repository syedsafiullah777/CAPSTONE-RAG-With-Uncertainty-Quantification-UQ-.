"""llama.cpp GGUF backend for Colab GPU (primary remote path)."""

from __future__ import annotations

from pathlib import Path
import time
from typing import Any

from src.models.types import GenerationResult


class LlamaCppBackend:
    name = "llama_cpp"

    def __init__(
        self,
        *,
        model_path: str | None = None,
        hf_repo_id: str = "bartowski/Qwen_Qwen3-8B-GGUF",
        gguf_filename: str = "Qwen_Qwen3-8B-Q4_K_M.gguf",
        quantisation: str = "Q4_K_M",
        n_ctx: int = 4096,
        n_gpu_layers: int = -1,
        model_name: str = "Qwen3-8B",
    ) -> None:
        self.model_path = model_path
        self.hf_repo_id = hf_repo_id
        self.gguf_filename = gguf_filename
        self.quantisation = quantisation
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.model_name = model_name
        self._llm = None

    def is_available(self) -> bool:
        try:
            import llama_cpp  # noqa: F401
        except ImportError:
            return False
        if self.model_path and Path(self.model_path).exists():
            return True
        # Available as a backend implementation even if weights not downloaded yet.
        return True

    def _load(self) -> Any:
        if self._llm is not None:
            return self._llm
        from llama_cpp import Llama

        if self.model_path and Path(self.model_path).exists():
            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False,
            )
            return self._llm

        # Download from Hugging Face on first use (Colab-friendly).
        self._llm = Llama.from_pretrained(
            repo_id=self.hf_repo_id,
            filename=self.gguf_filename,
            n_ctx=self.n_ctx,
            n_gpu_layers=self.n_gpu_layers,
            verbose=False,
        )
        return self._llm

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.1,
        max_new_tokens: int = 512,
        top_p: float | None = None,
    ) -> GenerationResult:
        llm = self._load()
        start = time.perf_counter()
        kwargs: dict[str, Any] = {
            "prompt": prompt,
            "max_tokens": max_new_tokens,
            "temperature": temperature,
        }
        if top_p is not None:
            kwargs["top_p"] = top_p
        output = llm(**kwargs)
        latency = time.perf_counter() - start
        choice = (output.get("choices") or [{}])[0]
        text = str(choice.get("text") or "").strip()
        return GenerationResult(
            text=text,
            model=self.model_name,
            backend=self.name,
            quantisation=self.quantisation,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            latency_seconds=latency,
            prompt_chars=len(prompt),
            finish_reason=choice.get("finish_reason"),
            raw={"usage": output.get("usage")},
        )
