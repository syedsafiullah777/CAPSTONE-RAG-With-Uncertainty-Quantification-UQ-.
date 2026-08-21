"""LLM backends for V2 (Colab Qwen3-8B primary; optional Ollama for local smoke)."""

from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.models.types import GenerationResult

__all__ = ["GenerationResult", "collect_fingerprint", "create_backend"]
