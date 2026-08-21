"""LLM generation result and backend protocol."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass
class GenerationResult:
    text: str
    model: str
    backend: str
    quantisation: str | None
    temperature: float
    max_new_tokens: int
    latency_seconds: float
    prompt_chars: int
    finish_reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LLMBackend(Protocol):
    name: str

    def is_available(self) -> bool:
        ...

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.1,
        max_new_tokens: int = 512,
        top_p: float | None = None,
    ) -> GenerationResult:
        ...
