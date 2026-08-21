"""Phase 2 tests: profiling helpers and report artefacts (no 140 selection)."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import V2_ROOT, project_root
from src.data.profile_finqa import EXPECTED_COLUMNS, build_profile, profile_split, render_markdown


def _fake_row(i: int, question: str | None = None) -> dict:
    q = question if question is not None else f"What is metric {i}?"
    return {
        "id": f"finqa_{i}",
        "context_id": f"ctx_{i // 2}",
        "split": "test",
        "question": q,
        "program_answer": str(i),
        "original_answer": str(i),
        "context": "pre table post " * 20,
        "table": "| a | b |\n| 1 | 2 |",
        "pre_text": "pre",
        "post_text": "post",
        "file_name": f"EDGAR/file_{i // 2}.pdf",
        "company_name": f"Company {i % 3}",
        "company_symbol": f"C{i % 3}",
        "report_year": 2010 + (i % 5),
        "page_number": i % 10,
        "company_sector": "Financials",
        "company_industry": "Banks",
        "company_headquarters": "US",
        "company_date_added": None,
        "company_cik": 1000 + i,
        "company_founded": "1900",
    }


def test_profile_split_detects_duplicate_questions() -> None:
    rows = [_fake_row(0), _fake_row(1, question="Same Q?"), _fake_row(2, question="Same Q?")]
    result = profile_split("test", rows)
    assert result["n_rows"] == 3
    assert result["duplicate_question_groups"] == 1
    assert result["duplicate_question_extra_rows"] == 1
    assert result["rows_with_essential_fields"] == 3


def test_build_profile_from_fake_dataset() -> None:
    class FakeSplit:
        def __init__(self, rows):
            self._rows = rows

        def __iter__(self):
            return iter(self._rows)

        def __len__(self):
            return len(self._rows)

    class FakeDS(dict):
        pass

    ds = FakeDS(
        train=FakeSplit([_fake_row(i) for i in range(3)]),
        dev=FakeSplit([_fake_row(100 + i) for i in range(2)]),
        test=FakeSplit([_fake_row(200 + i) for i in range(5)]),
    )
    profile = build_profile(ds)
    assert profile["splits"] == {"train": 3, "dev": 2, "test": 5}
    assert profile["sampling_readiness"]["phase2_selected_140"] is False
    assert profile["columns"] == EXPECTED_COLUMNS
    md = render_markdown(profile)
    assert "FinQA" in md
    assert "not** selected" in md or "not selected" in md.lower() or "**not** selected" in md


def test_phase2_docs_exist() -> None:
    assert (project_root() / "docs" / "v1_audit.md").is_file()
    # dataset_profile.md is produced by inspect_dataset.py; require it after the live run.
    profile_md = project_root() / "docs" / "dataset_profile.md"
    profile_json = project_root() / "data" / "processed" / "finqa_profile.json"
    assert profile_md.is_file(), "Run: PYTHONPATH=. python scripts/inspect_dataset.py"
    assert profile_json.is_file()
    data = json.loads(profile_json.read_text(encoding="utf-8"))
    assert data["subset"] == "FinQA"
    assert set(data["splits"]) == {"train", "dev", "test"}
    assert data["splits"]["train"] == 6251
    assert data["splits"]["dev"] == 883
    assert data["splits"]["test"] == 1147
    assert data["sampling_readiness"]["phase2_selected_140"] is False
    assert data["sampling_readiness"]["can_support_140_from_test"] is True
    assert "selected_140_questions.csv" not in [
        p.name for p in (project_root() / "data" / "final").iterdir()
    ]


def test_v2_root_unchanged_name() -> None:
    assert V2_ROOT.name == "V2"
    assert Path(V2_ROOT).is_dir()
