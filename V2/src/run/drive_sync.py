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


def _job_rels(job: str) -> tuple[str, str, str]:
    """Return (raw_rel, checkpoint_rel, config_rel) under the Drive root."""
    name = job.strip("/") or "phase14_benchmark"
    if name.startswith("phase16"):
        phase = "phase16"
    elif name.startswith("phase15"):
        phase = "phase15"
    else:
        phase = "phase14"
    return f"results/raw/{name}", f"checkpoints/{name}", f"configs/{phase}"


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
    job: str = "phase14_benchmark",
) -> dict[str, Any]:
    """Copy raw JSONL + checkpoint into Drive. No-op if Drive is absent."""
    root = drive_root()
    if root is None:
        return {"synced": False, "reason": "Drive root not mounted"}
    raw_rel, ckpt_rel, _cfg_rel = _job_rels(job)
    dest = root / raw_rel / run_id
    dest.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for name in ("cases.jsonl", "judge.jsonl", "checkpoint.json", "summary.json"):
        src = Path(run_dir) / name
        if src.is_file():
            shutil.copy2(src, dest / name)
            copied.append(name)
    if checkpoint_copy is not None and Path(checkpoint_copy).is_file():
        ckpt_dest = root / ckpt_rel
        ckpt_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(checkpoint_copy, ckpt_dest / Path(checkpoint_copy).name)
        copied.append(f"checkpoint_copy:{Path(checkpoint_copy).name}")
    return {"synced": True, "dest": str(dest), "copied": copied, "job": job}


def sync_benchmark_configs(config_dir: Path, *, job: str = "phase14_benchmark") -> dict[str, Any]:
    root = drive_root()
    if root is None:
        return {"synced": False, "reason": "Drive root not mounted"}
    _raw_rel, _ckpt_rel, config_rel = _job_rels(job)
    dest = root / config_rel
    dest.mkdir(parents=True, exist_ok=True)
    if job.startswith("phase16"):
        phase = "phase16"
    elif job.startswith("phase15"):
        phase = "phase15"
    else:
        phase = "phase14"
    copied: list[str] = []
    names = [
        f"{phase}_runtime_fingerprint.json",
        f"{phase}_smoke_test.json",
        f"{phase}_benchmark_summary.json",
        "threshold.lock.json",
    ]
    if phase == "phase16":
        names.extend(
            [
                "phase16_judge_summary.json",
                "phase16_judge_smoke_test.json",
            ]
        )
    for name in names:
        src = Path(config_dir) / name
        if src.is_file():
            shutil.copy2(src, dest / name)
            copied.append(name)
    return {"synced": True, "dest": str(dest), "copied": copied, "job": job}
