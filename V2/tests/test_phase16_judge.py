"""Phase 16 post-hoc LLM-as-judge. Does not rerun RAG or rewrite Phase 15 JSONL."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import project_root
from src.evaluation.judge import (
    METRIC_LABEL,
    build_judge_prompt,
    claim_for_judge,
    format_retrieved_evidence,
    judge_one_case,
)
from src.evaluation.judge_runner import run_judge
from src.evaluation.runner import EXPECTED_RAW_SHA256, sha256_file
from src.models.mock_backend import MockBackend


def _nb(name: str) -> dict:
    path = project_root() / "notebooks" / name
    assert path.is_file(), path
    return json.loads(path.read_text(encoding="utf-8"))


def _cell_text(nb: dict) -> str:
    parts: list[str] = []
    for cell in nb.get("cells") or []:
        src = cell.get("source") or []
        parts.append("".join(src) if isinstance(src, list) else str(src))
    return "\n".join(parts)


def _case(*, architecture: str, decision: str = "ANSWER", draft: str | None = None) -> dict:
    return {
        "case_key": f"{architecture}:finqa_test_1",
        "question_id": "finqa_test_1",
        "architecture": architecture,
        "question": "What is the ROI?",
        "answer": (
            "I cannot answer reliably because supporting evidence is insufficient."
            if architecture == "multi_agent_uq" and decision == "ABSTAIN"
            else "The ROI is 12.5 percent."
        ),
        "decision": decision,
        "reference_answer": "0.125",
        "configuration": {"draft_answer": draft} if draft is not None else {},
        "retrieved_evidence": [
            {"file_name": "pdf/A/1.pdf", "text": "Return on investment was 12.5 percent."},
        ],
    }


def test_uq_claim_uses_draft_not_abstention() -> None:
    case = _case(architecture="multi_agent_uq", decision="ABSTAIN", draft="The ROI is 12.5 percent.")
    claim, source = claim_for_judge(case)
    assert source == "draft_answer"
    assert "12.5" in claim
    assert "cannot answer reliably" not in claim
    prompt = build_judge_prompt(
        question=case["question"],
        evidence=format_retrieved_evidence(case["retrieved_evidence"]),
        claim=claim,
    )
    assert "12.5" in prompt
    assert "cannot answer reliably" not in prompt
    assert "program_answer" not in prompt.lower()
    assert "gold context" not in prompt.lower()
    assert case["reference_answer"] not in prompt


def test_single_agent_claim_is_displayed_answer() -> None:
    case = _case(architecture="single_agent")
    claim, source = claim_for_judge(case)
    assert source == "answer"
    assert claim == case["answer"]


def test_judge_parse_and_metric_label() -> None:
    case = _case(architecture="single_agent")
    row = judge_one_case(case, MockBackend(), source_raw_sha256="abc")
    assert row["used_rag_rerun"] is False
    assert row["parse_failure"] is False
    assert row["parsed_faithfulness_score"] == 0.85
    assert row["raw_judge_output"]
    assert row["judge_metric_label"] == METRIC_LABEL
    assert "official RAGAS" not in METRIC_LABEL
    assert "custom/RAGAS-inspired" in METRIC_LABEL


def test_empty_uq_draft_is_parse_failure() -> None:
    case = _case(architecture="multi_agent_uq", decision="ABSTAIN", draft="")
    row = judge_one_case(case, MockBackend(), source_raw_sha256="abc")
    assert row["parse_failure"] is True
    assert row["error"] == "empty_claim"
    assert row["parsed_faithfulness_score"] is None


def test_official_mock_420_refused() -> None:
    with pytest.raises(RuntimeError, match="mock"):
        run_judge(backend_name="mock", n_cases=420, sync_drive=False)


def test_script_refuses_mock_without_n_cases() -> None:
    import os
    import subprocess
    import sys

    script = project_root() / "scripts" / "run_judge.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root())
    proc = subprocess.run(
        [sys.executable, str(script), "--backend", "mock"],
        cwd=str(project_root()),
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode != 0
    assert "mock" in (proc.stderr + proc.stdout).lower()


def test_notebook_is_420_judge_not_rag_rerun() -> None:
    nb = _nb("colab_phase16_judge.ipynb")
    text = _cell_text(nb)
    assert nb.get("nbformat") == 4
    assert "run_judge.py" in text
    assert "--backend llama_cpp" in text
    assert "--resume-latest" in text
    assert "420" in text
    assert "phase16_judge" in text
    assert "f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa" in text
    assert "run_full_benchmark.py" not in text
    assert "/content/drive/MyDrive/MSc-RAG" in text
    assert "custom/RAGAS-inspired" in text
    assert "Not official RAGAS" in text or "not official RAGAS" in text


def test_mock_three_cases_resume_and_phase15_sha_stable() -> None:
    import shutil

    raw = project_root() / "results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl"
    if not raw.is_file():
        pytest.skip("canonical Phase 15 JSONL not present")
    rid = "phase16_judge_test_mock3"
    run_dir = project_root() / "results/raw/phase16_judge" / rid
    ckpt = project_root() / "results/checkpoints/phase16_judge" / f"{rid}.json"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    if ckpt.exists():
        ckpt.unlink()
    before = sha256_file(raw)
    assert before == EXPECTED_RAW_SHA256
    cpu_path = project_root() / "results/processed/phase16_cases.jsonl"
    cpu_before = cpu_path.read_bytes() if cpu_path.is_file() else None
    summary = run_judge(
        backend_name="mock",
        n_cases=3,
        backend=MockBackend(),
        sync_drive=False,
        run_id="phase16_judge_test_mock3",
    )
    after = sha256_file(raw)
    assert after == before
    if cpu_before is not None:
        assert cpu_path.read_bytes() == cpu_before
    assert summary["used_rag_rerun"] is False
    assert summary["n_planned"] == 3
    assert summary["n_completed"] == 3
    assert summary["status"] == "PASS"
    resume = run_judge(
        backend_name="mock",
        n_cases=3,
        backend=MockBackend(),
        sync_drive=False,
        resume="phase16_judge_test_mock3",
    )
    assert resume["skipped_this_session"] == 3
    assert resume["executed_this_session"] == 0
    assert sha256_file(raw) == EXPECTED_RAW_SHA256
    judge_path = project_root() / "results/raw/phase16_judge/phase16_judge_test_mock3/judge.jsonl"
    lines = [json.loads(line) for line in judge_path.read_text().splitlines() if line.strip()]
    assert len(lines) == 3
    assert all(row.get("used_rag_rerun") is False for row in lines)
    assert all(row.get("parsed_faithfulness_score") == 0.85 for row in lines)
