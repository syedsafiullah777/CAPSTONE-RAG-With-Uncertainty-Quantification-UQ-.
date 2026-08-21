#!/usr/bin/env python3
"""Phase 5: freeze FinQA DEV calibration questions (no threshold lock)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config
from src.data.profile_finqa import load_finqa
from src.data.select_calibration import freeze_calibration
from src.utils import create_run_id, get_logger, setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze FinQA DEV calibration set")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing freeze")
    args = parser.parse_args()

    config = load_experiment_config()
    run_id = create_run_id("phase5")
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=run_id,
        console=True,
        file=True,
    )
    log = get_logger(run_id=run_id, phase="phase5")

    cal_dir = get_path(config, "data_calibration")
    out_csv = cal_dir / "calibration_questions.csv"
    out_manifest = cal_dir / "calibration_manifest.json"
    test_csv = get_path(config, "data_final") / "selected_140_questions.csv"

    if out_csv.exists() and out_manifest.exists() and not args.force:
        log.info("Calibration freeze already exists: %s", out_csv)
        print(json.dumps({"status": "exists", "csv": str(out_csv), "manifest": str(out_manifest)}, indent=2))
        return 0

    n = int(config.get("dataset", "calibration_size", default=40))
    seed = int(config.get("dataset", "calibration_seed", default=42))
    dataset_id = str(config.get("dataset", "huggingface_id", default="G4KMU/t2-ragbench"))
    subset = str(config.get("dataset", "subset", default="FinQA"))

    log.info("Loading %s %s DEV for calibration freeze n=%s seed=%s", dataset_id, subset, n, seed)
    ds = load_finqa()
    dev_rows = [dict(row) for row in ds["dev"]]
    result = freeze_calibration(
        dev_rows,
        frozen_test_csv=test_csv,
        output_csv=out_csv,
        output_manifest=out_manifest,
        n=n,
        seed=seed,
        dataset_id=dataset_id,
        subset=subset,
    )
    manifest = result["manifest"]
    log.info(
        "Calibration frozen n=%s companies=%s files=%s sha256=%s threshold_locked=%s",
        manifest["n"],
        manifest["unique_companies"],
        manifest["unique_files"],
        manifest["selected_ids_sha256"],
        manifest["threshold_locked"],
    )
    snap = get_path(config, "results_config") / "phase5_calibration_manifest.json"
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "frozen",
                "n": manifest["n"],
                "seed": seed,
                "unique_companies": manifest["unique_companies"],
                "unique_files": manifest["unique_files"],
                "selected_ids_sha256": manifest["selected_ids_sha256"],
                "threshold_locked": False,
                "csv": str(out_csv),
                "manifest": str(out_manifest),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
