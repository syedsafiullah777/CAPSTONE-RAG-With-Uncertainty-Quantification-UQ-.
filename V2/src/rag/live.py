"""Live comparison runner: three independent RAG architectures on one question.

Uses the shared Phase 6 knowledge base and a single loaded LLM backend.
Does not chain answers across architectures.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.config import ExperimentConfig, get_path, load_experiment_config, project_root
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.models.types import LLMBackend
from src.rag.multi_agent import run_multi_agent
from src.rag.multi_agent_uq import run_multi_agent_uq
from src.rag.schema import (
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
    ARCHITECTURE_SINGLE_AGENT,
    RAGCaseResult,
)
from src.rag.single_agent import run_single_agent
from src.utils import create_run_id

LIVE_ARCHITECTURES: tuple[str, ...] = (
    ARCHITECTURE_SINGLE_AGENT,
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
)

ARCHITECTURE_LABELS = {
    ARCHITECTURE_SINGLE_AGENT: "Single-Agent RAG",
    ARCHITECTURE_MULTI_AGENT: "Multi-Agent RAG",
    ARCHITECTURE_MULTI_AGENT_UQ: "Uncertainty / Abstention RAG",
}

DECISION_ERROR = "ERROR"
DECISION_UNAVAILABLE = "UNAVAILABLE"
LIVE_FAILURE_DECISIONS = {DECISION_ERROR, DECISION_UNAVAILABLE}


@dataclass
class LiveComparison:
    """One live-artefact run: same question through three independent pipelines."""

    run_id: str
    question: str
    question_id: str
    question_source: str  # frozen | fresh
    backend: str | None
    results: dict[str, RAGCaseResult] = field(default_factory=dict)
    fingerprint: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["results"] = {key: result.to_dict() for key, result in self.results.items()}
        return payload


def format_optional(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def live_run_failed(result: RAGCaseResult) -> bool:
    """True when the live artefact must not treat the case as a successful RAG run."""
    if result.error:
        return True
    if not result.retrieved_evidence:
        return True
    if not (result.answer or "").strip():
        return True
    return False


def normalize_live_case(result: RAGCaseResult) -> RAGCaseResult:
    """Live-app only: map failed retrieval/generation to ERROR/UNAVAILABLE.

    Does not change the Phase 8–10 pipeline modules. Clears fabricated answers
    and confidence when evidence is missing or generation failed.
    """
    if result.error:
        result.decision = DECISION_ERROR
        result.answer = ""
        result.confidence = None
        result.verification_result = None
        if result.configuration:
            result.configuration = dict(result.configuration)
            result.configuration.pop("uncertainty_result", None)
            result.configuration.pop("draft_answer", None)
        return result

    if not result.retrieved_evidence:
        result.decision = DECISION_UNAVAILABLE
        result.error = "No evidence retrieved; not a successful RAG run."
        result.answer = ""
        result.confidence = None
        result.verification_result = None
        if result.configuration:
            result.configuration = dict(result.configuration)
            result.configuration.pop("uncertainty_result", None)
            result.configuration.pop("draft_answer", None)
        return result

    if not (result.answer or "").strip():
        result.decision = DECISION_UNAVAILABLE
        result.error = "Generation returned empty text; not a successful RAG run."
        result.confidence = None
        result.verification_result = None
        return result

    return result


def make_fresh_question_id(question: str) -> str:
    digest = hashlib.sha256(question.strip().encode("utf-8")).hexdigest()[:10]
    return f"live_fresh_{digest}"


def load_frozen_questions(limit: int | None = None) -> list[dict[str, str]]:
    """Read the frozen 140-question CSV (read-only; does not modify it)."""
    csv_path = get_path(load_experiment_config(), "data_final") / "selected_140_questions.csv"
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "id": str(row.get("id") or ""),
                    "question": str(row.get("question") or ""),
                    "program_answer": str(row.get("program_answer") or ""),
                }
            )
            if limit is not None and len(rows) >= limit:
                break
    return rows


def run_live_comparison(
    question: str,
    *,
    question_id: str | None = None,
    question_source: str = "fresh",
    reference_answer: str | None = None,
    config: ExperimentConfig | None = None,
    backend: LLMBackend | None = None,
    backend_name: str | None = None,
    run_id: str | None = None,
    fingerprint: dict[str, Any] | None = None,
    threshold: float | None = None,
) -> LiveComparison:
    """Run the three architectures independently on the same original question."""
    cfg = config or load_experiment_config()
    model_cfg = dict(cfg.section("model"))
    if backend_name:
        model_cfg["backend"] = backend_name

    rid = run_id or create_run_id("phase11")
    qid = question_id or make_fresh_question_id(question)
    fp = fingerprint or collect_fingerprint(
        model_config=model_cfg,
        project_root=str(project_root()),
    )
    llm = backend or create_backend(model_cfg)
    backend_used = str(getattr(llm, "name", model_cfg.get("backend")))

    comparison = LiveComparison(
        run_id=rid,
        question=question,
        question_id=qid,
        question_source=question_source,
        backend=backend_used,
        fingerprint=fp,
    )

    runners = (
        (ARCHITECTURE_SINGLE_AGENT, run_single_agent, {}),
        (ARCHITECTURE_MULTI_AGENT, run_multi_agent, {}),
        (ARCHITECTURE_MULTI_AGENT_UQ, run_multi_agent_uq, {"threshold": threshold}),
    )

    try:
        for architecture, runner, extra in runners:
            kwargs: dict[str, Any] = {
                "question_id": qid,
                "reference_answer": reference_answer,
                "config": cfg,
                "backend": llm,
                "backend_name": backend_name,
                "run_id": rid,
                "fingerprint": fp,
            }
            kwargs.update(extra)
            comparison.results[architecture] = normalize_live_case(runner(question, **kwargs))
    except Exception as exc:  # noqa: BLE001
        comparison.error = f"{type(exc).__name__}: {exc}"

    return comparison
