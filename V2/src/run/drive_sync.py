"""Optional Google Drive persistence for benchmark checkpoints and raw JSONL.

Colab notebooks set ``V2_DRIVE_ROOT=/content/drive/MyDrive/MSc-RAG``.
Local runs skip sync when Drive is not mounted. Never treats missing Drive as PASS.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any


DRIVE_ENV = "V2_DRIVE_ROOT"
DEFAULT_COLAB_DRIVE = Path("/content/drive/MyDrive/MSc-RAG")
RAW_REL = "results/raw/phase14_benchmark"
CHECKPOINT_REL = "checkpoints/phase14_benchmark"
CONFIG_REL = "configs/phase14"


def drive_root() -> Path | None:
    env = (os.environ.get(DRIVE_ENV) or "").strip()
    if env:
        path = Path(env)
        return path if path.is_dir() else None
    if DEFAULT_COLAB_DRIVE.is_dir():
        return DEFAULT_COLAB_DRIVE
    return None


def sync_benchmark_run(
    run_dir: Path,
    *,
    run_id: str,
    checkpoint_copy: Path | None = None,
) -> dict[str, Any]:
    """Copy raw JSONL + checkpoint into Drive. No-op if Drive is absent."""
    root = drive_root()
    if root is None:
        return {"synced": False, "reason": "Drive root not mounted"}
    dest = root / RAW_REL / run_id
    dest.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for name in ("cases.jsonl", "checkpoint.json", "summary.json"):
        src = Path(run_dir) / name
        if src.is_file():
            shutil.copy2(src, dest / name)
            copied.append(name)
    if checkpoint_copy is not None and Path(checkpoint_copy).is_file():
        ckpt_dest = root / CHECKPOINT_REL
        ckpt_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(checkpoint_copy, ckpt_dest / Path(checkpoint_copy).name)
        copied.append(f"checkpoint_copy:{Path(checkpoint_copy).name}")
    return {"synced": True, "dest": str(dest), "copied": copied}


def sync_benchmark_configs(config_dir: Path) -> dict[str, Any]:
    root = drive_root()
    if root is None:
        return {"synced": False, "reason": "Drive root not mounted"}
    dest = root / CONFIG_REL
    dest.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for name in (
        "phase14_runtime_fingerprint.json",
        "phase14_smoke_test.json",
        "phase14_benchmark_summary.json",
        "threshold.lock.json",
    ):
        src = Path(config_dir) / name
        if src.is_file():
            shutil.copy2(src, dest / name)
            copied.append(name)
    return {"synced": True, "dest": str(dest), "copied": copied}
