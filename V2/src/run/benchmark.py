"""Phase 14 benchmark runner: frozen 140 × 3 architectures.

Default is the 9-case validation (3 questions × 3 architectures).
The full 420-case run requires ``allow_full=True`` and is not launched from this phase's notebook.
Uses the Phase 13 locked threshold. Does not recalibrate. Does not chain architectures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD, load_official_lock, lock_path
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
from src.run.drive_sync import sync_benchmark_run
from src.run.store import CaseStore, case_is_successful, utc_now
from src.run.subset import ids_sha256, load_frozen_question_rows
from src.utils import create_run_id, get_logger

BENCHMARK_N_QUESTIONS = 140
BENCHMARK_N_ARCHITECTURES = 3
BENCHMARK_N_CASES = BENCHMARK_N_QUESTIONS * BENCHMARK_N_ARCHITECTURES
VALIDATION_N_QUESTIONS = 3
VALIDATION_N_CASES = VALIDATION_N_QUESTIONS * BENCHMARK_N_ARCHITECTURES
SELECTION_RULE = "first_n_rows_of_frozen_140_csv"
THRESHOLD_NOTE = "LOCKED on FinQA DEV calibration — not tuned on the frozen 140"
BENCHMARK_ARCHITECTURES = (
    ARCHITECTURE_SINGLE_AGENT,
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
)
VALIDATION_QUESTION_IDS = (
    "finqa_test_1000",
    "finqa_test_1012",
    "finqa_test_1017",
)


def _runner_for(architecture: str) -> Callable[..., RAGCaseResult]:
    runners = {
        ARCHITECTURE_SINGLE_AGENT: run_single_agent,
        ARCHITECTURE_MULTI_AGENT: run_multi_agent,
        ARCHITECTURE_MULTI_AGENT_UQ: run_multi_agent_uq,
    }
    return runners[architecture]


def planned_case_keys(
    question_ids: list[str],
    architectures: tuple[str, ...] = BENCHMARK_ARCHITECTURES,
) -> list[str]:
    return [f"{architecture}:{qid}" for qid in question_ids for architecture in architectures]


def select_benchmark_questions(
    *,
    n: int = VALIDATION_N_QUESTIONS,
    allow_full: bool = False,
    config: ExperimentConfig | None = None,
    csv_path: Path | None = None,
) -> list[dict[str, str]]:
    if n < 1:
        raise ValueError("Benchmark n must be >= 1")
    if allow_full:
        if n != BENCHMARK_N_QUESTIONS:
            raise ValueError(
                f"Full Phase 14 benchmark must use all {BENCHMARK_N_QUESTIONS} frozen questions "
                f"({BENCHMARK_N_CASES} cases)."
            )
    elif n > VALIDATION_N_QUESTIONS:
        raise ValueError(
            f"Phase 14 validation is capped at {VALIDATION_N_QUESTIONS} questions "
            f"({VALIDATION_N_CASES} cases). Do not launch the 420-case benchmark without "
            "--allow-full-420."
        )
    rows = load_frozen_question_rows(csv_path)
    if len(rows) != BENCHMARK_N_QUESTIONS:
        raise ValueError(f"Frozen test CSV has {len(rows)} rows; expected {BENCHMARK_N_QUESTIONS}")
    selected = rows[:n]
    frozen_ids = {row["id"] for row in rows}
    leaked_dev = [row["id"] for row in selected if str(row["id"]).startswith("finqa_dev_")]
    if leaked_dev:
        raise RuntimeError(f"Benchmark set includes DEV IDs: {leaked_dev[:5]}")
    if any(row["id"] not in frozen_ids for row in selected):
        raise ValueError("Benchmark subset is not a subset of the frozen 140")
    if any(not str(row["id"]).startswith("finqa_test_") for row in selected):
        raise RuntimeError("Benchmark IDs must be FinQA test (finqa_test_*)")
    return selected


def verify_validation_subset(questions: list[dict[str, str]]) -> None:
    ids = [row["id"] for row in questions]
    if ids != list(VALIDATION_QUESTION_IDS):
        raise ValueError(
            "Phase 14 9-case validation must be the first 3 frozen-140 rows "
            f"{list(VALIDATION_QUESTION_IDS)}; got {ids}"
        )


def verify_full_subset(questions: list[dict[str, str]]) -> None:
    from src.data.select_140 import rows_fingerprint

    ids = [row["id"] for row in questions]
    if len(ids) != BENCHMARK_N_QUESTIONS:
        raise ValueError(f"Full benchmark requires {BENCHMARK_N_QUESTIONS} questions, got {len(ids)}")
    manifest_path = project_root() / "data" / "final" / "sampling_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = list(manifest.get("selected_ids") or [])
    if ids != expected:
        raise ValueError("Full benchmark IDs do not match the frozen Phase 4 sampling manifest")
    expected_sha = str(manifest.get("selected_ids_sha256") or "")
    if expected_sha and rows_fingerprint([{"id": qid} for qid in ids]) != expected_sha:
        raise ValueError("Full benchmark ID SHA-256 does not match the Phase 4 manifest")


def annotate_benchmark_result(
    result: RAGCaseResult,
    *,
    threshold: float,
    mode: str,
) -> RAGCaseResult:
    cfg = dict(result.configuration or {})
    cfg["phase"] = 14
    cfg["mode"] = mode
    cfg["threshold_locked"] = True
    cfg["threshold_note"] = THRESHOLD_NOTE
    cfg["threshold_source"] = "results/config/threshold.lock.json"
    if result.architecture == ARCHITECTURE_MULTI_AGENT_UQ:
        if result.threshold is None:
            result.threshold = threshold
        elif abs(float(result.threshold) - threshold) > 1e-9:
            raise RuntimeError(
                f"UQ case used T={result.threshold}, expected locked T={threshold}. "
                "Do not recalibrate."
            )
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
    mode: str,
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
        threshold=threshold if architecture == ARCHITECTURE_MULTI_AGENT_UQ else None,
    )
    return annotate_benchmark_result(result, threshold=threshold, mode=mode)


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
    mode: str,
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
    if architecture == ARCHITECTURE_MULTI_AGENT_UQ:
        kwargs["threshold"] = threshold
    result = runner(question["question"], **kwargs)
    return annotate_benchmark_result(result, threshold=threshold, mode=mode)


def resolve_run_dir(
    *,
    config: ExperimentConfig,
    run_id: str | None,
    resume: str | None,
    resume_latest: bool,
) -> tuple[str, Path, bool]:
    raw_root = get_path(config, "results_raw") / "phase14_benchmark"
    if resume_latest:
        from src.run.store import latest_run_dir

        latest = latest_run_dir(raw_root)
        if latest is None:
            raise FileNotFoundError(f"No Phase 14 checkpoint under {raw_root}")
        return latest.name, latest, True
    if resume:
        run_dir = raw_root / resume
        if not (run_dir / "checkpoint.json").is_file() and not (run_dir / "cases.jsonl").is_file():
            raise FileNotFoundError(f"Cannot resume; missing store at {run_dir}")
        return resume, run_dir, True
    rid = run_id or create_run_id("phase14")
    run_dir = raw_root / rid
    if run_dir.exists() and ((run_dir / "cases.jsonl").is_file() or (run_dir / "checkpoint.json").is_file()):
        raise FileExistsError(
            f"Raw store already exists at {run_dir}. Use --resume {rid} "
            "or a new run_id. Refusing to overwrite raw results."
        )
    return rid, run_dir, False


def run_benchmark(
    *,
    backend_name: str = "mock",
    n_questions: int = VALIDATION_N_QUESTIONS,
    allow_full: bool = False,
    config: ExperimentConfig | None = None,
    backend: LLMBackend | None = None,
    run_id: str | None = None,
    resume: str | None = None,
    resume_latest: bool = False,
    retry_failed: bool = True,
    stop_after: int | None = None,
    skip_preflight: bool = False,
    fingerprint: dict[str, Any] | None = None,
    lock_file: Path | None = None,
    sync_drive: bool = True,
) -> dict[str, Any]:
    """Run or resume the benchmark. Architectures stay independent (no chaining).

    Phase 14 validation uses n_questions=3 (9 cases). The 140-question path is
    implemented here but the CLI/notebook refuse --allow-full-420.
    """
    cfg = config or load_experiment_config()
    if allow_full and str(backend_name).lower() in {"mock", "test"}:
        raise RuntimeError("Full 420-case benchmark cannot use a mock backend.")
    lock = load_official_lock(lock_file)
    threshold = float(lock["threshold"])
    if abs(threshold - EXPECTED_LOCKED_THRESHOLD) > 1e-9:
        raise RuntimeError("Locked threshold mismatch. Do not recalibrate.")

    questions = select_benchmark_questions(n=n_questions, allow_full=allow_full, config=cfg)
    if n_questions == VALIDATION_N_QUESTIONS:
        verify_validation_subset(questions)
    elif n_questions == BENCHMARK_N_QUESTIONS:
        verify_full_subset(questions)

    mode = "benchmark_validation" if n_questions == VALIDATION_N_QUESTIONS else "benchmark"
    question_ids = [row["id"] for row in questions]
    planned = planned_case_keys(question_ids)
    rid, run_dir, is_resume = resolve_run_dir(
        config=cfg,
        run_id=run_id,
        resume=resume,
        resume_latest=resume_latest,
    )
    checkpoint_copy = get_path(cfg, "results_checkpoints") / "phase14_benchmark" / f"{rid}.json"
    store = CaseStore(run_dir, checkpoint_copy=checkpoint_copy)
    log = get_logger(run_id=rid, phase="phase14", architecture="benchmark")

    model_cfg = dict(cfg.section("model"))
    model_cfg["backend"] = backend_name
    fp = fingerprint or collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))
    seed = cfg.section("execution").get("random_seed")
    llm = backend or create_backend(model_cfg)

    meta = {
        "phase": 14,
        "mode": mode,
        "run_id": rid,
        "backend": backend_name,
        "n_questions": len(questions),
        "n_architectures": BENCHMARK_N_ARCHITECTURES,
        "n_cases": len(planned),
        "question_ids": question_ids,
        "question_ids_sha256": ids_sha256(question_ids),
        "architectures": list(BENCHMARK_ARCHITECTURES),
        "independent_architectures": True,
        "chained": False,
        "threshold": threshold,
        "threshold_locked": True,
        "threshold_note": THRESHOLD_NOTE,
        "threshold_source": str(lock_file or lock_path()),
        "lock_run_id": lock.get("run_id"),
        "lock_source_split": lock.get("source_split"),
        "used_frozen_test_140_for_lock": False,
        "used_frozen_test_140_as_eval_set": True,
        "modifies_frozen_140": False,
        "modifies_frozen_calibration": False,
        "modifies_threshold_lock": False,
        "allow_full": allow_full,
        "resumed": is_resume,
        "skip_preflight": skip_preflight,
        "device": fp.get("device"),
        "gpu": fp.get("gpu"),
        "random_seed": seed,
        "selection_rule": SELECTION_RULE,
    }
    store.write_checkpoint(meta, planned)
    log.info(
        "Benchmark start run_id=%s mode=%s resume=%s n_cases=%s completed=%s failed=%s pending=%s T=%.2f LOCKED",
        rid,
        mode,
        is_resume,
        len(planned),
        len(store.completed_keys),
        len(store.failed_keys),
        store.progress(planned)["n_pending"],
        threshold,
    )

    executed = 0
    skipped = 0
    questions_by_id = {row["id"]: row for row in questions}
    lock_before = Path(lock_file or lock_path()).read_text(encoding="utf-8") if Path(lock_file or lock_path()).is_file() else ""
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
                mode=mode,
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
                mode=mode,
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
                "progress completed=%s failed=%s pending=%s | %s case_key=%s decision=%s n_evidence=%s confidence=%s threshold=%s latency=%.2fs error=%s",
                store.progress(planned)["n_completed"],
                store.progress(planned)["n_failed"],
                store.progress(planned)["n_pending"],
                "OK" if ok else "FAIL",
                case_key,
                result.decision,
                len(result.retrieved_evidence),
                result.confidence,
                result.threshold,
                result.latency_seconds,
                result.error,
            )
        store.write_checkpoint(meta, planned)
        if sync_drive:
            drive_info = sync_benchmark_run(run_dir, run_id=rid, checkpoint_copy=checkpoint_copy)
            if drive_info.get("synced"):
                log.info("Drive sync dest=%s", drive_info.get("dest"))

    lock_after_path = Path(lock_file or lock_path())
    if lock_before and lock_after_path.is_file() and lock_after_path.read_text(encoding="utf-8") != lock_before:
        raise RuntimeError("threshold.lock.json changed during Phase 14. Refusing to continue.")

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
        json.dumps(summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    if sync_drive:
        summary["drive_sync"] = sync_benchmark_run(run_dir, run_id=rid, checkpoint_copy=checkpoint_copy)
    log.info(
        "Benchmark end status=%s completed=%s failed=%s pending=%s executed=%s skipped=%s T=%.2f LOCKED",
        status,
        progress["n_completed"],
        progress["n_failed"],
        progress["n_pending"],
        executed,
        skipped,
        threshold,
    )
    return summary


def _relative_or_absolute(path: Path) -> str:
    root = project_root()
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)
