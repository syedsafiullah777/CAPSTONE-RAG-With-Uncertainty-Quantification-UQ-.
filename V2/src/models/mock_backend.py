"""Deterministic mock backend for unit tests (no model weights)."""

from __future__ import annotations

import time

from src.models.types import GenerationResult


class MockBackend:
    name = "mock"

    def __init__(self, canned: str = "MOCK_ANSWER") -> None:
        self.canned = canned

    def is_available(self) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.1,
        max_new_tokens: int = 512,
        top_p: float | None = None,
    ) -> GenerationResult:
        _ = top_p
        start = time.perf_counter()
        if "Support score" in prompt:
            text = "0.85"
        else:
            text = f"{self.canned} | prompt_chars={len(prompt)}"
        return GenerationResult(
            text=text,
            model="mock-qwen3-8b",
            backend=self.name,
            quantisation="none",
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            latency_seconds=time.perf_counter() - start,
            prompt_chars=len(prompt),
            finish_reason="stop",
            raw={},
        )
