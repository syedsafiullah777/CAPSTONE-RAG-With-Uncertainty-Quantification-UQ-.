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
from src.models.runtime_guard import LiveRuntimeError, mock_forbidden
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

KNOWN_GOOD_QUESTION_ID = "finqa_test_1000"
ADDITIONAL_NUMERICAL_QUESTION_ID = "finqa_test_1012"
THRESHOLD_NOT_LOCKED = "NOT LOCKED"
INSUFFICIENT_EVIDENCE_QUESTION = (
    "What was SpaceX's audited GAAP net income for fiscal year 2025, "
    "and how many Starship orbital launches did the company complete that year?"
)
INSUFFICIENT_EVIDENCE_QUESTION_ID = "live_insufficient_evidence"
FRESH_KB_QUESTION = (
    "According to Snap-on Incorporated's five-year stock performance graph, "
    "what was the cumulative total shareholder return on Snap-on's own common stock "
    "at December 31, 2013, if $100 was invested on December 31, 2008?"
)


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
    used_precomputed_benchmark_lookup: bool = False
    locked_threshold: float | None = None

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


def resolve_displayed_confidence(result: RAGCaseResult) -> float | None:
    """Expose the calculated UQ confidence. Never invent 0 for a missing value."""
    if result.architecture == ARCHITECTURE_MULTI_AGENT_UQ:
        uq = (result.configuration or {}).get("uncertainty_result") or {}
        if uq.get("confidence") is not None:
            return float(uq["confidence"])
        if result.confidence is not None:
            return float(result.confidence)
        return None
    return None if result.confidence is None else float(result.confidence)


def format_confidence_display(result: RAGCaseResult) -> str:
    value = resolve_displayed_confidence(result)
    if value is None:
        return "n/a"
    return f"{value:.4f}"


def format_threshold_display(result: RAGCaseResult) -> str:
    """Live artefact displays the official lock when threshold_source is locked."""
    if result.architecture != ARCHITECTURE_MULTI_AGENT_UQ:
        return "n/a"
    source = (result.configuration or {}).get("threshold_source")
    if source == "locked" and result.threshold is not None:
        return f"{float(result.threshold):.4f} (locked)"
    if result.threshold is None:
        return THRESHOLD_NOT_LOCKED
    return f"{float(result.threshold):.4f} (smoke/demo — {THRESHOLD_NOT_LOCKED})"


UI_ABSTAIN_LOW_CONFIDENCE = "ABSTAIN — Low confidence"
UI_MODERATE_CONFIDENCE_WARNING = "Moderate confidence — verify supporting evidence."
UI_CONFIDENCE_WARNING_NOTE = (
    "Warning is a user-facing confidence indicator and does not alter the research decision rule."
)


def _confidence_in_lock_hundredths(confidence: float, locked_t: float) -> bool:
    """True when confidence is still in the locked T hundredths band (e.g. 0.65 ≤ c < 0.66).

    UI proximity only. Not a second research threshold. Not written to the lock file.
    """
    return locked_t <= confidence < locked_t + 0.01


def uq_ui_confidence_overlay(result: RAGCaseResult) -> dict[str, Any]:
    """Streamlit-only UQ captions. Does not mutate decision, confidence, or stored results."""
    empty = {
        "show": False,
        "decision_heading": None,
        "warning": None,
        "note": None,
    }
    if result.architecture != ARCHITECTURE_MULTI_AGENT_UQ:
        return empty
    note = UI_CONFIDENCE_WARNING_NOTE
    confidence = resolve_displayed_confidence(result)
    if confidence is None:
        return {
            "show": True,
            "decision_heading": result.decision,
            "warning": None,
            "note": note,
        }
    heading = result.decision
    warning = None
    if result.decision == "ABSTAIN":
        heading = UI_ABSTAIN_LOW_CONFIDENCE
    elif result.decision == "ANSWER" and result.threshold is not None:
        locked_t = float(result.threshold)
        if confidence >= locked_t and _confidence_in_lock_hundredths(confidence, locked_t):
            warning = UI_MODERATE_CONFIDENCE_WARNING
    return {
        "show": True,
        "decision_heading": heading,
        "warning": warning,
        "note": note,
    }


