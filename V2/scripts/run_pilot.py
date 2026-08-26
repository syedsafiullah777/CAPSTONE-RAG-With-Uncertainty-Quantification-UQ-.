#!/usr/bin/env python3
"""Phase 12 pilot: 6 frozen questions × 3 architectures = 18 resumable cases."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config, project_root
from src.models.fingerprint import collect_fingerprint
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight
from src.run.pilot import run_pilot
from src.run.subset import (
    PILOT_N_CASES,
    PILOT_N_QUESTIONS,
    THRESHOLD_NOTE,
    select_pilot_questions,
    write_pilot_manifest,
)
from src.utils import setup_logging
from src.utils.evidence import ValidationRecord, summarize_environment


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 12 pilot (18 cases; threshold NOT LOCKED)")
    parser.add_argument("--backend", default="mock", help="mock|ollama_dev|llama_cpp|transformers|auto")
    parser.add_argument(
        "--n-questions",
        type=int,
        default=PILOT_N_QUESTIONS,
        help=f"Pilot questions from the frozen 140 (max {PILOT_N_QUESTIONS})",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--resume", default=None, help="Resume this run_id")
    parser.add_argument("--resume-latest", action="store_true")
    parser.add_argument("--no-retry-failed", action="store_true")
    parser.add_argument("--stop-after", type=int, default=None, help="Execute at most N new cases then stop")
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()

    if args.n_questions > PILOT_N_QUESTIONS:
        raise SystemExit(
            f"Refusing --n-questions {args.n_questions}. Phase 12 cap is {PILOT_N_QUESTIONS} "
            f"({PILOT_N_CASES} cases). Do not run the 420-case benchmark from this script."
        )

    config = load_experiment_config()
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=args.run_id or args.resume or "phase12",
        console=True,
        file=True,
    )

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

    questions = select_pilot_questions(n=args.n_questions, config=config)
    write_pilot_manifest(questions)

    model_cfg = dict(config.section("model"))
    model_cfg["backend"] = args.backend
    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))

    summary = run_pilot(
        backend_name=args.backend,
        n_questions=args.n_questions,
        config=config,
        run_id=args.run_id,
        resume=args.resume,
        resume_latest=args.resume_latest,
        retry_failed=not args.no_retry_failed,
        stop_after=args.stop_after,
        skip_preflight=args.skip_preflight,
        fingerprint=fingerprint,
    )

    out_dir = get_path(config, "results_config")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "phase12_runtime_fingerprint.json").write_text(
        json.dumps(fingerprint, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "phase12_pilot_summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    expected = (
        f"{args.n_questions} frozen questions × 3 independent architectures; "
        f"raw JSONL + checkpoint/resume; threshold 0.55 {THRESHOLD_NOTE}"
    )
    validation = ValidationRecord(
        phase=12,
        test_name="phase12_pilot",
        command=f"PYTHONPATH=. python scripts/run_pilot.py --backend {args.backend} --n-questions {args.n_questions}",
        environment=summarize_environment(fingerprint),
        expected=expected,
        actual=(
            f"status={summary['status']} completed={summary['n_completed']} "
            f"failed={summary['n_failed']} pending={summary['n_pending']} "
            f"threshold={summary['threshold']} locked={summary['threshold_locked']}"
        ),
        status="PASS" if summary["status"] == "PASS" else "FAIL",  # type: ignore[arg-type]
        error=None if summary["status"] == "PASS" else json.dumps(summary.get("failed") or {}),
        output_path=str(summary.get("raw_path")),
        extra={
            "run_id": summary["run_id"],
            "threshold_note": THRESHOLD_NOTE,
            "evidence_md": "project_record/evidence/phase12_validation.md",
        },
    )
    if summary["status"] == "INCOMPLETE":
        validation.status = "NEEDS_VERIFICATION"
        validation.error = "Pilot stopped before all 18 cases completed (resume available)."
    (out_dir / "phase12_smoke_test.json").write_text(
        json.dumps(validation.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({k: summary[k] for k in (
        "status",
        "run_id",
        "n_completed",
        "n_failed",
        "n_pending",
        "executed_this_session",
        "skipped_this_session",
        "threshold",
        "threshold_locked",
        "threshold_note",
        "raw_path",
    ) if k in summary}, indent=2))
    if summary["status"] == "PASS":
        return 0
    if summary["status"] == "INCOMPLETE":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
