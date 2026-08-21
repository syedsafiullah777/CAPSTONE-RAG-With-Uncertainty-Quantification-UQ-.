"""Phase 3 tests: verification artefacts exist; 140 not frozen."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import project_root


def test_phase3_checkpoint_docs_exist() -> None:
    root = project_root()
    assert (root / "docs" / "phase3_dataset_verification.md").is_file()
    assert (root / "docs" / "dataset_profile.md").is_file()
    assert (root / "data" / "processed" / "finqa_profile.json").is_file()
    assert (root / "data" / "processed" / "finqa_pdf_probe.json").is_file()


def test_phase3_pdf_probe_test_fully_resolved() -> None:
    probe = json.loads(
        (project_root() / "data" / "processed" / "finqa_pdf_probe.json").read_text(encoding="utf-8")
    )
    assert probe["phase"] == 3
    assert probe["phase3_selected_140"] is False
    assert probe["test_pdf_resolution"]["matched_in_repo"] == 380
    assert probe["test_pdf_resolution"]["missing"] == 0
    assert probe["path_mapping_rule"] == "repo_path = data/FinQA/{split}/{file_name}"


def test_phase3_profile_splits_unchanged() -> None:
    profile = json.loads(
        (project_root() / "data" / "processed" / "finqa_profile.json").read_text(encoding="utf-8")
    )
    assert profile["splits"] == {"train": 6251, "dev": 883, "test": 1147}
    assert profile["sampling_readiness"]["phase2_selected_140"] is False


def test_phase3_did_not_freeze_140() -> None:
    final_dir = project_root() / "data" / "final"
    assert not (final_dir / "selected_140_questions.csv").exists()
    assert not (final_dir / "sampling_manifest.json").exists()
