"""Phase 8 tests: schema, prompts, single-agent pipeline (mock LLM)."""

from __future__ import annotations

import json
from unittest.mock import patch

from src.config import load_experiment_config, project_root
from src.models.mock_backend import MockBackend
from src.rag.prompts import build_baseline_prompt, format_evidence
from src.rag.schema import ARCHITECTURE_SINGLE_AGENT, RAGCaseResult
from src.rag.single_agent import run_single_agent
from src.retrieval.retriever import RetrievedChunk


def test_schema_has_required_raw_fields() -> None:
    fields = load_experiment_config().section("storage").get("raw_result_fields", [])
    result = RAGCaseResult(
        run_id="r1",
        question_id="q1",
        architecture=ARCHITECTURE_SINGLE_AGENT,
        question="Q?",
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.9],
        answer="A",
    )
    data = result.to_dict()
    for key in fields:
        assert key in data, f"missing field {key}"
    assert result.case_id == "single_agent:q1"
    assert data["decision"] == "ANSWER"
    assert data["verification_result"] is None
    assert data["confidence"] is None


def test_format_evidence_and_prompt() -> None:
    chunks = [
        RetrievedChunk(
            chunk_id="c1",
            text="Revenue was 100.",
            score=0.88,
            doc_id="d1",
            file_name="pdf/X/2013/page_1.pdf",
            split="test",
            page=1,
            company_symbol="X",
            report_year="2013",
            role="test",
            context_id="ctx",
            source_type="pdf",
        )
    ]
    evidence = format_evidence(chunks)
    assert "Revenue was 100." in evidence
    prompt = build_baseline_prompt("What was revenue?", chunks)
    assert "What was revenue?" in prompt
    assert "Revenue was 100." in prompt
    assert "Evidence:" in prompt


def test_single_agent_with_mock_backend_and_fake_retrieve() -> None:
    fake_chunks = [
        RetrievedChunk(
            chunk_id="c1",
            text="S&P 500 value at end of 2010 was 145.51.",
            score=0.91,
            doc_id="d1",
            file_name="pdf/SNA/2013/page_34.pdf",
            split="test",
            page=1,
            company_symbol="SNA",
            report_year="2013",
            role="test",
            context_id="finqa_test_ctx_130",
            source_type="pdf",
        )
    ]

    with patch("src.rag.single_agent.retrieve", return_value=fake_chunks):
        result = run_single_agent(
            "What is the S&P value?",
            question_id="finqa_test_1000",
            reference_answer="0.455",
            backend=MockBackend(canned="45.51"),
            backend_name="mock",
            run_id="phase8_test",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
        )

    assert result.architecture == "single_agent"
    assert result.case_key == "single_agent:finqa_test_1000"
    assert result.error is None
    assert result.answer
    assert len(result.retrieved_evidence) == 1
    assert result.retrieved_evidence[0]["file_name"] == "pdf/SNA/2013/page_34.pdf"
    assert result.retrieval_scores[0] == 0.91
    assert result.decision == "ANSWER"
    assert result.confidence is None
    assert result.verification_result is None
    assert result.backend == "mock"


def test_phase8_smoke_artefacts_if_present() -> None:
    root = project_root()
    smoke = root / "results" / "config" / "phase8_smoke_test.json"
    detail = root / "results" / "config" / "phase8_single_agent_smoke.json"
    if not smoke.is_file():
        return
    data = json.loads(smoke.read_text(encoding="utf-8"))
    assert data["phase"] == 8
    assert data["status"] in {"PASS", "FAIL", "NEEDS_VERIFICATION"}
    assert detail.is_file()
    detail_data = json.loads(detail.read_text(encoding="utf-8"))
    assert detail_data["architecture"] == "single_agent"
    assert detail_data["n_questions"] >= 1
    case0 = detail_data["cases"][0]
    assert case0["retrieved_evidence"]
    assert case0["architecture"] == "single_agent"
