"""Phase 12 pilot: 6 frozen questions × 3 independent architectures = 18 cases."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.config import ExperimentConfig, get_path, load_experiment_config, project_root
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.models.types import LLMBackend
from src.rag.multi_agent import run_multi_agent
from src.rag.multi_agent_uq import run_multi_agent_uq
from src.rag.schema import (
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
    ARCHITECTURE_SINGLE_AGENT,
    RAGCaseResult,
)
from src.rag.single_agent import run_single_agent
from src.run.store import CaseStore, case_is_successful, utc_now
from src.run.subset import (
    PILOT_N_ARCHITECTURES,
    PILOT_N_CASES,
    PILOT_N_QUESTIONS,
    THRESHOLD_NOTE,
    select_pilot_questions,
    verify_pilot_subset,
)
from src.utils import create_run_id, get_logger

PILOT_ARCHITECTURES = (
    ARCHITECTURE_SINGLE_AGENT,
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
)

def _runner_for(architecture: str) -> Callable[..., RAGCaseResult]:
    runners = {
        ARCHITECTURE_SINGLE_AGENT: run_single_agent,
        ARCHITECTURE_MULTI_AGENT: run_multi_agent,
        ARCHITECTURE_MULTI_AGENT_UQ: run_multi_agent_uq,
    }
    return runners[architecture]


def planned_case_keys(question_ids: list[str], architectures: tuple[str, ...] = PILOT_ARCHITECTURES) -> list[str]:
    return [f"{architecture}:{qid}" for qid in question_ids for architecture in architectures]


def smoke_threshold(config: ExperimentConfig) -> float:
    raw = config.section("uncertainty").get("smoke_threshold")
    return float(raw) if raw is not None else 0.55


def annotate_pilot_result(result: RAGCaseResult, *, threshold: float) -> RAGCaseResult:
    """Stamp pilot diagnostics. Does not change UQ method or architecture code."""
    cfg = dict(result.configuration or {})
    cfg["phase"] = 12
    cfg["mode"] = "pilot"
    cfg["threshold_locked"] = False
    cfg["threshold_note"] = THRESHOLD_NOTE
    if result.architecture == ARCHITECTURE_MULTI_AGENT_UQ:
        cfg.setdefault("threshold_source", "smoke")
        if result.threshold is None:
            result.threshold = threshold
    result.configuration = cfg
    return result


def error_result(
    *,
    run_id: str,
    question: dict[str, str],
    architecture: str,
    error: str,
    fingerprint: dict[str, Any],
    backend_name: str,
    threshold: float,
    seed: int | None,
) -> RAGCaseResult:
    gpu = fingerprint.get("gpu")
    gpu_name = gpu.get("name") if isinstance(gpu, dict) else gpu
    result = RAGCaseResult(
        run_id=run_id,
        question_id=question["id"],
        architecture=architecture,
        question=question["question"],
        retrieved_evidence=[],
        retrieval_scores=[],
        answer="",
        reference_answer=question.get("program_answer") or None,
        decision="ERROR",
        model=str((fingerprint.get("model_config") or {}).get("name") or "Qwen3-8B"),
        device=fingerprint.get("device"),
        gpu=str(gpu_name) if gpu_name else None,
        backend=backend_name,
        random_seed=seed,
        error=error,
        case_key=f"{architecture}:{question['id']}",
    )
    return annotate_pilot_result(result, threshold=threshold)


def run_one_case(
    question: dict[str, str],
    architecture: str,
    *,
    config: ExperimentConfig,
    backend: LLMBackend,
    backend_name: str,
    run_id: str,
    fingerprint: dict[str, Any],
    threshold: float,
) -> RAGCaseResult:
    runner = _runner_for(architecture)
    kwargs: dict[str, Any] = {
        "question_id": question["id"],
        "reference_answer": question.get("program_answer") or None,
        "config": config,
        "backend": backend,
        "backend_name": backend_name,
        "run_id": run_id,
        "fingerprint": fingerprint,
    }
    result = runner(question["question"], **kwargs)
    return annotate_pilot_result(result, threshold=threshold)


def resolve_run_dir(
    *,
    config: ExperimentConfig,
    run_id: str | None,
    resume: str | None,
    resume_latest: bool,
) -> tuple[str, Path, bool]:
    raw_root = get_path(config, "results_raw") / "phase12_pilot"
    if resume_latest:
        from src.run.store import latest_run_dir

        latest = latest_run_dir(raw_root)
        if latest is None:
            raise FileNotFoundError(f"No Phase 12 checkpoint under {raw_root}")
        return latest.name, latest, True
    if resume:
        run_dir = raw_root / resume
        if not (run_dir / "checkpoint.json").is_file() and not (run_dir / "cases.jsonl").is_file():
            raise FileNotFoundError(f"Cannot resume; missing store at {run_dir}")
        return resume, run_dir, True
    rid = run_id or create_run_id("phase12")
    run_dir = raw_root / rid
    if run_dir.exists() and ((run_dir / "cases.jsonl").is_file() or (run_dir / "checkpoint.json").is_file()):
        raise FileExistsError(
            f"Raw store already exists at {run_dir}. Use --resume {rid} "
            "or a new run_id. Refusing to overwrite raw results."
        )
    return rid, run_dir, False


def run_pilot(
    *,
    backend_name: str = "mock",
    n_questions: int = PILOT_N_QUESTIONS,
    config: ExperimentConfig | None = None,
    backend: LLMBackend | None = None,
    run_id: str | None = None,
    resume: str | None = None,
    resume_latest: bool = False,
    retry_failed: bool = True,
    stop_after: int | None = None,
    skip_preflight: bool = False,
    fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run or resume the 18-case pilot. Architectures stay independent (no chaining)."""
    if n_questions > PILOT_N_QUESTIONS:
        raise ValueError(
            f"Phase 12 refuses n_questions={n_questions}. Cap is {PILOT_N_QUESTIONS} "
            f"({PILOT_N_CASES} cases). Do not start the 420-case benchmark here."
        )
    cfg = config or load_experiment_config()
    if cfg.section("uncertainty").get("confidence_threshold") is not None:
        raise RuntimeError(
            "Phase 12 must not use a locked confidence_threshold. "
            "Use uncertainty.smoke_threshold only (NOT LOCKED)."
        )

    questions = select_pilot_questions(n=n_questions, config=cfg)
    if n_questions == PILOT_N_QUESTIONS:
        try:
            verify_pilot_subset(questions)
        except FileNotFoundError:
            pass

    question_ids = [row["id"] for row in questions]
    planned = planned_case_keys(question_ids)
    rid, run_dir, is_resume = resolve_run_dir(
        config=cfg,
        run_id=run_id,
        resume=resume,
        resume_latest=resume_latest,
    )
    checkpoint_copy = get_path(cfg, "results_checkpoints") / "phase12_pilot" / f"{rid}.json"
    store = CaseStore(run_dir, checkpoint_copy=checkpoint_copy)
    log = get_logger(run_id=rid, phase="phase12", architecture="pilot")

    model_cfg = dict(cfg.section("model"))
    model_cfg["backend"] = backend_name
    fp = fingerprint or collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))
    threshold = smoke_threshold(cfg)
    seed = cfg.section("execution").get("random_seed")
    llm = backend or create_backend(model_cfg)

    meta = {
        "phase": 12,
        "mode": "pilot",
        "run_id": rid,
        "backend": backend_name,
        "n_questions": len(questions),
        "n_architectures": PILOT_N_ARCHITECTURES,
        "n_cases": len(planned),
        "question_ids": question_ids,
        "architectures": list(PILOT_ARCHITECTURES),
        "threshold": threshold,
        "threshold_locked": False,
        "threshold_note": THRESHOLD_NOTE,
        "resumed": is_resume,
        "skip_preflight": skip_preflight,
        "device": fp.get("device"),
        "gpu": fp.get("gpu"),
        "random_seed": seed,
    }
    store.write_checkpoint(meta, planned)
    log.info(
        "Pilot start run_id=%s resume=%s n_cases=%s completed=%s failed=%s pending=%s threshold=%.2f (%s)",
        rid,
        is_resume,
        len(planned),
        len(store.completed_keys),
        len(store.failed_keys),
        store.progress(planned)["n_pending"],
        threshold,
        THRESHOLD_NOTE,
    )

    executed = 0
    skipped = 0
    questions_by_id = {row["id"]: row for row in questions}
    for case_key in planned:
        architecture, qid = case_key.split(":", 1)
        question = questions_by_id[qid]
        if not store.should_run(case_key, retry_failed=retry_failed):
            skipped += 1
            log.info("SKIP duplicate/completed case_key=%s", case_key)
            continue
        if stop_after is not None and executed >= stop_after:
            log.info("STOP_AFTER=%s reached; checkpoint saved for resume", stop_after)
            break
        log.info("RUN case_key=%s", case_key)
        try:
            result = run_one_case(
                question,
                architecture,
                config=cfg,
                backend=llm,
                backend_name=backend_name,
                run_id=rid,
                fingerprint=fp,
                threshold=threshold,
            )
        except Exception as exc:  # noqa: BLE001
            result = error_result(
                run_id=rid,
                question=question,
                architecture=architecture,
                error=f"{type(exc).__name__}: {exc}",
                fingerprint=fp,
                backend_name=backend_name,
                threshold=threshold,
                seed=seed,
            )
            log.info("ERROR case_key=%s error=%s", case_key, result.error)
        written = store.append_result(result)
        if not written:
            skipped += 1
            log.info("SKIP duplicate write case_key=%s", case_key)
        else:
            executed += 1
            ok = case_is_successful(result)
            log.info(
                "%s case_key=%s decision=%s n_evidence=%s confidence=%s latency=%.2fs error=%s",
                "OK" if ok else "FAIL",
                case_key,
                result.decision,
                len(result.retrieved_evidence),
                result.confidence,
                result.latency_seconds,
                result.error,
            )
        store.write_checkpoint(meta, planned)

    progress = store.progress(planned)
    status = "PASS" if progress["n_completed"] == len(planned) and progress["n_failed"] == 0 else (
        "INCOMPLETE" if progress["n_pending"] else "FAIL"
    )
    summary = {
        **meta,
        **progress,
        "status": status,
        "executed_this_session": executed,
        "skipped_this_session": skipped,
        "raw_path": _relative_or_absolute(store.raw_path),
        "checkpoint_path": str(store.checkpoint_path),
        "recorded_at_utc": utc_now(),
        "fingerprint": {
            "device": fp.get("device"),
            "gpu": fp.get("gpu"),
            "model_config": fp.get("model_config"),
            "git_commit": fp.get("git_commit"),
        },
    }
    (run_dir / "summary.json").write_text(
        json_dumps(summary) + "\n",
        encoding="utf-8",
    )
    log.info(
        "Pilot end status=%s completed=%s failed=%s pending=%s executed=%s skipped=%s",
        status,
        progress["n_completed"],
        progress["n_failed"],
        progress["n_pending"],
        executed,
        skipped,
    )
    return summary


def _relative_or_absolute(path: Path) -> str:
    root = project_root()
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


def json_dumps(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, indent=2, default=str)
