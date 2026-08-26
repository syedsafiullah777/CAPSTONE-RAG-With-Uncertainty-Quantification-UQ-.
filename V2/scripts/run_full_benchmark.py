#!/usr/bin/env python3
"""Phase 15: official 140 × 3 = 420 benchmark. Does not run the Phase 14 9-case validation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD, load_official_lock
from src.config import get_path, load_experiment_config, project_root
from src.models.fingerprint import collect_fingerprint
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight
from src.run.benchmark import (
    BENCHMARK_N_CASES,
    BENCHMARK_N_QUESTIONS,
    THRESHOLD_NOTE,
    run_benchmark,
    select_benchmark_questions,
)
from src.run.drive_sync import sync_benchmark_configs
from src.utils import setup_logging
from src.utils.evidence import ValidationRecord, summarize_environment


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 15 final benchmark (140 questions × 3 architectures = 420 cases; T=0.65 locked)"
    )
    parser.add_argument("--backend", default="llama_cpp", help="llama_cpp|transformers (mock refused)")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--resume", default=None, help="Resume this run_id")
    parser.add_argument("--resume-latest", action="store_true")
    parser.add_argument("--no-retry-failed", action="store_true")
    parser.add_argument("--stop-after", type=int, default=None, help="Execute at most N new cases then stop")
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--no-drive-sync", action="store_true")
    args = parser.parse_args()

    if str(args.backend).lower() in {"mock", "test"}:
        raise SystemExit("Phase 15 refuses a mock backend. Use llama_cpp on Colab GPU.")

    config = load_experiment_config()
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=args.run_id or args.resume or "phase15",
        console=True,
        file=True,
    )

    lock = load_official_lock()
    if abs(float(lock["threshold"]) - EXPECTED_LOCKED_THRESHOLD) > 1e-9:
        raise SystemExit("Locked T is not 0.65. Do not recalibrate.")

    retrieval_cfg = config.section("retrieval")
    index_dir = get_path(config, "kb_index")
    manifest_rel = str(retrieval_cfg.get("index_manifest") or "knowledge_base/index/index_manifest.json")
    manifest_file = (project_root() / manifest_rel).resolve()
    collection_name = str(retrieval_cfg.get("collection_name") or COLLECTION_NAME)

    if not args.skip_preflight:
        try:
            preflight = validate_index_preflight(
                index_dir,
                manifest_path=manifest_file,
                collection_name=collection_name,
            )
            print(
                json.dumps(
                    {
                        "index_preflight": "PASS",
                        "expected_chunks": preflight["expected_chunks"],
                        "actual_count": preflight["actual_count"],
                    }
                )
            )
        except IndexPreflightError as exc:
            raise SystemExit(f"Index preflight FAIL: {exc}") from exc

    if args.backend == "llama_cpp" and os.environ.get("V2_REQUIRE_CUDA", "1") == "1":
        from src.models.runtime_guard import verify_live_llama_cpp_runtime

        runtime = verify_live_llama_cpp_runtime(require_cuda=True)
        print(json.dumps({"runtime_lock": runtime}, indent=2))

    select_benchmark_questions(n=BENCHMARK_N_QUESTIONS, allow_full=True, config=config)

    model_cfg = dict(config.section("model"))
    model_cfg["backend"] = args.backend
    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))

    summary = run_benchmark(
        backend_name=args.backend,
        n_questions=BENCHMARK_N_QUESTIONS,
        allow_full=True,
        config=config,
        run_id=args.run_id,
        resume=args.resume,
        resume_latest=args.resume_latest,
        retry_failed=not args.no_retry_failed,
        stop_after=args.stop_after,
        skip_preflight=args.skip_preflight,
        fingerprint=fingerprint,
        sync_drive=not args.no_drive_sync,
    )

    out_dir = get_path(config, "results_config")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "phase15_runtime_fingerprint.json").write_text(
        json.dumps(fingerprint, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "phase15_benchmark_summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    expected = (
        f"{BENCHMARK_N_QUESTIONS} frozen test questions × 3 independent architectures "
        f"= {BENCHMARK_N_CASES} cases; locked T={EXPECTED_LOCKED_THRESHOLD}; "
        "incremental JSONL + Drive checkpoint/resume"
    )
    validation = ValidationRecord(
        phase=15,
        test_name="phase15_full_benchmark",
        command=f"PYTHONPATH=. python scripts/run_full_benchmark.py --backend {args.backend}",
        environment=summarize_environment(fingerprint),
        expected=expected,
        actual=(
            f"status={summary['status']} completed={summary['n_completed']} "
            f"failed={summary['n_failed']} pending={summary['n_pending']} "
            f"threshold={summary['threshold']} locked={summary['threshold_locked']} "
            f"n_cases={summary.get('n_cases')}"
        ),
        status="PASS" if summary["status"] == "PASS" else "FAIL",  # type: ignore[arg-type]
        error=None if summary["status"] == "PASS" else json.dumps(summary.get("failed") or {}),
        output_path=str(summary.get("raw_path")),
        extra={
            "run_id": summary["run_id"],
            "threshold_note": THRESHOLD_NOTE,
            "evidence_md": "project_record/evidence/phase15_validation.md",
            "n_planned": BENCHMARK_N_CASES,
        },
    )
    if summary["status"] == "INCOMPLETE":
        validation.status = "NEEDS_VERIFICATION"
        validation.error = "Benchmark stopped before all 420 cases completed (resume available)."
    (out_dir / "phase15_smoke_test.json").write_text(
        json.dumps(validation.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    drive_cfg = (
        sync_benchmark_configs(out_dir, job="phase15_benchmark")
        if not args.no_drive_sync
        else {"synced": False, "reason": "disabled"}
    )
    print(json.dumps({"drive_configs": drive_cfg}, indent=2))

    print(json.dumps({k: summary[k] for k in (
        "status",
        "phase",
        "run_id",
        "n_questions",
        "n_cases",
        "n_completed",
        "n_failed",
        "n_pending",
        "executed_this_session",
        "skipped_this_session",
        "threshold",
        "threshold_locked",
        "threshold_note",
        "raw_path",
        "drive_sync",
    ) if k in summary}, indent=2))
    if summary["status"] == "PASS":
        return 0
    if summary["status"] == "INCOMPLETE":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
