#!/usr/bin/env python3
"""Phase 4: freeze the FinQA test 140-question evaluation set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config, project_root
from src.data.profile_finqa import load_finqa
from src.data.select_140 import freeze_test_140
from src.utils import create_run_id, get_logger, setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze FinQA test 140-question set")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing freeze")
    args = parser.parse_args()

    config = load_experiment_config()
    run_id = create_run_id("phase4")
    log_dir = get_path(config, "results_logs")
    setup_logging(level="INFO", log_dir=log_dir, run_id=run_id, console=True, file=True)
    log = get_logger(run_id=run_id, phase="phase4")

    final_dir = get_path(config, "data_final")
    out_csv = final_dir / "selected_140_questions.csv"
    out_manifest = final_dir / "sampling_manifest.json"

    if out_csv.exists() and out_manifest.exists() and not args.force:
        log.info("Freeze already exists: %s (use --force to overwrite)", out_csv)
        print(json.dumps({"status": "exists", "csv": str(out_csv), "manifest": str(out_manifest)}, indent=2))
        return 0

    n = int(config.get("dataset", "frozen_test_size", default=140))
    seed = int(config.get("dataset", "sampling_seed", default=42))
    dataset_id = str(config.get("dataset", "huggingface_id", default="G4KMU/t2-ragbench"))
    subset = str(config.get("dataset", "subset", default="FinQA"))

    log.info("Loading %s %s test split for freeze n=%s seed=%s", dataset_id, subset, n, seed)
    ds = load_finqa()
    test_rows = [dict(row) for row in ds["test"]]
    result = freeze_test_140(
        test_rows,
        output_csv=out_csv,
        output_manifest=out_manifest,
        n=n,
        seed=seed,
        dataset_id=dataset_id,
        subset=subset,
    )
    manifest = result["manifest"]
    log.info(
        "Frozen n=%s companies=%s files=%s sha256=%s",
        manifest["n"],
        manifest["unique_companies"],
        manifest["unique_files"],
        manifest["selected_ids_sha256"],
    )
    print(
        json.dumps(
            {
                "status": "frozen",
                "n": manifest["n"],
                "seed": seed,
                "unique_companies": manifest["unique_companies"],
                "unique_files": manifest["unique_files"],
                "selected_ids_sha256": manifest["selected_ids_sha256"],
                "csv": str(out_csv),
                "manifest": str(out_manifest),
            },
            indent=2,
        )
    )
    # Touch a small pointer under results/config for reproducibility snapshots.
    snap = get_path(config, "results_config") / "phase4_sampling_manifest.json"
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
