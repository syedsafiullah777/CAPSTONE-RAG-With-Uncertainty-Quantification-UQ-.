"""Phase 11 tests: live comparison runner + Streamlit app helpers."""

from __future__ import annotations

import json
from unittest.mock import patch

from src.config import load_experiment_config, project_root
from src.models.mock_backend import MockBackend
from src.rag.live import (
    ARCHITECTURE_LABELS,
    DECISION_ERROR,
    DECISION_UNAVAILABLE,
    INSUFFICIENT_EVIDENCE_QUESTION,
    INSUFFICIENT_EVIDENCE_QUESTION_ID,
    LIVE_ARCHITECTURES,
    THRESHOLD_NOT_LOCKED,
    format_confidence_display,
    format_threshold_display,
    load_frozen_questions,
    make_fresh_question_id,
    normalize_live_case,
    resolve_displayed_confidence,
    run_live_comparison,
)
from src.rag.schema import (
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
    ARCHITECTURE_SINGLE_AGENT,
    RAGCaseResult,
)
from src.retrieval.retriever import RetrievedChunk


def _sample_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="c1",
        text="Interest expense, net for 2018 was $270.4 million and for 2017 was $267.8 million.",
        score=0.91,
        doc_id="d1",
        file_name="pdf/NCLH/2018/page_97.pdf",
        split="test",
        page=1,
        company_symbol="NCLH",
        report_year="2018",
        role="test",
        context_id="finqa_test_ctx_231",
        source_type="pdf",
    )


def test_frozen_loader_does_not_alter_file() -> None:
    rows = load_frozen_questions(limit=3)
    assert len(rows) == 3
    assert rows[0]["id"] == "finqa_test_1000"
    assert rows[0]["question"]
    csv_path = project_root() / "data" / "final" / "selected_140_questions.csv"
    assert csv_path.is_file()


def test_fresh_question_id_is_stable() -> None:
    assert make_fresh_question_id("What is ROI?") == make_fresh_question_id("What is ROI?")
    assert make_fresh_question_id("What is ROI?").startswith("live_fresh_")


def test_live_comparison_runs_three_architectures_independently() -> None:
    chunk = _sample_chunk()
    original = "What was the percentage change in net interest expense?"
    seen: list[str] = []

    def _retrieve(question: str, **_kwargs):
        seen.append(question)
        return [chunk]

    backend = MockBackend(canned="Approximately 0.97% increase.")
    with (
        patch("src.rag.single_agent.retrieve", side_effect=_retrieve),
        patch("src.rag.multi_agent.retrieve", side_effect=_retrieve),
        patch("src.rag.multi_agent_uq.retrieve", side_effect=_retrieve),
    ):
        comparison = run_live_comparison(
            original,
            question_id="finqa_test_1012",
            question_source="frozen",
            reference_answer="0.0097",
            backend=backend,
            backend_name="mock",
            run_id="phase11_test",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
        )

    assert comparison.error is None
    assert set(comparison.results) == set(LIVE_ARCHITECTURES)
    assert seen == [original, original, original]
    assert comparison.results[ARCHITECTURE_SINGLE_AGENT].architecture == ARCHITECTURE_SINGLE_AGENT
    assert comparison.results[ARCHITECTURE_MULTI_AGENT].verification_result is not None
    uq = comparison.results[ARCHITECTURE_MULTI_AGENT_UQ]
    assert uq.decision in {"ANSWER", "ABSTAIN"}
    assert uq.threshold is not None
    assert uq.confidence is not None
    for result in comparison.results.values():
        assert result.question == original
        assert result.answer
        assert result.retrieved_evidence
        assert result.error is None


