"""Phase 13 tests: numeric match, DEV-only T selection, lock guards, resume."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.calibration.data import (
    CALIBRATION_N,
    assert_no_test_leakage,
    load_calibration_questions,
    verify_calibration_subset,
)
from src.calibration.lock import build_lock_payload, official_lock_allowed
from src.calibration.runner import run_calibration
from src.calibration.select import select_threshold
from src.config.loader import ExperimentConfig
from src.evaluation.numeric import numeric_match
from src.models.mock_backend import MockBackend
from src.rag.schema import ARCHITECTURE_MULTI_AGENT_UQ, RAGCaseResult
from src.retrieval.retriever import RetrievedChunk


def _chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="c1",
        text="Goodwill allocated 11.7 percent of the revised purchase price.",
        score=0.82,
        doc_id="d1",
        file_name="pdf/MAS/2018/page_1.pdf",
        split="dev",
        page=1,
        company_symbol="MAS",
        report_year="2018",
        role="calibration",
        context_id="ctx",
        source_type="pdf",
    )


def _patch_get_path(tmp_path: Path):
    from src.config import get_path as real_get_path

    def fake(config, key):
        if key in {"results_raw", "results_checkpoints", "results_logs", "results_config"}:
            mapping = {
                "results_raw": tmp_path / "raw",
                "results_checkpoints": tmp_path / "checkpoints",
                "results_logs": tmp_path / "logs",
                "results_config": tmp_path / "config",
            }
            mapping[key].mkdir(parents=True, exist_ok=True)
            return mapping[key]
        return real_get_path(config, key)

    return fake


def test_numeric_match_percent_and_ratio() -> None:
    assert numeric_match("The allocation is 11.7%.", "0.11657559198542805")
    assert numeric_match("ROI is 45.51%.", "0.4550999999999999")
    assert numeric_match("$96.1 million", "96.1")
    assert not numeric_match("I cannot answer reliably because supporting evidence is insufficient.", "0.4551")


def test_calibration_questions_are_dev_and_disjoint_from_140() -> None:
    rows = load_calibration_questions(n=CALIBRATION_N)
    assert len(rows) == 40
    assert all(r["id"].startswith("finqa_dev_") for r in rows)
    verify_calibration_subset(rows)
    assert_no_test_leakage(rows)


def test_selector_max_selective_accuracy_with_coverage_floor() -> None:
    points = []
    for i in range(6):
        points.append({"question_id": f"finqa_dev_{i}", "confidence": 0.8, "correct": True})
    for i in range(6, 10):
        points.append({"question_id": f"finqa_dev_{i}", "confidence": 0.2, "correct": False})
    result = select_threshold(points)
    assert result["selected"] is True
    assert result["coverage"] >= 0.50
    assert result["threshold"] > 0.2
    assert result["selective_accuracy"] == 1.0
    assert result["n"] == 10


def test_official_lock_refuses_mock_and_mac() -> None:
    ok, reason = official_lock_allowed(backend="mock", device="cuda", n_completed=40)
    assert ok is False
    assert "Mock" in reason
    ok, reason = official_lock_allowed(backend="llama_cpp", device="mps_capable_host", n_completed=40)
    assert ok is False
    ok, reason = official_lock_allowed(backend="llama_cpp", device="cuda", n_completed=40)
    assert ok is True


def test_lock_payload_refuses_test_ids() -> None:
    cases = [
        {
            "question_id": "finqa_test_1000",
            "confidence": 0.7,
            "answer": "0.45",
            "reference_answer": "0.45",
            "configuration": {"draft_answer": "0.45"},
        }
    ]
    with pytest.raises(RuntimeError, match="leaks frozen test"):
        build_lock_payload(
            cases,
            run_id="x",
            backend="llama_cpp",
            device="cuda",
            gpu={"name": "Tesla T4"},
            git_commit="abc",
            official=True,
        )


def test_run_calibration_resume_and_no_lock_on_mock(tmp_path: Path) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    chunk = _chunk()
    backend = MockBackend(canned="The allocation is 11.7%.")
    with (
        patch("src.calibration.runner.get_path", fake_get_path),
        patch("src.calibration.lock.get_path", fake_get_path),
        patch("src.calibration.lock.load_experiment_config") as load_cfg,
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        from src.config import load_experiment_config

        load_cfg.side_effect = load_experiment_config
        first = run_calibration(
            backend_name="mock",
            n_questions=2,
            backend=backend,
            run_id="phase13_resume_test",
            stop_after=1,
            write_lock=True,
        )
        assert first["n_completed"] == 1
        assert first["status"] == "INCOMPLETE"
        assert first["lock"]["locked"] is False

        second = run_calibration(
            backend_name="mock",
            n_questions=2,
            backend=backend,
            resume="phase13_resume_test",
            write_lock=True,
        )
        assert second["n_completed"] == 2
        assert second["executed_this_session"] == 1
        assert second["lock"]["locked"] is False
        assert "NOT LOCKED" in str(second["lock"]["threshold_note"])

    raw = tmp_path / "raw" / "phase13_calibration" / "phase13_resume_test" / "cases.jsonl"
    keys = [json.loads(line)["case_key"] for line in raw.read_text().splitlines() if line.strip()]
    assert len(keys) == 2
    assert all(k.startswith("multi_agent_uq:finqa_dev_") for k in keys)
    candidate = tmp_path / "config" / "threshold.candidate.json"
    assert candidate.is_file()
    payload = json.loads(candidate.read_text())
    assert payload["locked"] is False
    assert payload["used_frozen_test_140"] is False
    assert not (tmp_path / "config" / "threshold.lock.json").is_file()


def test_run_calibration_refuses_n_over_40() -> None:
    with pytest.raises(ValueError, match="Cap is 40"):
        run_calibration(backend_name="mock", n_questions=140, write_lock=False)
