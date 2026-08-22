"""Tests for storage/backup/recovery configuration (project management — not RAG)."""

from __future__ import annotations

from pathlib import Path

from src.config import load_experiment_config, project_root


def test_storage_section_exists() -> None:
    cfg = load_experiment_config()
    storage = cfg.section("storage")
    assert storage.get("roles", {}).get("github") == "source_version_control"
    assert storage.get("roles", {}).get("google_drive") == "persistent_experiment_archive"
    assert storage.get("benchmark", {}).get("total_cases") == 420


def test_storage_benchmark_recovery_flags() -> None:
    recovery = load_experiment_config().section("storage").get("benchmark", {}).get("recovery", {})
    assert recovery.get("incremental_save") is True
    assert recovery.get("never_restart_from_question_1") is True
    assert recovery.get("duplicate_prevention") is True


def test_storage_raw_result_fields_non_empty() -> None:
    fields = load_experiment_config().section("storage").get("raw_result_fields", [])
    assert "run_id" in fields
    assert "question_id" in fields
    assert "architecture" in fields
    assert len(fields) >= 15


def test_storage_docs_and_rules_exist() -> None:
    root = project_root()
    assert (root / "docs" / "storage_backup_recovery.md").is_file()
    assert (root / "docs" / "IMPLEMENTATION_PLAN.md").is_file()
    assert (root / "project_record" / "PHASE_COMPLETION_BACKUP_TEMPLATE.md").is_file()
    repo_root = root.parent
    assert (repo_root / ".cursor" / "rules" / "06-storage-backup-recovery.mdc").is_file()


def test_storage_drive_layout_matches_spec() -> None:
    layout = load_experiment_config().section("storage").get("google_drive", {}).get("layout", {})
    for key in ("results_raw", "checkpoints", "logs", "configs", "artifacts"):
        assert key in layout
