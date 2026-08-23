#!/usr/bin/env python3
"""Phase 11 smoke: live artefact runner on one frozen case + one fresh question."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config, project_root
from src.models.fingerprint import collect_fingerprint
from src.rag.live import LIVE_ARCHITECTURES, load_frozen_questions, run_live_comparison
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight
from src.utils import create_run_id, get_logger, setup_logging
from src.utils.evidence import ValidationRecord, summarize_environment

FRESH_QUESTION = (
    "Based on the Snap-on five-year stock performance graph, what was the "
    "S&P 500 cumulative value at the end of 2010 if $100 was invested at the end of 2008?"
)


def _comparison_failed(comparison) -> bool:
    if comparison.error:
        return True
    if set(comparison.results) != set(LIVE_ARCHITECTURES):
        return True
    for result in comparison.results.values():
        if result.error:
            return True
        if not result.retrieved_evidence:
            return True
        if not (result.answer or "").strip():
            return True
        if result.question != comparison.question:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 11 live artefact smoke")
    parser.add_argument("--backend", default="mock", help="mock|ollama_dev|llama_cpp|transformers|auto")
    parser.add_argument(
        "--fresh-only",
        action="store_true",
        help="Run one fresh question only (Colab live validation; no 140-question benchmark)",
    )
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()

    config = load_experiment_config()
    run_id = create_run_id("phase11")
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=run_id,
        console=True,
        file=True,
    )
    log = get_logger(run_id=run_id, phase="phase11", architecture="live")

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
            log.info(
                "Index preflight PASS expected=%s actual=%s",
                preflight["expected_chunks"],
                preflight["actual_count"],
            )
        except IndexPreflightError as exc:
            log.error("Index preflight FAIL: %s", exc)
            raise SystemExit(str(exc)) from exc

    frozen = load_frozen_questions(limit=1)
    if not frozen:
        raise SystemExit("Frozen 140 CSV produced no questions")
    frozen_row = frozen[0]

    model_cfg = dict(config.section("model"))
    model_cfg["backend"] = args.backend
    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))

    jobs = []
    if not args.fresh_only:
        jobs.append(
            {
                "question": frozen_row["question"],
                "question_id": frozen_row["id"],
                "question_source": "frozen",
                "reference_answer": frozen_row.get("program_answer"),
            }
        )
    jobs.append(
        {
            "question": FRESH_QUESTION,
            "question_id": None,
            "question_source": "fresh",
            "reference_answer": None,
        }
    )

    comparisons = []
    failures = 0
    for job in jobs:
        log.info("Live comparison source=%s qid=%s", job["question_source"], job["question_id"] or "fresh")
        comparison = run_live_comparison(
            job["question"],
            question_id=job["question_id"],
            question_source=job["question_source"],
            reference_answer=job.get("reference_answer"),
            config=config,
            backend_name=args.backend,
            run_id=run_id,
            fingerprint=fingerprint,
        )
        comparisons.append(comparison.to_dict())
        if _comparison_failed(comparison):
            failures += 1
            log.info("FAIL source=%s error=%s", job["question_source"], comparison.error)
        else:
            for architecture, result in comparison.results.items():
                log.info(
                    "OK source=%s arch=%s n_evidence=%s decision=%s latency=%.2fs",
                    job["question_source"],
                    architecture,
                    len(result.retrieved_evidence),
                    result.decision,
                    result.latency_seconds,
                )

    out_dir = get_path(config, "results_config")
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "phase11_live_smoke.json"
    smoke_payload = {
        "phase": 11,
        "run_id": run_id,
        "backend": args.backend,
        "n_comparisons": len(comparisons),
        "n_architectures": len(LIVE_ARCHITECTURES),
        "n_failures": failures,
        "status": "PASS" if failures == 0 else "FAIL",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "comparisons": comparisons,
    }
    raw_path.write_text(json.dumps(smoke_payload, indent=2) + "\n", encoding="utf-8")

    validation = ValidationRecord(
        phase=11,
        test_name="phase11_live_artefact_smoke",
        command=(
            f"PYTHONPATH=. python scripts/smoke_live_artefact.py --backend {args.backend}"
            + (" --fresh-only" if args.fresh_only else "")
        ),
        environment=summarize_environment(fingerprint),
        expected=(
            "1 fresh question through 3 independent architectures with evidence and answers"
            if args.fresh_only
            else "1 frozen + 1 fresh question; each runs 3 independent architectures with evidence and answers"
        ),
        actual=f"n={len(comparisons)} failures={failures} status={smoke_payload['status']}",
        status="PASS" if failures == 0 else "FAIL",  # type: ignore[arg-type]
        error=None if failures == 0 else f"{failures} comparison(s) failed",
        output_path=str(raw_path.relative_to(project_root())),
        extra={"evidence_md": "project_record/evidence/phase11_validation.md"},
    )
    val_path = out_dir / "phase11_smoke_test.json"
    val_path.write_text(json.dumps(validation.to_dict(), indent=2) + "\n", encoding="utf-8")
    (out_dir / "phase11_runtime_fingerprint.json").write_text(
        json.dumps(fingerprint, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": smoke_payload["status"].lower(),
                "n_comparisons": len(comparisons),
                "n_failures": failures,
                "out": str(raw_path),
                "validation": str(val_path),
            },
            indent=2,
        )
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
