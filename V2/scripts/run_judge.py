#!/usr/bin/env python3
"""Phase 16 post-hoc LLM-as-judge faithfulness over frozen Phase 15 cases.

Does not rerun RAG or rewrite Phase 15 JSONL / Phase 16 CPU metrics.
Official: 420 cases, llama_cpp, Colab GPU.
Local smoke: --backend mock --n-cases 3
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config
from src.evaluation.judge import METRIC_LABEL
from src.evaluation.judge_runner import BENCHMARK_N_CASES, run_judge
from src.evaluation.runner import EXPECTED_RAW_SHA256
from src.models.fingerprint import collect_fingerprint
from src.utils import setup_logging
from src.utils.evidence import ValidationRecord, summarize_environment


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 16 post-hoc LLM-as-judge faithfulness (frozen Phase 15 JSONL; no RAG rerun)"
    )
    parser.add_argument("--backend", default="llama_cpp", help="llama_cpp (official) or mock (local smoke only)")
    parser.add_argument("--n-cases", type=int, default=BENCHMARK_N_CASES)
    parser.add_argument("--raw", default=None, help="Path to Phase 15 cases.jsonl")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--resume-latest", action="store_true")
    parser.add_argument("--no-retry-failed", action="store_true")
    parser.add_argument("--stop-after", type=int, default=None)
    parser.add_argument("--no-drive-sync", action="store_true")
    args = parser.parse_args()

    config = load_experiment_config()
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=args.run_id or args.resume or "phase16_judge",
        console=True,
        file=True,
    )

    if str(args.backend).lower() in {"llama_cpp", "llamacpp", "gguf", "colab"}:
        os.environ.setdefault("V2_REQUIRE_CUDA", "1")
        os.environ.setdefault("V2_FORBID_MOCK", "1")

    model_cfg = dict(config.section("model"))
    model_cfg["backend"] = args.backend
    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(V2_ROOT))

    raw = Path(args.raw) if args.raw else None
    summary = run_judge(
        backend_name=args.backend,
        n_cases=args.n_cases,
        config=config,
        raw_path=raw,
        run_id=args.run_id,
        resume=args.resume,
        resume_latest=args.resume_latest,
        retry_failed=not args.no_retry_failed,
        stop_after=args.stop_after,
        fingerprint=fingerprint,
        sync_drive=not args.no_drive_sync,
    )

    out_dir = get_path(config, "results_config")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "phase16_judge_runtime_fingerprint.json").write_text(
        json.dumps(fingerprint, indent=2) + "\n", encoding="utf-8"
    )
    record = ValidationRecord(
        phase=16,
        test_name="phase16_judge_faithfulness",
        command="PYTHONPATH=. python scripts/run_judge.py --backend llama_cpp",
        environment=summarize_environment(fingerprint),
        expected=(
            f"{BENCHMARK_N_CASES} post-hoc judge cases on frozen Phase 15 JSONL; "
            f"SHA {EXPECTED_RAW_SHA256}; {METRIC_LABEL}; no RAG rerun"
        ),
        actual=(
            f"status={summary['status']} completed={summary.get('n_completed')} "
            f"failed={summary.get('n_failed')} pending={summary.get('n_pending')} "
            f"used_rag_rerun={summary.get('used_rag_rerun')} "
            f"source_unchanged={summary.get('source_raw_unchanged')}"
        ),
        status="PASS" if summary["status"] == "PASS" else "FAIL",  # type: ignore[arg-type]
        output_path=str(summary.get("raw_path")),
        extra={
            "run_id": summary.get("run_id"),
            "metric_label": METRIC_LABEL,
            "n_planned": summary.get("n_planned"),
            "evidence_md": "project_record/evidence/phase16_validation.md",
        },
    )
    if summary["status"] == "INCOMPLETE":
        record.status = "NEEDS_VERIFICATION"
        record.error = "Judge stopped before all planned cases completed (resume available)."
    (out_dir / "phase16_judge_smoke_test.json").write_text(
        json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps({k: summary[k] for k in (
        "status",
        "phase",
        "mode",
        "run_id",
        "n_planned",
        "n_completed",
        "n_failed",
        "n_pending",
        "n_parse_failure",
        "executed_this_session",
        "skipped_this_session",
        "used_rag_rerun",
        "source_raw_sha256",
        "source_raw_unchanged",
        "metric_label",
        "raw_path",
        "metrics_csv",
        "drive_sync",
    ) if k in summary}, indent=2))
    if summary["status"] == "PASS":
        return 0
    if summary["status"] == "INCOMPLETE":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
