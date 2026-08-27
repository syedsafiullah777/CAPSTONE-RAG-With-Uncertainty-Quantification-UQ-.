"""Minimal Phase 1 health checks: config and environment load."""

from __future__ import annotations

from pathlib import Path

from src import __version__
from src.config import V2_ROOT, get_path, load_experiment_config, load_prompts_config, project_root
from src.utils import create_run_id, get_logger, setup_logging


def test_project_root_is_v2() -> None:
    root = project_root()
    assert root == V2_ROOT
    assert root.name == "V2"
    assert (root / "config" / "experiment.yaml").is_file()


def test_experiment_config_loads() -> None:
    config = load_experiment_config()
    assert config.get("project", "name") == "msc-rag-v2"
    assert config.get("dataset", "subset") == "FinQA"
    assert config.get("dataset", "frozen_test_size") == 140
    assert config.get("dataset", "total_cases") == 420
    assert config.get("model", "name") == "Qwen3-8B"
    # Threshold must not be invented in Phase 1.
    assert config.get("uncertainty", "confidence_threshold") is None


def test_standard_paths_resolve_under_v2() -> None:
    config = load_experiment_config()
    for key in (
        "data_final",
        "kb_index",
        "results_raw",
        "results_logs",
        "results_checkpoints",
        "results_metrics",
    ):
        path = get_path(config, key)
        assert path.is_absolute()
        assert V2_ROOT in path.parents or path == V2_ROOT
        assert str(path).startswith(str(V2_ROOT))


def test_prompts_config_loads() -> None:
    prompts = load_prompts_config()
    assert prompts.get("version")
    assert prompts.get("baseline", {}).get("system")
    assert "{evidence}" in str(prompts.get("baseline", {}).get("user_template") or "")
    assert "{question}" in str(prompts.get("baseline", {}).get("user_template") or "")


def test_run_id_and_logging() -> None:
    run_id = create_run_id("phase1")
    assert run_id.startswith("phase1_")
    logger = setup_logging(level="INFO", log_dir=None, console=True, file=False)
    adapter = get_logger(run_id=run_id, phase="phase1")
    adapter.info("phase1_health_check_ok")
    assert logger.name == "v2"
    assert __version__ == "0.1.0-phase1"


def test_v2_gitignore_exists() -> None:
    assert (V2_ROOT / ".gitignore").is_file()
