"""RAG architectures: baseline (Phase 8); multi-agent / UQ in later phases."""

from src.rag.schema import ARCHITECTURE_SINGLE_AGENT, RAGCaseResult
from src.rag.single_agent import run_single_agent

__all__ = [
    "ARCHITECTURE_SINGLE_AGENT",
    "RAGCaseResult",
    "run_single_agent",
]
