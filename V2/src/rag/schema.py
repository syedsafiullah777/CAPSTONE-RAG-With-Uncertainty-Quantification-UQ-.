"""Common RAG case-result schema aligned with storage.raw_result_fields."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

ARCHITECTURE_SINGLE_AGENT = "single_agent"
ARCHITECTURE_MULTI_AGENT = "multi_agent"
ARCHITECTURE_MULTI_AGENT_UQ = "multi_agent_uq"


@dataclass
class RAGCaseResult:
    """One architecture–question evaluation record (raw, before aggregation)."""

    run_id: str
    question_id: str
    architecture: str
    question: str
    retrieved_evidence: list[dict[str, Any]]
    retrieval_scores: list[float]
    answer: str
    reference_answer: str | None = None
    verification_result: Any = None  # Phase 9+
    confidence: float | None = None  # Phase 10+
    threshold: float | None = None  # Phase 10+
    decision: str = "ANSWER"  # baseline always answers; abstention is Phase 10
    latency_seconds: float = 0.0
    model: str | None = None
    model_version: str | None = None
    quantisation: str | None = None
    device: str | None = None
    gpu: str | None = None
    configuration: dict[str, Any] = field(default_factory=dict)
    random_seed: int | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: str | None = None
    # Extra provenance (allowed beyond minimal field list)
    retrieval_top_k: int | None = None
    backend: str | None = None
    prompt_chars: int | None = None
    case_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def case_id(self) -> str:
        return self.case_key or f"{self.architecture}:{self.question_id}"
