"""Phase 12 pilot: subset, schema, checkpoint, resume, duplicate prevention."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import load_experiment_config
from src.config.loader import ExperimentConfig
from src.models.mock_backend import MockBackend
from src.rag.schema import (
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
    ARCHITECTURE_SINGLE_AGENT,
    RAGCaseResult,
)
from src.retrieval.retriever import RetrievedChunk
from src.run.pilot import PILOT_ARCHITECTURES, planned_case_keys, run_pilot
from src.run.store import CaseStore, STATUS_COMPLETED
from src.run.subset import (
    PILOT_N_CASES,
    PILOT_N_QUESTIONS,
    THRESHOLD_NOTE,
    ids_sha256,
    select_pilot_questions,
    verify_pilot_subset,
    write_pilot_manifest,
)


def _chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="c1",
        text="S&P 500 December 31, 2008 $100.00 December 31, 2010 145.51. Net interest 2018 270.4 2017 267.8.",
        score=0.88,
        doc_id="d1",
        file_name="pdf/SNA/2013/page_34.pdf",
        split="test",
        page=1,
        company_symbol="SNA",
        report_year="2013",
        role="test",
        context_id="ctx",
        source_type="pdf",
    )


def _patch_get_path(tmp_path: Path):
    from src.config import get_path as real_get_path

    def fake(config, key):
        if key == "results_raw":
            return tmp_path / "raw"
        if key == "results_checkpoints":
            return tmp_path / "checkpoints"
        if key == "results_logs":
            return tmp_path / "logs"
        return real_get_path(config, key)

    return fake


def test_pilot_subset_is_first_six_frozen_ids() -> None:
    rows = select_pilot_questions(n=6)
    ids = [row["id"] for row in rows]
    assert ids == [
        "finqa_test_1000",
        "finqa_test_1012",
        "finqa_test_1017",
        "finqa_test_1027",
        "finqa_test_1039",
        "finqa_test_1040",
    ]
    assert len(ids) == PILOT_N_QUESTIONS
    assert len(planned_case_keys(ids)) == PILOT_N_CASES
    from src.run.subset import load_frozen_question_rows

    all_ids = {row["id"] for row in load_frozen_question_rows()}
    assert set(ids).issubset(all_ids)
    verify_pilot_subset(rows)


def test_pilot_refuses_more_than_six_questions() -> None:
    with pytest.raises(ValueError, match="capped"):
        select_pilot_questions(n=140)


def test_pilot_manifest_does_not_lock_threshold(tmp_path: Path) -> None:
    questions = select_pilot_questions(n=6)
    path = write_pilot_manifest(questions, path=tmp_path / "pilot_subset_manifest.json")
    manifest = json.loads(path.read_text())
    assert manifest["modifies_frozen_140"] is False
    assert manifest["modifies_frozen_calibration"] is False
    assert manifest["threshold_locked"] is False
    assert manifest["threshold_note"] == THRESHOLD_NOTE
    assert manifest["n_cases"] == 18
    verify_pilot_subset(questions, manifest)


def test_case_store_skips_duplicates_and_resumes(tmp_path: Path) -> None:
    store = CaseStore(tmp_path / "run1")
    result = RAGCaseResult(
        run_id="r",
        question_id="finqa_test_1000",
        architecture=ARCHITECTURE_SINGLE_AGENT,
        question="Q",
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.9],
        answer="A",
        case_key="single_agent:finqa_test_1000",
    )
    assert store.append_result(result) is True
    assert store.append_result(result) is False
    assert store.has_completed("single_agent:finqa_test_1000")
    assert store.should_run("single_agent:finqa_test_1000", retry_failed=True) is False
    reloaded = CaseStore(tmp_path / "run1")
    assert reloaded.has_completed("single_agent:finqa_test_1000")
    lines = (tmp_path / "run1" / "cases.jsonl").read_text().strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["case_status"] == STATUS_COMPLETED


def test_store_records_failed_and_retries(tmp_path: Path) -> None:
    store = CaseStore(tmp_path / "runf")
    failed = RAGCaseResult(
        run_id="r",
        question_id="q1",
        architecture=ARCHITECTURE_MULTI_AGENT,
        question="Q",
        retrieved_evidence=[],
        retrieval_scores=[],
        answer="",
        error="boom",
        case_key="multi_agent:q1",
    )
    assert store.append_result(failed) is True
    assert store.should_run("multi_agent:q1", retry_failed=False) is False
    assert store.should_run("multi_agent:q1", retry_failed=True) is True


def test_run_pilot_resume_and_duplicate_prevention(tmp_path: Path) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    chunk = _chunk()
    backend = MockBackend(canned="The ROI is 45.51%.")
    with (
        patch("src.run.pilot.get_path", fake_get_path),
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        first = run_pilot(
            backend_name="mock",
            n_questions=2,
            backend=backend,
            run_id="phase12_resume_test",
            stop_after=3,
            skip_preflight=True,
        )
        assert first["executed_this_session"] == 3
        assert first["n_completed"] == 3
        assert first["n_pending"] == 3
        assert first["status"] == "INCOMPLETE"
        assert first["threshold"] == 0.55
        assert first["threshold_locked"] is False
        assert first["threshold_note"] == THRESHOLD_NOTE

        second = run_pilot(
            backend_name="mock",
            n_questions=2,
            backend=backend,
            resume="phase12_resume_test",
            skip_preflight=True,
        )
        assert second["executed_this_session"] == 3
        assert second["skipped_this_session"] == 3
        assert second["n_completed"] == 6
        assert second["n_pending"] == 0
        assert second["status"] == "PASS"

        third = run_pilot(
            backend_name="mock",
            n_questions=2,
            backend=backend,
            resume="phase12_resume_test",
            skip_preflight=True,
        )
        assert third["executed_this_session"] == 0
        assert third["skipped_this_session"] == 6
        assert third["n_completed"] == 6

    raw = tmp_path / "raw" / "phase12_pilot" / "phase12_resume_test" / "cases.jsonl"
    keys = [json.loads(line)["case_key"] for line in raw.read_text().splitlines() if line.strip()]
    assert len(keys) == 6
    assert len(set(keys)) == 6
    fields = load_experiment_config().section("storage").get("raw_result_fields", [])
    first_case = json.loads(raw.read_text().splitlines()[0])
    for key in fields:
        assert key in first_case, f"missing raw field {key}"
    uq_rows = [json.loads(line) for line in raw.read_text().splitlines() if "multi_agent_uq:" in line]
    assert uq_rows
    assert uq_rows[0]["decision"] in {"ANSWER", "ABSTAIN"}
    assert uq_rows[0]["configuration"]["threshold_locked"] is False
    assert uq_rows[0]["configuration"]["threshold_note"] == THRESHOLD_NOTE


def test_run_pilot_error_handling_continues(tmp_path: Path) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    chunk = _chunk()

    def boom(*_args, **_kwargs):
        raise RuntimeError("injected failure")

    with (
        patch("src.run.pilot.get_path", fake_get_path),
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", side_effect=boom),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
        patch("src.run.pilot.run_single_agent", side_effect=run_single_ok),
        patch("src.run.pilot.run_multi_agent", side_effect=boom),
        patch("src.run.pilot.run_multi_agent_uq", side_effect=run_uq_ok),
    ):
        summary = run_pilot(
            backend_name="mock",
            n_questions=1,
            backend=MockBackend(),
            run_id="phase12_error_test",
            skip_preflight=True,
        )
    assert summary["n_failed"] == 1
    assert summary["n_completed"] == 2
    assert "multi_agent:finqa_test_1000" in summary["failed"]
    assert summary["status"] == "FAIL"


def run_single_ok(question: str, **kwargs) -> RAGCaseResult:
    return RAGCaseResult(
        run_id=kwargs["run_id"],
        question_id=kwargs["question_id"],
        architecture=ARCHITECTURE_SINGLE_AGENT,
        question=question,
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.8],
        answer="ok",
        case_key=f"single_agent:{kwargs['question_id']}",
        latency_seconds=0.01,
    )


def run_uq_ok(question: str, **kwargs) -> RAGCaseResult:
    return RAGCaseResult(
        run_id=kwargs["run_id"],
        question_id=kwargs["question_id"],
        architecture=ARCHITECTURE_MULTI_AGENT_UQ,
        question=question,
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.8],
        answer="ok",
        confidence=0.7,
        threshold=0.55,
        decision="ANSWER",
        case_key=f"multi_agent_uq:{kwargs['question_id']}",
        latency_seconds=0.02,
        configuration={},
    )


def test_refuses_locked_threshold(tmp_path: Path) -> None:
    cfg = load_experiment_config()
    raw = dict(cfg.raw)
    raw["uncertainty"] = dict(cfg.section("uncertainty"))
    raw["uncertainty"]["confidence_threshold"] = 0.7
    locked = ExperimentConfig(raw=raw, source_path=cfg.source_path)
    with pytest.raises(RuntimeError, match="must not use a locked"):
        run_pilot(
            backend_name="mock",
            n_questions=1,
            config=locked,
            backend=MockBackend(),
            skip_preflight=True,
        )


def test_refuses_overwrite_existing_run(tmp_path: Path) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    chunk = _chunk()
    with (
        patch("src.run.pilot.get_path", fake_get_path),
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        run_pilot(
            backend_name="mock",
            n_questions=1,
            backend=MockBackend(),
            run_id="phase12_overwrite_test",
            skip_preflight=True,
        )
        with pytest.raises(FileExistsError, match="Refusing to overwrite"):
            run_pilot(
                backend_name="mock",
                n_questions=1,
                backend=MockBackend(),
                run_id="phase12_overwrite_test",
                skip_preflight=True,
            )


def test_architectures_are_independent(tmp_path: Path) -> None:
    seen: list[str] = []

    def track(arch: str):
        def _run(question: str, **kwargs) -> RAGCaseResult:
            seen.append(f"{arch}:{kwargs['question_id']}")
            return RAGCaseResult(
                run_id=kwargs["run_id"],
                question_id=kwargs["question_id"],
                architecture=arch,
                question=question,
                retrieved_evidence=[{"text": "e"}],
                retrieval_scores=[0.9],
                answer="independent",
                case_key=f"{arch}:{kwargs['question_id']}",
            )

        return _run

    fake_get_path = _patch_get_path(tmp_path)
    with (
        patch("src.run.pilot.get_path", fake_get_path),
        patch("src.run.pilot.run_single_agent", side_effect=track(ARCHITECTURE_SINGLE_AGENT)),
        patch("src.run.pilot.run_multi_agent", side_effect=track(ARCHITECTURE_MULTI_AGENT)),
        patch("src.run.pilot.run_multi_agent_uq", side_effect=track(ARCHITECTURE_MULTI_AGENT_UQ)),
    ):
        run_pilot(
            backend_name="mock",
            n_questions=1,
            backend=MockBackend(),
            run_id="phase12_independent",
            skip_preflight=True,
        )
    assert seen == [
        "single_agent:finqa_test_1000",
        "multi_agent:finqa_test_1000",
        "multi_agent_uq:finqa_test_1000",
    ]
    assert PILOT_ARCHITECTURES == (
        ARCHITECTURE_SINGLE_AGENT,
        ARCHITECTURE_MULTI_AGENT,
        ARCHITECTURE_MULTI_AGENT_UQ,
    )
