"""RAG architectures: single-agent (Phase 8), multi-agent (Phase 9), UQ in Phase 10."""

from src.rag.multi_agent import run_multi_agent
from src.rag.schema import (
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_SINGLE_AGENT,
    RAGCaseResult,
)
from src.rag.single_agent import run_single_agent

__all__ = [
    "ARCHITECTURE_MULTI_AGENT",
    "ARCHITECTURE_SINGLE_AGENT",
    "RAGCaseResult",
    "run_multi_agent",
    "run_single_agent",
]
