"""Phase 13: run Multi-Agent + UQ on the frozen DEV calibration set."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.calibration.data import (
    CALIBRATION_N,
    assert_no_test_leakage,
    load_calibration_questions,
    verify_calibration_subset,
)
from src.calibration.lock import (
    build_lock_payload,
    official_lock_allowed,
    write_threshold_files,
)
from src.config import ExperimentConfig, get_path, load_experiment_config, project_root
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.models.types import LLMBackend
from src.rag.multi_agent_uq import run_multi_agent_uq
from src.rag.schema import ARCHITECTURE_MULTI_AGENT_UQ, RAGCaseResult
from src.run.pilot import error_result, smoke_threshold
from src.run.store import CaseStore, case_is_successful, latest_run_dir, utc_now
from src.utils import create_run_id, get_logger

CALIBRATION_ARCHITECTURE = ARCHITECTURE_MULTI_AGENT_UQ


def planned_case_keys(question_ids: list[str]) -> list[str]:
    return [f"{CALIBRATION_ARCHITECTURE}:{qid}" for qid in question_ids]


def resolve_run_dir(
    *,
    config: ExperimentConfig,
    run_id: str | None,
    resume: str | None,
    resume_latest: bool,
) -> tuple[str, Path, bool]:
    raw_root = get_path(config, "results_raw") / "phase13_calibration"
    if resume_latest:
        latest = latest_run_dir(raw_root)
        if latest is None:
            raise FileNotFoundError(f"No Phase 13 checkpoint under {raw_root}")
        return latest.name, latest, True
    if resume:
        run_dir = raw_root / resume
        if not (run_dir / "checkpoint.json").is_file() and not (run_dir / "cases.jsonl").is_file():
            raise FileNotFoundError(f"Cannot resume; missing store at {run_dir}")
        return resume, run_dir, True
    rid = run_id or create_run_id("phase13")
    run_dir = raw_root / rid
    if run_dir.exists() and ((run_dir / "cases.jsonl").is_file() or (run_dir / "checkpoint.json").is_file()):
        raise FileExistsError(
            f"Raw store already exists at {run_dir}. Use --resume {rid}. "
            "Refusing to overwrite raw results."
        )
    return rid, run_dir, False


def annotate_calibration_result(result: RAGCaseResult, *, threshold: float) -> RAGCaseResult:
    cfg = dict(result.configuration or {})
    cfg["phase"] = 13
    cfg["mode"] = "calibration"
    cfg["threshold_locked"] = False
    cfg["threshold_note"] = "smoke/demo during collection — lock is computed after the DEV run"
    cfg["source_split"] = "dev"
    if result.threshold is None:
        result.threshold = threshold
    result.configuration = cfg
    return result


def run_calibration(
    *,
    backend_name: str = "mock",
    n_questions: int = CALIBRATION_N,
    config: ExperimentConfig | None = None,
    backend: LLMBackend | None = None,
    run_id: str | None = None,
    resume: str | None = None,
    resume_latest: bool = False,
    retry_failed: bool = True,
    stop_after: int | None = None,
    fingerprint: dict[str, Any] | None = None,
    write_lock: bool = True,
) -> dict[str, Any]:
    if n_questions > CALIBRATION_N:
        raise ValueError(
            f"Phase 13 refuses n_questions={n_questions}. Cap is {CALIBRATION_N} DEV items. "
            "Do not start the 420-case benchmark here."
        )
    cfg = config or load_experiment_config()
    questions = load_calibration_questions(n=n_questions, config=cfg)
    assert_no_test_leakage(questions, config=cfg)
    if n_questions == CALIBRATION_N:
        verify_calibration_subset(questions)

    question_ids = [row["id"] for row in questions]
    planned = planned_case_keys(question_ids)
    rid, run_dir, is_resume = resolve_run_dir(
        config=cfg,
        run_id=run_id,
        resume=resume,
        resume_latest=resume_latest,
    )
    checkpoint_copy = get_path(cfg, "results_checkpoints") / "phase13_calibration" / f"{rid}.json"
    store = CaseStore(run_dir, checkpoint_copy=checkpoint_copy)
    log = get_logger(run_id=rid, phase="phase13", architecture="calibration")

    model_cfg = dict(cfg.section("model"))
    model_cfg["backend"] = backend_name
    fp = fingerprint or collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))
    threshold = smoke_threshold(cfg)
    seed = cfg.section("execution").get("random_seed")
    llm = backend or create_backend(model_cfg)

    meta = {
        "phase": 13,
        "mode": "calibration",
        "run_id": rid,
        "backend": backend_name,
        "architecture": CALIBRATION_ARCHITECTURE,
        "n_questions": len(questions),
        "n_cases": len(planned),
        "question_ids": question_ids,
        "source_split": "dev",
        "used_frozen_test_140": False,
        "collection_threshold": threshold,
        "threshold_locked": False,
        "resumed": is_resume,
        "device": fp.get("device"),
        "gpu": fp.get("gpu"),
        "random_seed": seed,
    }
    store.write_checkpoint(meta, planned)
    log.info(
        "Calibration start run_id=%s n=%s completed=%s pending=%s (T not locked yet)",
        rid,
        len(planned),
        len(store.completed_keys),
        store.progress(planned)["n_pending"],
    )

    executed = 0
    skipped = 0
    by_id = {row["id"]: row for row in questions}
    for case_key in planned:
        _, qid = case_key.split(":", 1)
        question = by_id[qid]
        if not store.should_run(case_key, retry_failed=retry_failed):
            skipped += 1
            log.info("SKIP completed case_key=%s", case_key)
            continue
        if stop_after is not None and executed >= stop_after:
            log.info("STOP_AFTER=%s reached", stop_after)
            break
        log.info("RUN case_key=%s", case_key)
        try:
            result = run_multi_agent_uq(
                question["question"],
                question_id=question["id"],
                reference_answer=question.get("program_answer") or None,
                config=cfg,
                backend=llm,
                backend_name=backend_name,
                run_id=rid,
                fingerprint=fp,
            )
            result = annotate_calibration_result(result, threshold=threshold)
        except Exception as exc:  # noqa: BLE001
            result = error_result(
                run_id=rid,
                question=question,
                architecture=CALIBRATION_ARCHITECTURE,
                error=f"{type(exc).__name__}: {exc}",
                fingerprint=fp,
                backend_name=backend_name,
                threshold=threshold,
                seed=seed,
            )
            result = annotate_calibration_result(result, threshold=threshold)
            log.info("ERROR case_key=%s error=%s", case_key, result.error)
        if not store.append_result(result):
            skipped += 1
        else:
            executed += 1
            log.info(
                "%s case_key=%s decision=%s confidence=%s latency=%.2fs",
                "OK" if case_is_successful(result) else "FAIL",
                case_key,
                result.decision,
                result.confidence,
                result.latency_seconds,
            )
        store.write_checkpoint(meta, planned)

    progress = store.progress(planned)
    run_status = "PASS" if progress["n_completed"] == len(planned) and progress["n_failed"] == 0 else (
        "INCOMPLETE" if progress["n_pending"] else "FAIL"
    )
    cases = []
    if store.raw_path.is_file():
        import json

        cases = [json.loads(line) for line in store.raw_path.read_text().splitlines() if line.strip()]

    lock_info: dict[str, Any] = {"locked": False, "threshold_note": "NOT LOCKED"}
    if write_lock and cases:
        allowed, reason = official_lock_allowed(
            backend=backend_name,
            device=fp.get("device"),
            n_completed=progress["n_completed"],
        )
        payload = build_lock_payload(
            cases,
            run_id=rid,
            backend=backend_name,
            device=fp.get("device"),
            gpu=fp.get("gpu"),
            git_commit=fp.get("git_commit"),
            official=allowed and n_questions == CALIBRATION_N,
        )
        if not allowed:
            payload["locked"] = False
            payload["threshold_note"] = f"candidate only — NOT LOCKED ({reason})"
        written = write_threshold_files(payload)
        lock_info = {
            "locked": payload.get("locked"),
            "threshold": payload.get("threshold"),
            "selected": payload.get("selected"),
            "coverage": payload.get("coverage"),
            "selective_accuracy": payload.get("selective_accuracy"),
            "threshold_note": payload.get("threshold_note"),
            "reason": reason if not allowed else payload.get("reason"),
            "files": written,
        }

    summary = {
        **meta,
        **progress,
        "status": run_status,
        "executed_this_session": executed,
        "skipped_this_session": skipped,
        "lock": lock_info,
        "raw_path": str(store.raw_path),
        "recorded_at_utc": utc_now(),
        "fingerprint": {
            "device": fp.get("device"),
            "gpu": fp.get("gpu"),
            "model_config": fp.get("model_config"),
            "git_commit": fp.get("git_commit"),
        },
    }
    try:
        summary["raw_path"] = str(store.raw_path.resolve().relative_to(project_root()))
    except ValueError:
        pass
    (run_dir / "summary.json").write_text(
        __import__("json").dumps(summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    log.info(
        "Calibration end status=%s completed=%s locked=%s T=%s",
        run_status,
        progress["n_completed"],
        lock_info.get("locked"),
        lock_info.get("threshold"),
    )
    return summary
