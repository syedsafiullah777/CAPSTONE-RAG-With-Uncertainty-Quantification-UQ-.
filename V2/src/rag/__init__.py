"""RAG architectures: single-agent, multi-agent, UQ/abstention, and live comparison."""

from src.rag.live import LiveComparison, run_live_comparison
from src.rag.multi_agent import run_multi_agent
from src.rag.multi_agent_uq import run_multi_agent_uq
from src.rag.schema import (
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
    ARCHITECTURE_SINGLE_AGENT,
    RAGCaseResult,
)
from src.rag.single_agent import run_single_agent

__all__ = [
    "ARCHITECTURE_MULTI_AGENT",
    "ARCHITECTURE_MULTI_AGENT_UQ",
    "ARCHITECTURE_SINGLE_AGENT",
    "LiveComparison",
    "RAGCaseResult",
    "run_live_comparison",
    "run_multi_agent",
    "run_multi_agent_uq",
    "run_single_agent",
]
