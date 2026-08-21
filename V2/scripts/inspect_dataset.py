#!/usr/bin/env python3
"""Phase 2: load and profile T²-RAGBench FinQA. Does not select the frozen 140."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config, project_root
from src.data.profile_finqa import build_profile, load_finqa, save_profile
from src.utils import create_run_id, get_logger, setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile G4KMU/t2-ragbench FinQA")
    parser.add_argument(
        "--offline-ok",
        action="store_true",
        help="Allow using cached HF data if already downloaded",
    )
    args = parser.parse_args()
    _ = args  # reserved

    config = load_experiment_config()
    run_id = create_run_id("phase2")
    log_dir = get_path(config, "results_logs")
    setup_logging(level="INFO", log_dir=log_dir, run_id=run_id, console=True, file=True)
    log = get_logger(run_id=run_id, phase="phase2")

    log.info("Loading %s FinQA from Hugging Face", "G4KMU/t2-ragbench")
    ds = load_finqa()
    profile = build_profile(ds)
    paths = save_profile(
        profile,
        processed_dir=get_path(config, "data_processed"),
        docs_dir=project_root() / "docs",
    )
    log.info(
        "Profile saved json=%s markdown=%s splits=%s",
        paths["json"],
        paths["markdown"],
        profile["splits"],
    )
    print(json_summary(profile, paths))
    return 0


def json_summary(profile: dict, paths: dict) -> str:
    import json

    return json.dumps(
        {
            "splits": profile["splits"],
            "total_rows": profile["total_rows"],
            "can_support_140_from_test": profile["sampling_readiness"]["can_support_140_from_test"],
            "selected_140": profile["sampling_readiness"]["phase2_selected_140"],
            "outputs": {k: str(v) for k, v in paths.items()},
        },
        indent=2,
    )


if __name__ == "__main__":
    raise SystemExit(main())
