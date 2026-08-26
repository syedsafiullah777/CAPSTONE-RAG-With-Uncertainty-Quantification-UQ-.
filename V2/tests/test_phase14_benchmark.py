"""Phase 14: locked T, 9-case validation, checkpoint/resume, no 420 launch."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD, load_official_lock
from src.config import load_experiment_config
from src.models.mock_backend import MockBackend
from src.rag.schema import (
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
    ARCHITECTURE_SINGLE_AGENT,
    RAGCaseResult,
)
from src.retrieval.retriever import RetrievedChunk
from src.run.benchmark import (
    BENCHMARK_N_CASES,
    BENCHMARK_N_QUESTIONS,
    VALIDATION_N_CASES,
    VALIDATION_N_QUESTIONS,
    VALIDATION_QUESTION_IDS,
    planned_case_keys,
    run_benchmark,
    select_benchmark_questions,
    verify_full_subset,
    verify_validation_subset,
)
from src.run.store import STATUS_COMPLETED
from src.run.subset import load_frozen_question_rows


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


def _write_lock(tmp_path: Path, **overrides) -> Path:
    payload = {
        "phase": 13,
        "locked": True,
        "threshold": 0.65,
        "source_split": "dev",
        "used_frozen_test_140": False,
        "n": 40,
        "run_id": "phase13_test_lock",
    }
    payload.update(overrides)
    path = tmp_path / "config" / "threshold.lock.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _patch_get_path(tmp_path: Path):
    from src.config import get_path as real_get_path

    def fake(config, key):
        mapping = {
            "results_raw": tmp_path / "raw",
            "results_checkpoints": tmp_path / "checkpoints",
            "results_logs": tmp_path / "logs",
            "results_config": tmp_path / "config",
        }
        if key in mapping:
            mapping[key].mkdir(parents=True, exist_ok=True)
            return mapping[key]
        return real_get_path(config, key)

    return fake


def test_load_official_lock_requires_dev_locked_065(tmp_path: Path) -> None:
    path = _write_lock(tmp_path)
    lock = load_official_lock(path)
    assert lock["threshold"] == EXPECTED_LOCKED_THRESHOLD
    assert lock["locked"] is True

    bad = _write_lock(tmp_path, threshold=0.55)
    with pytest.raises(RuntimeError, match="Do not recalibrate"):
        load_official_lock(bad)
    unlocked = _write_lock(tmp_path, locked=False)
    with pytest.raises(RuntimeError, match="not locked"):
        load_official_lock(unlocked)
    leaked = _write_lock(tmp_path, used_frozen_test_140=True)
    with pytest.raises(RuntimeError, match="frozen 140"):
        load_official_lock(leaked)


def test_validation_subset_is_first_three_frozen_ids() -> None:
    rows = select_benchmark_questions(n=3, allow_full=False)
    ids = [row["id"] for row in rows]
    assert ids == list(VALIDATION_QUESTION_IDS)
    assert len(planned_case_keys(ids)) == VALIDATION_N_CASES
    all_ids = {row["id"] for row in load_frozen_question_rows()}
    assert set(ids).issubset(all_ids)
    verify_validation_subset(rows)
    assert all(qid.startswith("finqa_test_") for qid in ids)
    assert not any(qid.startswith("finqa_dev_") for qid in ids)


def test_validation_refuses_more_than_three_without_full_flag() -> None:
    with pytest.raises(ValueError, match="capped"):
        select_benchmark_questions(n=4, allow_full=False)
    with pytest.raises(ValueError, match="capped"):
        select_benchmark_questions(n=140, allow_full=False)


def test_full_subset_matches_frozen_140_but_is_not_launched() -> None:
    rows = select_benchmark_questions(n=140, allow_full=True)
    assert len(rows) == BENCHMARK_N_QUESTIONS
    assert len(planned_case_keys([r["id"] for r in rows])) == BENCHMARK_N_CASES
    verify_full_subset(rows)
    with pytest.raises(ValueError, match="must use all 140"):
        select_benchmark_questions(n=3, allow_full=True)


def test_run_benchmark_resume_and_duplicate_prevention(tmp_path: Path) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    lock = _write_lock(tmp_path)
    chunk = _chunk()
    backend = MockBackend(canned="The ROI is 45.51%.")
    with (
        patch("src.run.benchmark.get_path", fake_get_path),
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        first = run_benchmark(
            backend_name="mock",
            n_questions=2,
            backend=backend,
            run_id="phase14_resume_test",
            stop_after=3,
            skip_preflight=True,
            lock_file=lock,
            sync_drive=False,
        )
        assert first["executed_this_session"] == 3
        assert first["n_completed"] == 3
        assert first["n_pending"] == 3
        assert first["status"] == "INCOMPLETE"
        assert first["threshold"] == 0.65
        assert first["threshold_locked"] is True

        second = run_benchmark(
            backend_name="mock",
            n_questions=2,
            backend=backend,
            resume="phase14_resume_test",
            skip_preflight=True,
            lock_file=lock,
            sync_drive=False,
        )
        assert second["executed_this_session"] == 3
        assert second["skipped_this_session"] == 3
        assert second["n_completed"] == 6
        assert second["status"] == "PASS"

        third = run_benchmark(
            backend_name="mock",
            n_questions=2,
            backend=backend,
            resume="phase14_resume_test",
            skip_preflight=True,
            lock_file=lock,
            sync_drive=False,
        )
        assert third["executed_this_session"] == 0
        assert third["skipped_this_session"] == 6

    raw = tmp_path / "raw" / "phase14_benchmark" / "phase14_resume_test" / "cases.jsonl"
    keys = [json.loads(line)["case_key"] for line in raw.read_text().splitlines() if line.strip()]
    assert len(keys) == 6
    assert len(set(keys)) == 6
    fields = load_experiment_config().section("storage").get("raw_result_fields", [])
    first_case = json.loads(raw.read_text().splitlines()[0])
    for key in fields:
        assert key in first_case, f"missing raw field {key}"
    uq_rows = [json.loads(line) for line in raw.read_text().splitlines() if "multi_agent_uq:" in line]
    assert uq_rows
    assert uq_rows[0]["threshold"] == 0.65
    assert uq_rows[0]["configuration"]["threshold_locked"] is True
    assert uq_rows[0]["case_status"] == STATUS_COMPLETED


def test_run_benchmark_nine_case_validation(tmp_path: Path) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    lock = _write_lock(tmp_path)
    before = lock.read_text(encoding="utf-8")
    chunk = _chunk()
    with (
        patch("src.run.benchmark.get_path", fake_get_path),
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        summary = run_benchmark(
            backend_name="mock",
            n_questions=3,
            backend=MockBackend(canned="The value is 45.51%."),
            run_id="phase14_nine_case",
            skip_preflight=True,
            lock_file=lock,
            sync_drive=False,
        )
    assert summary["n_completed"] == 9
    assert summary["n_failed"] == 0
    assert summary["n_cases"] == 9
    assert summary["question_ids"] == list(VALIDATION_QUESTION_IDS)
    assert summary["threshold"] == 0.65
    assert summary["modifies_threshold_lock"] is False
    assert summary["chained"] is False
    assert lock.read_text(encoding="utf-8") == before


def test_drive_sync_after_cases(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    lock = _write_lock(tmp_path)
    drive = tmp_path / "drive"
    drive.mkdir()
    monkeypatch.setenv("V2_DRIVE_ROOT", str(drive))
    chunk = _chunk()
    with (
        patch("src.run.benchmark.get_path", fake_get_path),
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        summary = run_benchmark(
            backend_name="mock",
            n_questions=1,
            backend=MockBackend(),
            run_id="phase14_drive",
            skip_preflight=True,
            lock_file=lock,
            sync_drive=True,
        )
    dest = drive / "results" / "raw" / "phase14_benchmark" / "phase14_drive" / "cases.jsonl"
    assert dest.is_file()
    keys = [json.loads(line)["case_key"] for line in dest.read_text().splitlines() if line.strip()]
    assert len(keys) == 3
    assert summary["drive_sync"]["synced"] is True


def test_retry_failed_and_error_handling(tmp_path: Path) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    lock = _write_lock(tmp_path)
    chunk = _chunk()

    def boom(*_args, **_kwargs):
        raise RuntimeError("injected failure")

    with (
        patch("src.run.benchmark.get_path", fake_get_path),
        patch("src.run.benchmark.run_single_agent", side_effect=_ok(ARCHITECTURE_SINGLE_AGENT)),
        patch("src.run.benchmark.run_multi_agent", side_effect=boom),
        patch("src.run.benchmark.run_multi_agent_uq", side_effect=_ok(ARCHITECTURE_MULTI_AGENT_UQ)),
    ):
        summary = run_benchmark(
            backend_name="mock",
            n_questions=1,
            backend=MockBackend(),
            run_id="phase14_error_test",
            skip_preflight=True,
            lock_file=lock,
            sync_drive=False,
        )
    assert summary["n_failed"] == 1
    assert summary["n_completed"] == 2
    assert "multi_agent:finqa_test_1000" in summary["failed"]
    assert summary["status"] == "FAIL"


def _ok(arch: str):
    def _run(question: str, **kwargs) -> RAGCaseResult:
        extra = {}
        if arch == ARCHITECTURE_MULTI_AGENT_UQ:
            extra = {"threshold": kwargs.get("threshold", 0.65), "confidence": 0.8, "decision": "ANSWER"}
        return RAGCaseResult(
            run_id=kwargs["run_id"],
            question_id=kwargs["question_id"],
            architecture=arch,
            question=question,
            retrieved_evidence=[{"text": "e"}],
            retrieval_scores=[0.8],
            answer="ok",
            case_key=f"{arch}:{kwargs['question_id']}",
            **extra,
        )

    return _run


def test_refuses_overwrite_existing_run(tmp_path: Path) -> None:
    fake_get_path = _patch_get_path(tmp_path)
    lock = _write_lock(tmp_path)
    chunk = _chunk()
    with (
        patch("src.run.benchmark.get_path", fake_get_path),
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        run_benchmark(
            backend_name="mock",
            n_questions=1,
            backend=MockBackend(),
            run_id="phase14_overwrite_test",
            skip_preflight=True,
            lock_file=lock,
            sync_drive=False,
        )
        with pytest.raises(FileExistsError, match="Refusing to overwrite"):
            run_benchmark(
                backend_name="mock",
                n_questions=1,
                backend=MockBackend(),
                run_id="phase14_overwrite_test",
                skip_preflight=True,
                lock_file=lock,
                sync_drive=False,
            )


def test_architectures_are_independent(tmp_path: Path) -> None:
    seen: list[str] = []

    def track(arch: str):
        def _run(question: str, **kwargs) -> RAGCaseResult:
            seen.append(f"{arch}:{kwargs['question_id']}")
            extra = {}
            if arch == ARCHITECTURE_MULTI_AGENT_UQ:
                extra = {"threshold": 0.65, "confidence": 0.7, "decision": "ANSWER"}
            return RAGCaseResult(
                run_id=kwargs["run_id"],
                question_id=kwargs["question_id"],
                architecture=arch,
                question=question,
                retrieved_evidence=[{"text": "e"}],
                retrieval_scores=[0.9],
                answer="independent",
                case_key=f"{arch}:{kwargs['question_id']}",
                **extra,
            )

        return _run

    fake_get_path = _patch_get_path(tmp_path)
    lock = _write_lock(tmp_path)
    with (
        patch("src.run.benchmark.get_path", fake_get_path),
        patch("src.run.benchmark.run_single_agent", side_effect=track(ARCHITECTURE_SINGLE_AGENT)),
        patch("src.run.benchmark.run_multi_agent", side_effect=track(ARCHITECTURE_MULTI_AGENT)),
        patch("src.run.benchmark.run_multi_agent_uq", side_effect=track(ARCHITECTURE_MULTI_AGENT_UQ)),
    ):
        run_benchmark(
            backend_name="mock",
            n_questions=1,
            backend=MockBackend(),
            run_id="phase14_independent",
            skip_preflight=True,
            lock_file=lock,
            sync_drive=False,
        )
    assert seen == [
        "single_agent:finqa_test_1000",
        "multi_agent:finqa_test_1000",
        "multi_agent_uq:finqa_test_1000",
    ]


def test_does_not_modify_frozen_csvs() -> None:
    from src.config import project_root

    root = project_root()
    test_csv = root / "data" / "final" / "selected_140_questions.csv"
    cal_csv = root / "data" / "calibration" / "calibration_questions.csv"
    t_stat = test_csv.stat()
    c_stat = cal_csv.stat()
    select_benchmark_questions(n=3)
    assert test_csv.stat().st_mtime == t_stat.st_mtime
    assert cal_csv.stat().st_mtime == c_stat.st_mtime
    assert test_csv.stat().st_size == t_stat.st_size
    assert cal_csv.stat().st_size == c_stat.st_size
