"""Central configuration loader for V2.

Loads YAML from V2/config/. Values may be placeholders marked NEEDS_VERIFICATION
in experiment.yaml; this module does not invent unverified scientific settings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# V2 project root = parents: config/ -> src/ -> V2/
V2_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT_CONFIG = V2_ROOT / "config" / "experiment.yaml"
DEFAULT_PROMPTS_CONFIG = V2_ROOT / "config" / "prompts.yaml"


def project_root() -> Path:
    """Return the absolute path to the V2 project root."""
    return V2_ROOT


@dataclass(frozen=True)
class ExperimentConfig:
    """Immutable view of the loaded experiment configuration."""

    raw: dict[str, Any]
    source_path: Path

    def section(self, name: str) -> dict[str, Any]:
        value = self.raw.get(name, {})
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TypeError(f"Config section '{name}' must be a mapping, got {type(value)}")
        return value

    def get(self, *keys: str, default: Any = None) -> Any:
        node: Any = self.raw
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Configuration root must be a mapping: {path}")
    return data


def load_experiment_config(path: Path | None = None) -> ExperimentConfig:
    """Load experiment.yaml (or an override path)."""
    config_path = Path(path) if path is not None else DEFAULT_EXPERIMENT_CONFIG
    return ExperimentConfig(raw=_load_yaml(config_path), source_path=config_path.resolve())


def load_prompts_config(path: Path | None = None) -> dict[str, Any]:
    """Load prompts.yaml (placeholders in Phase 1)."""
    config_path = Path(path) if path is not None else DEFAULT_PROMPTS_CONFIG
    return _load_yaml(config_path)


def get_path(config: ExperimentConfig, key: str) -> Path:
    """Resolve a configured relative path against the V2 root."""
    paths = config.section("paths")
    if key not in paths:
        raise KeyError(f"Unknown path key '{key}'. Available: {sorted(paths)}")
    relative = Path(str(paths[key]))
    if relative.is_absolute():
        return relative
    return (V2_ROOT / relative).resolve()