def resolve_live_locked_threshold() -> float:
    """Official T from threshold.lock.json. Does not retune or read yaml smoke_threshold."""
    from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD, load_official_lock

    lock = load_official_lock()
    threshold = float(lock["threshold"])
    if abs(threshold - EXPECTED_LOCKED_THRESHOLD) > 1e-9:
        raise RuntimeError(
            f"Live artefact requires locked T={EXPECTED_LOCKED_THRESHOLD}, found {threshold}."
        )
    if lock.get("used_frozen_test_140") is True:
        raise RuntimeError("Lock claims the frozen 140 was used. Refusing live demo.")
    if str(lock.get("source_split") or "") != "dev":
        raise RuntimeError("Official lock must have source_split=dev.")
    return threshold


def annotate_live_uq_lock(result: RAGCaseResult, locked_t: float) -> RAGCaseResult:
    """Live-layer label only. Does not change retrieve/generate/verify internals."""
    result.threshold = float(locked_t)
    cfg = dict(result.configuration or {})
    cfg["threshold_source"] = "locked"
    cfg["threshold_locked"] = True
    cfg["threshold_note"] = "LOCKED T from results/config/threshold.lock.json (DEV 40 only)"
    result.configuration = cfg
    return result


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

    if result.architecture == ARCHITECTURE_MULTI_AGENT_UQ:
        uq = (result.configuration or {}).get("uncertainty_result") or {}
        if uq.get("confidence") is not None:
            result.confidence = float(uq["confidence"])
        elif result.confidence is None:
            result.decision = DECISION_UNAVAILABLE
            result.error = "UQ confidence could not be calculated; not a valid zero-confidence result."
            result.confidence = None

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
    """Run the three architectures independently on the same original question.

    Always applies locked T from threshold.lock.json. The ``threshold`` argument is
    ignored so the live artefact cannot silently fall back to smoke 0.55.
    """
    cfg = config or load_experiment_config()
    model_cfg = dict(cfg.section("model"))
    if mock_forbidden():
        backend_name = "llama_cpp"
        model_cfg["backend"] = "llama_cpp"
        if backend is not None and str(getattr(backend, "name", "")).lower() in {"mock", "test"}:
            raise LiveRuntimeError(
                "Mock backend is forbidden for this live demo. Use llama_cpp on Colab T4."
            )
    elif backend_name:
        model_cfg["backend"] = backend_name

    locked_t = resolve_live_locked_threshold()
    _ = threshold
    rid = run_id or create_run_id("phase20")
    qid = question_id or make_fresh_question_id(question)
    fp = fingerprint or collect_fingerprint(
        model_config=model_cfg,
        project_root=str(project_root()),
    )
    llm = backend or create_backend(model_cfg)
    backend_used = str(getattr(llm, "name", model_cfg.get("backend")))
    if mock_forbidden() and backend_used.lower() in {"mock", "test"}:
        raise LiveRuntimeError(
            "Mock backend is forbidden for this live demo. Use llama_cpp on Colab T4."
        )

    comparison = LiveComparison(
        run_id=rid,
        question=question,
        question_id=qid,
        question_source=question_source,
        backend=backend_used,
        fingerprint=fp,
        used_precomputed_benchmark_lookup=False,
        locked_threshold=locked_t,
    )

    runners = (
        (ARCHITECTURE_SINGLE_AGENT, run_single_agent, {}),
        (ARCHITECTURE_MULTI_AGENT, run_multi_agent, {}),
        (ARCHITECTURE_MULTI_AGENT_UQ, run_multi_agent_uq, {"threshold": locked_t}),
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
            case = normalize_live_case(runner(question, **kwargs))
            if architecture == ARCHITECTURE_MULTI_AGENT_UQ:
                case = annotate_live_uq_lock(case, locked_t)
            comparison.results[architecture] = case
    except Exception as exc:  # noqa: BLE001
        comparison.error = f"{type(exc).__name__}: {exc}"

    return comparison
