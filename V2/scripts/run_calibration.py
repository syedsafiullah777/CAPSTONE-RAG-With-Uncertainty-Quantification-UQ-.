#!/usr/bin/env python3
"""Phase 13: DEV calibration (40 questions, multi_agent_uq). Does not run the 420-case benchmark."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.calibration.data import CALIBRATION_N
from src.calibration.runner import run_calibration
from src.config import get_path, load_experiment_config, project_root
from src.models.fingerprint import collect_fingerprint
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight
from src.utils import setup_logging
from src.utils.evidence import ValidationRecord, summarize_environment


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 13 DEV calibration / threshold lock")
    parser.add_argument("--backend", default="mock", help="mock|ollama_dev|llama_cpp|transformers|auto")
    parser.add_argument("--n-questions", type=int, default=CALIBRATION_N)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--resume-latest", action="store_true")
    parser.add_argument("--no-retry-failed", action="store_true")
    parser.add_argument("--stop-after", type=int, default=None)
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--no-lock", action="store_true", help="Collect confidences only; do not write lock/candidate")
    args = parser.parse_args()

    if args.n_questions > CALIBRATION_N:
        raise SystemExit(
            f"Refusing --n-questions {args.n_questions}. Phase 13 cap is {CALIBRATION_N} DEV items."
        )

    config = load_experiment_config()
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=args.run_id or args.resume or "phase13",
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

    model_cfg = dict(config.section("model"))
    model_cfg["backend"] = args.backend
    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))

    summary = run_calibration(
        backend_name=args.backend,
        n_questions=args.n_questions,
        config=config,
        run_id=args.run_id,
        resume=args.resume,
        resume_latest=args.resume_latest,
        retry_failed=not args.no_retry_failed,
        stop_after=args.stop_after,
        fingerprint=fingerprint,
        write_lock=not args.no_lock,
    )

    out_dir = get_path(config, "results_config")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "phase13_runtime_fingerprint.json").write_text(
        json.dumps(fingerprint, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "phase13_calibration_summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    lock = summary.get("lock") or {}
    locked = bool(lock.get("locked"))
    expected = (
        f"{args.n_questions} FinQA DEV questions, architecture multi_agent_uq; "
        "T selected by max selective accuracy with coverage >= 0.50; "
        "official lock only on llama_cpp/CUDA"
    )
    validation = ValidationRecord(
        phase=13,
        test_name="phase13_calibration",
        command=f"PYTHONPATH=. python scripts/run_calibration.py --backend {args.backend} --n-questions {args.n_questions}",
        environment=summarize_environment(fingerprint),
        expected=expected,
        actual=(
            f"status={summary['status']} completed={summary['n_completed']} "
            f"locked={locked} T={lock.get('threshold')} note={lock.get('threshold_note')}"
        ),
        status="PASS" if summary["status"] == "PASS" else "FAIL",  # type: ignore[arg-type]
        error=None if summary["status"] == "PASS" else json.dumps(summary.get("failed") or {}),
        output_path=str(summary.get("raw_path")),
        extra={
            "run_id": summary["run_id"],
            "locked": locked,
            "threshold": lock.get("threshold"),
            "evidence_md": "project_record/evidence/phase13_validation.md",
        },
    )
    if summary["status"] == "INCOMPLETE":
        validation.status = "NEEDS_VERIFICATION"
        validation.error = "Calibration stopped before all DEV cases completed."
    (out_dir / "phase13_smoke_test.json").write_text(
        json.dumps(validation.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": summary["status"],
                "run_id": summary["run_id"],
                "n_completed": summary["n_completed"],
                "n_failed": summary["n_failed"],
                "n_pending": summary["n_pending"],
                "locked": locked,
                "threshold": lock.get("threshold"),
                "threshold_note": lock.get("threshold_note"),
                "raw_path": summary.get("raw_path"),
            },
            indent=2,
        )
    )
    if summary["status"] == "PASS":
        return 0
    if summary["status"] == "INCOMPLETE":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
