"""Optional local Ollama backend (development / smoke only — not required for Colab benchmark)."""

from __future__ import annotations

import time
from typing import Any

from src.models.types import GenerationResult


class OllamaBackend:
    name = "ollama_dev"

    def __init__(self, model: str = "qwen3:8b") -> None:
        self.model = model

    def is_available(self) -> bool:
        try:
            import ollama
        except ImportError:
            return False
        try:
            listed = ollama.list()
            models = listed.get("models", []) if isinstance(listed, dict) else getattr(listed, "models", [])
            names: list[str] = []
            for item in models:
                if isinstance(item, dict):
                    names.append(str(item.get("model") or item.get("name") or ""))
                else:
                    names.append(str(getattr(item, "model", None) or getattr(item, "name", None) or ""))
            return any(n == self.model or n.startswith(self.model) for n in names if n)
        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.1,
        max_new_tokens: int = 512,
        top_p: float | None = None,
    ) -> GenerationResult:
        import ollama

        options: dict[str, Any] = {
            "temperature": temperature,
            "num_predict": max_new_tokens,
        }
        if top_p is not None:
            options["top_p"] = top_p

        start = time.perf_counter()
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "options": options,
        }
        # Qwen3 via Ollama may return empty content when "thinking" mode is on.
        try:
            response = ollama.chat(**kwargs, think=False)
        except TypeError:
            response = ollama.chat(**kwargs)
        latency = time.perf_counter() - start
        if isinstance(response, dict):
            text = str(response.get("message", {}).get("content", "")).strip()
            raw_meta = {"ollama_keys": list(response.keys())}
        else:
            message = getattr(response, "message", None)
            text = str(getattr(message, "content", "") or "").strip()
            raw_meta = {"ollama_type": type(response).__name__}
        return GenerationResult(
            text=text,
            model=self.model,
            backend=self.name,
            quantisation="ollama_bundled",
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            latency_seconds=latency,
            prompt_chars=len(prompt),
            finish_reason="stop",
            raw=raw_meta,
        )
