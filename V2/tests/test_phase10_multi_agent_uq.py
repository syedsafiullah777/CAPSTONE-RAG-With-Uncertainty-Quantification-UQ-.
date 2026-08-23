"""Phase 10 tests: UQ confidence, abstention gate, multi_agent_uq pipeline."""

from __future__ import annotations

import json
from unittest.mock import patch

from src.config import load_experiment_config, project_root
from src.models.mock_backend import MockBackend
from src.rag.multi_agent_uq import run_multi_agent_uq
from src.rag.schema import ARCHITECTURE_MULTI_AGENT_UQ, RAGCaseResult
from src.rag.uncertainty import (
    apply_abstention_decision,
    compute_combined_confidence,
    compute_retrieval_score,
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


def test_retrieval_and_combined_confidence() -> None:
    assert compute_retrieval_score([0.8, 0.6]) == 0.7
    combined = compute_combined_confidence(0.8, 0.6)
    assert combined["confidence"] == 0.7
    assert combined["method"] == "mean_retrieval_verification"


def test_apply_abstention_decision() -> None:
    answer, decision = apply_abstention_decision(
        draft_answer="Draft",
        confidence=0.7,
        threshold=0.55,
        abstention_message="Abstain msg",
    )
    assert decision == "ANSWER"
    assert answer == "Draft"

    answer, decision = apply_abstention_decision(
        draft_answer="Draft",
        confidence=0.4,
        threshold=0.55,
        abstention_message="Abstain msg",
    )
    assert decision == "ABSTAIN"
    assert answer == "Abstain msg"


def test_multi_agent_uq_pipeline_answer_with_mock() -> None:
    chunk = _sample_chunk()

    with patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]):
        result = run_multi_agent_uq(
            "What was the percentage change?",
            question_id="finqa_test_1012",
            reference_answer="0.0097",
            backend=MockBackend(canned="Approximately 0.93% increase."),
            backend_name="mock",
            run_id="phase10_test",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
            threshold=0.55,
        )

    assert result.architecture == ARCHITECTURE_MULTI_AGENT_UQ
    assert result.case_key == "multi_agent_uq:finqa_test_1012"
    assert result.error is None
    assert result.answer
    assert result.decision == "ANSWER"
    assert result.threshold == 0.55
    assert result.confidence is not None
    assert result.confidence >= 0.55
    uq = result.configuration["uncertainty_result"]
    assert uq["retrieval_score"] == 0.91
    assert result.configuration["draft_answer"]


def test_multi_agent_uq_pipeline_abstain_with_high_threshold() -> None:
    chunk = _sample_chunk()

    with patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]):
        result = run_multi_agent_uq(
            "What was the percentage change?",
            question_id="finqa_test_1012",
            reference_answer="0.0097",
            backend=MockBackend(canned="Approximately 0.93% increase."),
            backend_name="mock",
            run_id="phase10_test_abstain",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
            threshold=0.99,
        )

    assert result.decision == "ABSTAIN"
    assert "insufficient" in result.answer.lower()
    assert result.configuration["draft_answer"]


def test_multi_agent_uq_schema_fields() -> None:
    fields = load_experiment_config().section("storage").get("raw_result_fields", [])
    result = RAGCaseResult(
        run_id="r1",
        question_id="q1",
        architecture=ARCHITECTURE_MULTI_AGENT_UQ,
        question="Q?",
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.9],
        answer="A",
        verification_result={"verification_score": 0.8, "status": "VERIFIED"},
        confidence=0.85,
        threshold=0.55,
        decision="ANSWER",
        configuration={"uncertainty_result": {"confidence": 0.85}},
    )
    data = result.to_dict()
    for key in fields:
        assert key in data, f"missing field {key}"


def test_phase10_smoke_artefacts_if_present() -> None:
    root = project_root()
    smoke = root / "results" / "config" / "phase10_smoke_test.json"
    detail = root / "results" / "config" / "phase10_multi_agent_uq_smoke.json"
    if not smoke.is_file():
        return
    data = json.loads(smoke.read_text(encoding="utf-8"))
    assert data["phase"] == 10
    assert data["status"] in {"PASS", "FAIL", "NEEDS_VERIFICATION"}
    assert detail.is_file()
    detail_data = json.loads(detail.read_text(encoding="utf-8"))
    assert detail_data["architecture"] == "multi_agent_uq"
    case0 = detail_data["cases"][0]
    assert case0["retrieved_evidence"]
    assert case0["verification_result"]
    assert case0["decision"] in {"ANSWER", "ABSTAIN"}
    assert case0["threshold"] is not None
