"""Phase 9 tests: multi-agent prompts, verification, pipeline (mock LLM)."""

from __future__ import annotations

import json
from unittest.mock import patch

from src.config import load_experiment_config, project_root
from src.models.mock_backend import MockBackend
from src.rag.prompts import build_multi_agent_draft_prompt, build_multi_agent_verification_prompt
from src.rag.schema import ARCHITECTURE_MULTI_AGENT, RAGCaseResult
from src.rag.multi_agent import run_multi_agent
from src.rag.text_utils import clean_generated_answer, parse_unit_score, token_overlap
from src.rag.verification import compute_verification_result
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


def test_clean_generated_answer_strips_think_and_echo() -> None:
    raw = (
        "<think>I should follow the instructions</think>\n"
        "You are answering questions about financial documents.\n"
        "Final answer: 45.51\n"
        "| prompt_chars=99"
    )
    assert clean_generated_answer(raw) == "45.51"


def test_token_overlap_and_parse_score() -> None:
    assert token_overlap("interest expense 270.4", "Interest expense net 270.4 million") > 0.0
    assert parse_unit_score("0.85") == 0.85
    assert parse_unit_score("Support score: 0.72") == 0.72
    assert parse_unit_score("Return only a number between 0 and 1.\n0.64") == 0.64
    assert parse_unit_score("between 0 and 1") is None


def test_multi_agent_prompts() -> None:
    chunk = _sample_chunk()
    draft = build_multi_agent_draft_prompt("What changed?", [chunk])
    verify = build_multi_agent_verification_prompt("What changed?", "0.93% increase", [chunk])
    assert "Final answer" in draft
    assert "Support score" in verify
    assert "270.4" in draft


def test_compute_verification_result_with_mock_backend() -> None:
    chunk = _sample_chunk()
    backend = MockBackend(canned="The change is about 0.93%.")
    result = compute_verification_result(
        "What changed?",
        "The change is about 0.93% based on interest expense.",
        [chunk],
        backend,
    )
    assert 0.0 <= result["verification_score"] <= 1.0
    assert result["status"] in {"VERIFIED", "WEAK_EVIDENCE"}
    assert result["llm_score"] == 0.85
    assert result["rationale"]
    assert result["rationale"].startswith(result["status"])


def test_multi_agent_pipeline_with_mock_backend_and_fake_retrieve() -> None:
    chunk = _sample_chunk()

    with patch("src.rag.multi_agent.retrieve", return_value=[chunk]):
        result = run_multi_agent(
            "What was the percentage change?",
            question_id="finqa_test_1012",
            reference_answer="0.0097",
            backend=MockBackend(canned="Approximately 0.93% increase."),
            backend_name="mock",
            run_id="phase9_test",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
        )

    assert result.architecture == ARCHITECTURE_MULTI_AGENT
    assert result.case_key == "multi_agent:finqa_test_1012"
    assert result.error is None
    assert result.answer
    assert len(result.retrieved_evidence) == 1
    assert result.verification_result is not None
    assert result.verification_result["verification_score"] >= 0.0
    assert result.confidence == result.verification_result["verification_score"]
    assert result.decision == "ANSWER"
    assert result.threshold is None


def test_multi_agent_schema_fields() -> None:
    fields = load_experiment_config().section("storage").get("raw_result_fields", [])
    result = RAGCaseResult(
        run_id="r1",
        question_id="q1",
        architecture=ARCHITECTURE_MULTI_AGENT,
        question="Q?",
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.9],
        answer="A",
        verification_result={"verification_score": 0.8, "status": "VERIFIED"},
        confidence=0.8,
    )
    data = result.to_dict()
    for key in fields:
        assert key in data, f"missing field {key}"


def test_phase9_smoke_artefacts_if_present() -> None:
    root = project_root()
    smoke = root / "results" / "config" / "phase9_smoke_test.json"
    detail = root / "results" / "config" / "phase9_multi_agent_smoke.json"
    if not smoke.is_file():
        return
    data = json.loads(smoke.read_text(encoding="utf-8"))
    assert data["phase"] == 9
    assert data["status"] in {"PASS", "FAIL", "NEEDS_VERIFICATION"}
    assert detail.is_file()
    detail_data = json.loads(detail.read_text(encoding="utf-8"))
    assert detail_data["architecture"] == "multi_agent"
    case0 = detail_data["cases"][0]
    assert case0["retrieved_evidence"]
    assert case0["verification_result"]