def test_live_comparison_accepts_fresh_question() -> None:
    chunk = _sample_chunk()
    question = "What was Norwegian Cruise Line interest expense in 2018?"

    with (
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        comparison = run_live_comparison(
            question,
            question_source="fresh",
            backend=MockBackend(canned="270.4 million"),
            backend_name="mock",
            run_id="phase11_fresh",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
        )

    assert comparison.question_source == "fresh"
    assert comparison.question_id.startswith("live_fresh_")
    assert ARCHITECTURE_SINGLE_AGENT in comparison.results
    payload = comparison.to_dict()
    fields = load_experiment_config().section("storage").get("raw_result_fields", [])
    for architecture in LIVE_ARCHITECTURES:
        for key in fields:
            assert key in payload["results"][architecture]


def test_empty_evidence_is_unavailable_not_answer() -> None:
    with (
        patch("src.rag.single_agent.retrieve", return_value=[]),
        patch("src.rag.multi_agent.retrieve", return_value=[]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[]),
    ):
        comparison = run_live_comparison(
            "What is the return on the S&P 500?",
            question_source="fresh",
            backend=MockBackend(canned="Fabricated mock answer"),
            backend_name="mock",
            run_id="phase11_empty",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
        )

    for result in comparison.results.values():
        assert result.decision == DECISION_UNAVAILABLE
        assert result.decision != "ANSWER"
        assert result.answer == ""
        assert result.confidence is None
        assert result.verification_result is None
        assert result.error
        assert "No evidence retrieved" in result.error


def test_retrieval_exception_is_error_not_answer() -> None:
    def _boom(*_args, **_kwargs):
        raise RuntimeError("ProxyError: 403 Forbidden")

    with (
        patch("src.rag.single_agent.retrieve", side_effect=_boom),
        patch("src.rag.multi_agent.retrieve", side_effect=_boom),
        patch("src.rag.multi_agent_uq.retrieve", side_effect=_boom),
    ):
        comparison = run_live_comparison(
            "What is the return on the S&P 500?",
            question_source="fresh",
            backend=MockBackend(canned="Fabricated mock answer"),
            backend_name="mock",
            run_id="phase11_proxy",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
        )

    for result in comparison.results.values():
        assert result.decision == DECISION_ERROR
        assert result.decision != "ANSWER"
        assert result.answer == ""
        assert result.confidence is None
        assert "ProxyError: 403 Forbidden" in (result.error or "")


def test_normalize_live_case_clears_fabricated_success() -> None:
    from src.rag.schema import RAGCaseResult

    result = RAGCaseResult(
        run_id="r",
        question_id="q",
        architecture=ARCHITECTURE_SINGLE_AGENT,
        question="Q?",
        retrieved_evidence=[],
        retrieval_scores=[],
        answer="Fabricated",
        confidence=0.9,
        decision="ANSWER",
        error=None,
    )
    normalized = normalize_live_case(result)
    assert normalized.decision == DECISION_UNAVAILABLE
    assert normalized.answer == ""
    assert normalized.confidence is None


def test_architecture_labels_cover_all_three() -> None:
    assert set(ARCHITECTURE_LABELS) == set(LIVE_ARCHITECTURES)


def test_insufficient_evidence_question_is_not_in_frozen_set() -> None:
    frozen_ids = {row["id"] for row in load_frozen_questions()}
    frozen_questions = {row["question"] for row in load_frozen_questions()}
    assert INSUFFICIENT_EVIDENCE_QUESTION_ID not in frozen_ids
    assert INSUFFICIENT_EVIDENCE_QUESTION not in frozen_questions
    assert "SpaceX" in INSUFFICIENT_EVIDENCE_QUESTION


def test_uq_display_uses_calculated_confidence_not_zero() -> None:
    result = RAGCaseResult(
        run_id="r1",
        question_id="q1",
        architecture=ARCHITECTURE_MULTI_AGENT_UQ,
        question="Q?",
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.4],
        answer="A",
        confidence=0.0,
        threshold=0.55,
        decision="ANSWER",
        configuration={
            "uncertainty_result": {
                "method": "mean_retrieval_verification",
                "retrieval_score": 0.7,
                "verification_score": 0.8376,
                "confidence": 0.7688,
            },
            "threshold_source": "smoke",
        },
    )
    normalized = normalize_live_case(result)
    assert resolve_displayed_confidence(normalized) == 0.7688
    assert format_confidence_display(normalized) == "0.7688"
    assert THRESHOLD_NOT_LOCKED in format_threshold_display(normalized)
    assert format_threshold_display(normalized).startswith("0.5500")
    assert "0.0000" not in format_confidence_display(normalized)


def test_missing_uq_confidence_is_na_not_zero() -> None:
    result = RAGCaseResult(
        run_id="r1",
        question_id="q1",
        architecture=ARCHITECTURE_MULTI_AGENT_UQ,
        question="Q?",
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.4],
        answer="A",
        confidence=None,
        threshold=0.55,
        decision="ANSWER",
        configuration={"threshold_source": "smoke"},
    )
    normalized = normalize_live_case(result)
    assert resolve_displayed_confidence(normalized) is None
    assert format_confidence_display(normalized) == "n/a"
    assert normalized.decision == DECISION_UNAVAILABLE


def test_format_optional_and_streamlit_helpers_exist() -> None:
    from src.rag.live import format_optional

    assert format_optional(None) == "n/a"
    assert format_optional(0.55) == "0.5500"
    import app.streamlit_app as live_app

    assert callable(live_app.main)
    assert callable(live_app.render_architecture)


def test_phase11_smoke_artefacts_if_present() -> None:
    root = project_root()
    smoke = root / "results" / "config" / "phase11_smoke_test.json"
    detail = root / "results" / "config" / "phase11_live_smoke.json"
    if not smoke.is_file():
        return
    data = json.loads(smoke.read_text(encoding="utf-8"))
    assert data["phase"] == 11
    assert data["status"] in {"PASS", "FAIL", "NEEDS_VERIFICATION"}
    assert detail.is_file()
    detail_data = json.loads(detail.read_text(encoding="utf-8"))
    assert detail_data["n_comparisons"] >= 1
    sources = {item["question_source"] for item in detail_data["comparisons"]}
    assert sources & {"fresh", "insufficient", "frozen"}
