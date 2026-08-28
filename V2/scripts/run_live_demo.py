#!/usr/bin/env python3
"""Phase 20 live-artefact demo: three questions × three independent architectures.

Does not rerun the 420-case benchmark, calibration, judge, or statistics.
Does not modify the frozen 140/40, T=0.65 lock, or Phase 15–18 result files.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD
from src.config import get_path, load_experiment_config, project_root
from src.evaluation.runner import sha256_file
from src.models.fingerprint import collect_fingerprint
from src.models.runtime_guard import mock_forbidden, verify_live_llama_cpp_runtime
from src.rag.live import (
    FRESH_KB_QUESTION,
    INSUFFICIENT_EVIDENCE_QUESTION,
    INSUFFICIENT_EVIDENCE_QUESTION_ID,
    KNOWN_GOOD_QUESTION_ID,
    LIVE_ARCHITECTURES,
    format_confidence_display,
    format_threshold_display,
    load_frozen_questions,
    resolve_live_locked_threshold,
    run_live_comparison,
)
from src.rag.schema import ARCHITECTURE_MULTI_AGENT_UQ, RAGCaseResult
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight
from src.statistics.constants import (
    CAL_40_REL,
    EXPECTED_CAL40_SHA256,
    EXPECTED_FROZEN140_SHA256,
    EXPECTED_JUDGE_SHA256,
    EXPECTED_LOCK_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
    FROZEN_140_REL,
    JUDGE_REL,
    LOCK_REL,
    PHASE15_REL,
    PROCESSED_REL,
)
from src.utils import create_run_id, get_logger, setup_logging
from src.utils.evidence import ValidationRecord, summarize_environment

PINNED = {
    PHASE15_REL: EXPECTED_PHASE15_SHA256,
    PROCESSED_REL: EXPECTED_PROCESSED_SHA256,
    JUDGE_REL: EXPECTED_JUDGE_SHA256,
    FROZEN_140_REL: EXPECTED_FROZEN140_SHA256,
    CAL_40_REL: EXPECTED_CAL40_SHA256,
    LOCK_REL: EXPECTED_LOCK_SHA256,
}


def _hashes(root: Path) -> dict[str, str]:
    return {rel: sha256_file(root / rel) for rel in PINNED}


def _assert_pins(observed: dict[str, str], label: str) -> None:
    for rel, expected in PINNED.items():
        got = observed.get(rel)
        if got != expected:
            raise RuntimeError(f"{label}: SHA-256 mismatch for {rel}: {got} != {expected}")


def _live_source_forbids_benchmark_lookup() -> None:
    forbidden = ("phase15_benchmark", "cases.jsonl", "phase16_cases.jsonl", "judge.jsonl")
    for rel in ("src/rag/live.py", "app/streamlit_app.py"):
        text = (project_root() / rel).read_text(encoding="utf-8")
        tree = ast.parse(text)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
            elif isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
        if imported & {"src.run.benchmark", "src.evaluation.runner"}:
            raise RuntimeError(f"{rel} must not import the benchmark/evaluation stack")
        for token in forbidden:
            if token in text:
                raise RuntimeError(f"{rel} must not reference {token} (no benchmark lookup)")


def _summarize_comparison(payload: dict) -> dict:
    uq_raw = (payload.get("results") or {}).get(ARCHITECTURE_MULTI_AGENT_UQ) or {}
    uq = RAGCaseResult(**uq_raw) if uq_raw else None
    per_arch = {}
    for name in LIVE_ARCHITECTURES:
        case = (payload.get("results") or {}).get(name) or {}
        per_arch[name] = {
            "decision": case.get("decision"),
            "n_evidence": len(case.get("retrieved_evidence") or []),
            "has_answer": bool((case.get("answer") or "").strip()),
            "error": case.get("error"),
            "backend": case.get("backend"),
            "device": case.get("device"),
            "gpu": case.get("gpu"),
            "latency_seconds": case.get("latency_seconds"),
            "verification_status": ((case.get("verification_result") or {}).get("status")),
            "confidence": case.get("confidence"),
            "threshold": case.get("threshold"),
        }
    return {
        "question_id": payload.get("question_id"),
        "question_source": payload.get("question_source"),
        "question": payload.get("question"),
        "used_precomputed_benchmark_lookup": payload.get("used_precomputed_benchmark_lookup"),
        "locked_threshold": payload.get("locked_threshold"),
        "uq_displayed_confidence": format_confidence_display(uq) if uq else None,
        "uq_displayed_threshold": format_threshold_display(uq) if uq else None,
        "architectures": per_arch,
        "n_architectures": len(payload.get("results") or {}),
        "independent_same_question": all(
            ((payload.get("results") or {}).get(name) or {}).get("question") == payload.get("question")
            for name in LIVE_ARCHITECTURES
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 20 live artefact validation")
    parser.add_argument("--backend", default="mock", help="mock|ollama_dev|llama_cpp|auto")
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()

    root = project_root()
    config = load_experiment_config()
    run_id = create_run_id("phase20")
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=run_id,
        console=True,
        file=True,
    )
    log = get_logger(run_id=run_id, phase="phase20", architecture="live")

    hashes_before = _hashes(root)
    _assert_pins(hashes_before, "before live demo")
    _live_source_forbids_benchmark_lookup()
    locked_t = resolve_live_locked_threshold()
    if abs(locked_t - EXPECTED_LOCKED_THRESHOLD) > 1e-9:
        raise RuntimeError("Locked T is not 0.65")

    retrieval_cfg = config.section("retrieval")
    index_dir = get_path(config, "kb_index")
    manifest_file = (
        root / str(retrieval_cfg.get("index_manifest") or "knowledge_base/index/index_manifest.json")
    ).resolve()
    if not args.skip_preflight:
        try:
            preflight = validate_index_preflight(
                index_dir,
                manifest_path=manifest_file,
                collection_name=str(retrieval_cfg.get("collection_name") or COLLECTION_NAME),
            )
            log.info("Index preflight PASS chunks=%s", preflight["actual_count"])
        except IndexPreflightError as exc:
            raise SystemExit(str(exc)) from exc

    if mock_forbidden() and str(args.backend).lower() in {"mock", "test"}:
        raise SystemExit("Mock backend is forbidden for this live demo. Use --backend llama_cpp.")
    runtime_lock = None
    if mock_forbidden() or str(args.backend).lower() == "llama_cpp":
        runtime_lock = verify_live_llama_cpp_runtime(
            require_cuda=os.environ.get("V2_REQUIRE_CUDA", "1") == "1"
        )
        args.backend = "llama_cpp"

    frozen_rows = load_frozen_questions()
    known_good = next((row for row in frozen_rows if row["id"] == KNOWN_GOOD_QUESTION_ID), None)
    if known_good is None:
        raise SystemExit(f"Frozen question {KNOWN_GOOD_QUESTION_ID} missing")
    frozen_questions = {row["question"] for row in frozen_rows}
    if FRESH_KB_QUESTION in frozen_questions:
        raise SystemExit("Fresh KB question collided with the frozen 140")
    if INSUFFICIENT_EVIDENCE_QUESTION in frozen_questions:
        raise SystemExit("Insufficient-evidence question collided with the frozen 140")

    model_cfg = dict(config.section("model"))
    model_cfg["backend"] = args.backend
    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(root))

    jobs = [
        {
            "label": "known_good",
            "question": known_good["question"],
            "question_id": known_good["id"],
            "question_source": "frozen",
            "reference_answer": known_good.get("program_answer"),
        },
        {
            "label": "fresh_kb",
            "question": FRESH_KB_QUESTION,
            "question_id": None,
            "question_source": "fresh",
            "reference_answer": None,
        },
        {
            "label": "insufficient_evidence",
            "question": INSUFFICIENT_EVIDENCE_QUESTION,
            "question_id": INSUFFICIENT_EVIDENCE_QUESTION_ID,
            "question_source": "insufficient",
            "reference_answer": None,
        },
    ]

    comparisons = []
    summaries = []
    for job in jobs:
        log.info("Live comparison label=%s source=%s", job["label"], job["question_source"])
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
        payload = comparison.to_dict()
        payload["demo_label"] = job["label"]
        comparisons.append(payload)
        summaries.append({"label": job["label"], **_summarize_comparison(payload)})

    hashes_after = _hashes(root)
    _assert_pins(hashes_after, "after live demo")
    if hashes_before != hashes_after:
        raise RuntimeError("Frozen research artefacts changed during the live demo")

    colab_gpu = bool(runtime_lock) and str(runtime_lock.get("device")) == "cuda"
    official_live = colab_gpu and str(args.backend).lower() == "llama_cpp"
    uq_insufficient = next(
        (item for item in summaries if item["label"] == "insufficient_evidence"),
        {},
    )
    uq_decision = ((uq_insufficient.get("architectures") or {}).get(ARCHITECTURE_MULTI_AGENT_UQ) or {}).get(
        "decision"
    )
    abstain_ok = uq_decision == "ABSTAIN"

    if official_live:
        status = "PASS" if abstain_ok else "NEEDS_VERIFICATION"
        status_note = (
            "Colab T4 llama_cpp live demo recorded."
            if abstain_ok
            else f"Colab T4 run recorded but UQ decision on insufficient-evidence was {uq_decision!r}, not ABSTAIN."
        )
    else:
        status = "NEEDS_VERIFICATION"
        status_note = (
            f"This process used backend={args.backend}. Official Phase 20 live validation requires "
            "Colab T4 + Qwen3-8B + llama_cpp. Local mock/Mac results are plumbing only."
        )

    out_dir = get_path(config, "results_config")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "phase": 20,
        "run_id": run_id,
        "status": status,
        "status_note": status_note,
        "backend": args.backend,
        "official_colab_t4_llama_cpp": official_live,
        "locked_threshold": locked_t,
        "used_precomputed_benchmark_lookup": False,
        "used_rag_rerun_of_420": False,
        "recomputed_statistics": False,
        "modified_frozen_140_40": False,
        "modified_threshold_lock": False,
        "modified_phase15_16_17_18": False,
        "n_comparisons": len(comparisons),
        "n_architectures": len(LIVE_ARCHITECTURES),
        "runtime_lock": runtime_lock,
        "fingerprint": fingerprint,
        "hashes": hashes_after,
        "summaries": summaries,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "entrypoint": "PYTHONPATH=. streamlit run app/streamlit_app.py",
        "colab_notebook": "notebooks/colab_phase11_live.ipynb",
    }
    summary_path = out_dir / "phase20_live_demo_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    record = ValidationRecord(
        phase=20,
        test_name="phase20_live_artefact",
        command=f"PYTHONPATH=. python scripts/run_live_demo.py --backend {args.backend}",
        environment=summarize_environment(fingerprint),
        expected=(
            "Three live questions (known-good frozen, fresh KB, insufficient-evidence) "
            "through three independent architectures at locked T=0.65; no benchmark lookup"
        ),
        actual=(
            f"status={status} backend={args.backend} official_colab={official_live} "
            f"locked_t={locked_t} insufficient_uq_decision={uq_decision} "
            f"n={len(comparisons)}"
        ),
        status="PASS" if status == "PASS" else "NEEDS_VERIFICATION",
        output_path=str(summary_path.relative_to(root)),
        extra={
            "status_note": status_note,
            "hashes_unchanged": True,
            "used_precomputed_benchmark_lookup": False,
        },
    )
    (out_dir / "phase20_smoke_test.json").write_text(
        json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps({
        "status": status,
        "phase": 20,
        "backend": args.backend,
        "official_colab_t4_llama_cpp": official_live,
        "locked_threshold": locked_t,
        "insufficient_uq_decision": uq_decision,
        "n_comparisons": len(comparisons),
        "out": str(summary_path.relative_to(root)),
        "status_note": status_note,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
