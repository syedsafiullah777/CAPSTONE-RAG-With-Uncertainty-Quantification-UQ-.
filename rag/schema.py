from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    source: str
    page: int | str
    text: str
    score: float | None = None


@dataclass
class RAGResult:
    system_name: str
    answer: str
    confidence: float | None
    decision: str
    retrieved_chunks: list[RetrievedChunk]
    response_time: float
    retrieval_score: float | None = None
    verification_score: float | None = None
    consistency_score: float | None = None
    hallucination_risk: str = "Unknown"
