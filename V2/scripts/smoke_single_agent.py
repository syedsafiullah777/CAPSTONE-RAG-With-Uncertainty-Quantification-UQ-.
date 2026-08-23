#!/usr/bin/env python3
"""Phase 8 smoke: Single-Agent RAG on a small set of frozen questions."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config, project_root
from src.models.fingerprint import collect_fingerprint
from src.rag.single_agent import run_single_agent
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight
from src.utils import create_run_id, get_logger, setup_logging
from src.utils.evidence import ValidationRecord, summarize_environment


def _load_questions(csv_path: Path, limit: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "id": str(row.get("id") or ""),
                    "question": str(row.get("question") or ""),
                    "program_answer": str(row.get("program_answer") or ""),
                }
            )
            if len(rows) >= limit:
                break
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 8 Single-Agent RAG smoke")
    parser.add_argument("--backend", default=None, help="mock|ollama_dev|llama_cpp|transformers|auto")
    parser.add_argument("--limit", type=int, default=3, help="Number of frozen questions (small validation set)")
    parser.add_argument(
        "--questions-csv",
        default=None,
        help="CSV of questions (default: frozen 140; only first --limit used)",
    )
    parser.add_argument("--out-dir", default=None, help="Output directory under results/")
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip Chroma index preflight (not recommended for Colab smoke)",
    )
    args = parser.parse_args()

    config = load_experiment_config()
    run_id = create_run_id("phase8")
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=run_id,
        console=True,
        file=True,
    )
    log = get_logger(run_id=run_id, phase="phase8", architecture="single_agent")

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

    model_cfg = dict(config.section("model"))
    if args.backend:
        model_cfg["backend"] = args.backend

    csv_path = Path(args.questions_csv) if args.questions_csv else get_path(config, "data_final") / "selected_140_questions.csv"
    questions = _load_questions(csv_path, max(1, args.limit))
    if not questions:
        raise SystemExit(f"No questions loaded from {csv_path}")

    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))
    out_dir = Path(args.out_dir) if args.out_dir else get_path(config, "results_config")
    out_dir.mkdir(parents=True, exist_ok=True)

    fp_path = out_dir / "phase8_runtime_fingerprint.json"
    fp_path.write_text(json.dumps(fingerprint, indent=2) + "\n", encoding="utf-8")

    results: list[dict] = []
    failures = 0
    for row in questions:
        log.info("Running question_id=%s", row["id"])
        result = run_single_agent(
            row["question"],
            question_id=row["id"],
            reference_answer=row.get("program_answer"),
            config=config,
            backend_name=args.backend,
            run_id=run_id,
            fingerprint=fingerprint,
        )
        payload = result.to_dict()
        results.append(payload)
        if result.error or not result.answer.strip() or not result.retrieved_evidence:
            failures += 1
            log.info(
                "FAIL qid=%s error=%s n_evidence=%s answer_len=%s",
                row["id"],
                result.error,
                len(result.retrieved_evidence),
                len(result.answer or ""),
            )
        else:
            log.info(
                "OK qid=%s n_evidence=%s top_score=%.4f latency=%.2fs",
                row["id"],
                len(result.retrieved_evidence),
                result.retrieval_scores[0] if result.retrieval_scores else -1.0,
                result.latency_seconds,
            )

    raw_path = out_dir / "phase8_single_agent_smoke.json"
    smoke_payload = {
        "phase": 8,
        "run_id": run_id,
        "architecture": "single_agent",
        "backend": args.backend or model_cfg.get("backend"),
        "n_questions": len(questions),
        "n_failures": failures,
        "status": "PASS" if failures == 0 else "FAIL",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "fingerprint_path": str(fp_path.relative_to(project_root())),
        "cases": results,
    }
    raw_path.write_text(json.dumps(smoke_payload, indent=2) + "\n", encoding="utf-8")

    # Also write JSONL for schema compatibility
    jsonl_path = out_dir / "phase8_single_agent_smoke.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for case in results:
            handle.write(json.dumps(case) + "\n")

    validation = ValidationRecord(
        phase=8,
        test_name="phase8_single_agent_smoke",
        command=f"PYTHONPATH=. python scripts/smoke_single_agent.py --backend {args.backend or 'auto'} --limit {args.limit}",
        environment=summarize_environment(fingerprint),
        expected="Each case: non-empty retrieved_evidence, non-empty answer, no error",
        actual=f"n={len(questions)} failures={failures} status={smoke_payload['status']}",
        status="PASS" if failures == 0 else "FAIL",  # type: ignore[arg-type]
        error=None if failures == 0 else f"{failures} case(s) failed",
        output_path=str(raw_path.relative_to(project_root())),
        extra={
            "jsonl_path": str(jsonl_path.relative_to(project_root())),
            "case_ids": [c.get("case_key") for c in results],
            "evidence_md": "project_record/evidence/phase8_validation.md",
        },
    )
    val_path = out_dir / "phase8_smoke_test.json"
    val_path.write_text(json.dumps(validation.to_dict(), indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": smoke_payload["status"].lower(),
                "n_questions": len(questions),
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
