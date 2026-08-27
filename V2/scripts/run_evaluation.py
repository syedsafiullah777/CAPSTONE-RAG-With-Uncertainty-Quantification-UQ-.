#!/usr/bin/env python3
"""Phase 16: CPU evaluation of saved Phase 15 420-case results. No RAG/Qwen rerun."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD, load_official_lock
from src.config import get_path, load_experiment_config
from src.evaluation.runner import run_evaluation
from src.utils import setup_logging
from src.utils.evidence import ValidationRecord


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 16 CPU metrics from Phase 15 JSONL (no LLM)")
    parser.add_argument(
        "--raw",
        default=None,
        help="Path to Phase 15 cases.jsonl (default: canonical 420-case run)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing processed outputs")
    args = parser.parse_args()

    config = load_experiment_config()
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id="phase16",
        console=True,
        file=True,
    )
    lock = load_official_lock()
    if abs(float(lock["threshold"]) - EXPECTED_LOCKED_THRESHOLD) > 1e-9:
        raise SystemExit("Locked T is not 0.65. Do not recalibrate.")

    raw = Path(args.raw) if args.raw else None
    summary = run_evaluation(raw_path=raw, config=config, force=args.force)
    out_dir = get_path(config, "results_config")
    record = ValidationRecord(
        phase=16,
        test_name="phase16_evaluation",
        command="PYTHONPATH=. python scripts/run_evaluation.py",
        environment={"used_llm_inference": False, "used_gpu": False, "device": "cpu"},
        expected="Score all 420 saved cases on CPU; no RAG/Qwen; T=0.65 unchanged",
        actual=(
            f"status={summary['status']} n_cases={summary['n_cases']} "
            f"used_llm={summary['used_llm_inference']} raw_unchanged={summary['raw_unchanged']}"
        ),
        status="PASS" if summary["status"] == "PASS" else "FAIL",
        output_path=str(summary.get("processed_path")),
        extra={
            "source_raw_sha256": summary.get("source_raw_sha256"),
            "metrics_csv": summary.get("metrics_csv"),
            "evidence_md": "project_record/evidence/phase16_validation.md",
        },
    )
    (out_dir / "phase16_smoke_test.json").write_text(
        json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: summary[k] for k in (
        "status",
        "phase",
        "run_id",
        "n_cases",
        "used_llm_inference",
        "used_gpu",
        "used_rag_rerun",
        "raw_unchanged",
        "source_raw_sha256",
        "processed_path",
        "metrics_csv",
        "metrics_json",
    ) if k in summary}, indent=2))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
