"""Phase 15: 420-case notebook/entrypoint structure. Does not execute the benchmark."""

from __future__ import annotations

import json

import pytest

from src.config import project_root
from src.run.benchmark import (
    BENCHMARK_N_CASES,
    BENCHMARK_N_QUESTIONS,
    planned_case_keys,
    run_benchmark,
    select_benchmark_questions,
    verify_full_subset,
)


def _nb(name: str) -> dict:
    path = project_root() / "notebooks" / name
    assert path.is_file(), path
    return json.loads(path.read_text(encoding="utf-8"))


def _cell_text(nb: dict) -> str:
    parts: list[str] = []
    for cell in nb.get("cells") or []:
        src = cell.get("source") or []
        if isinstance(src, list):
            parts.append("".join(src))
        else:
            parts.append(str(src))
    return "\n".join(parts)


def test_phase15_notebook_is_420_not_9_case() -> None:
    nb = _nb("colab_phase15_full_benchmark.ipynb")
    text = _cell_text(nb)
    assert nb.get("nbformat") == 4
    assert len(nb.get("cells") or []) >= 10
    assert "run_full_benchmark.py" in text
    assert "--backend llama_cpp" in text
    assert "--resume-latest" in text
    assert "V2_DRIVE_ROOT" in text
    assert "140" in text and "420" in text
    assert "T = 0.65" in text or "T=0.65" in text
    assert "phase15_benchmark" in text
    assert "/content/drive/MyDrive/MSc-RAG" in text
    assert "run_benchmark.py --backend llama_cpp --n-questions 3" not in text
    assert "Incremental JSONL" in text or "incremental" in text.lower()
    assert "checkpoint" in text.lower()
    assert "unique_keys" in text


def test_phase14_nine_case_notebook_unchanged_as_evidence() -> None:
    nb = _nb("colab_phase14_benchmark_validation.ipynb")
    text = _cell_text(nb)
    assert "run_benchmark.py --backend llama_cpp --n-questions 3" in text
    assert "run_full_benchmark.py" not in text
    assert "9 cases" in text
    assert "Does **not** launch the full 420-case benchmark" in text


def test_full_subset_is_140_questions() -> None:
    rows = select_benchmark_questions(n=140, allow_full=True)
    assert len(rows) == BENCHMARK_N_QUESTIONS
    verify_full_subset(rows)
    assert len(planned_case_keys([r["id"] for r in rows])) == BENCHMARK_N_CASES


def test_full_benchmark_refuses_mock_without_running() -> None:
    with pytest.raises(RuntimeError, match="mock"):
        run_benchmark(
            backend_name="mock",
            n_questions=140,
            allow_full=True,
            skip_preflight=True,
            sync_drive=False,
        )


def test_full_script_exists_and_refuses_mock() -> None:
    import os
    import subprocess
    import sys

    script = project_root() / "scripts" / "run_full_benchmark.py"
    assert script.is_file()
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
