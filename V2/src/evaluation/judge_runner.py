"""Resumable post-hoc LLM-as-judge job over frozen Phase 15 cases.

Does not rerun RAG architectures or rewrite Phase 15 / Phase 16 CPU artefacts.
"""

from __future__ import annotations

import csv
import json
import os
import platform
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.config import ExperimentConfig, get_path, load_experiment_config, project_root
from src.evaluation.judge import (
    JUDGE_MAX_NEW_TOKENS,
    JUDGE_N_CTX,
    JUDGE_TEMPERATURE,
    METRIC_LABEL,
    judge_one_case,
)
from src.evaluation.metrics import mean
from src.evaluation.runner import (
    BENCHMARK_ARCHITECTURES,
    BENCHMARK_N_CASES,
    DEFAULT_RAW_REL,
    EXPECTED_RAW_SHA256,
    assert_complete,
    load_gold_rows,
    load_raw_cases,
    sha256_file,
)
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.models.types import LLMBackend
from src.run.drive_sync import sync_benchmark_configs, sync_benchmark_run
from src.run.store import CaseStore, latest_run_dir, utc_now
from src.utils import create_run_id, get_logger

PHASE = 16
JOB = "phase16_judge"
RUN_PREFIX = "phase16_judge"
JUDGE_FILENAME = "judge.jsonl"


def resolve_judge_run_dir(
    *,
    config: ExperimentConfig,
    run_id: str | None,
    resume: str | None,
    resume_latest: bool,
) -> tuple[str, Path, bool]:
    raw_root = get_path(config, "results_raw") / JOB
    if resume_latest:
        latest = latest_run_dir(raw_root)
        if latest is None:
            raise FileNotFoundError(f"No checkpoint under {raw_root}")
        return latest.name, latest, True
    if resume:
        run_dir = raw_root / resume
        if not (run_dir / "checkpoint.json").is_file() and not (run_dir / JUDGE_FILENAME).is_file():
            raise FileNotFoundError(f"Cannot resume; missing store at {run_dir}")
        return resume, run_dir, True
    rid = run_id or create_run_id(RUN_PREFIX)
    run_dir = raw_root / rid
    if run_dir.exists() and ((run_dir / JUDGE_FILENAME).is_file() or (run_dir / "checkpoint.json").is_file()):
        raise FileExistsError(
            f"Judge store already exists at {run_dir}. Use --resume {rid} "
            "or a new run_id. Refusing to overwrite raw judge results."
        )
    return rid, run_dir, False


def verify_source_jsonl(path: Path) -> str:
    digest = sha256_file(path)
    if digest != EXPECTED_RAW_SHA256:
        raise ValueError(
            "Phase 16 judge requires the canonical Phase 15 JSONL "
            f"(sha256={EXPECTED_RAW_SHA256}); got {digest} from {path}"
        )
    return digest


def _verify_official_gpu() -> None:
    if platform.system() == "Darwin":
        raise RuntimeError(
            "Official 420-case judge is Colab GPU (llama_cpp). "
            "Use --backend mock --n-cases 3 for local smoke only."
        )
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"PyTorch is required for the official judge: {exc}") from exc
    if os.environ.get("V2_REQUIRE_CUDA", "1") == "1" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Runtime → GPU. Refusing mock fallback.")
    try:
        import llama_cpp  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("llama_cpp is not installed. Install the CUDA wheel on Colab.") from exc


def select_cases(cases: list[dict[str, Any]], n_cases: int) -> list[dict[str, Any]]:
    if n_cases < 1:
        raise ValueError("n_cases must be >= 1")
    if n_cases > len(cases):
        raise ValueError(f"Requested {n_cases} judge cases but source has {len(cases)}")
    return cases[:n_cases]


def load_cpu_rows() -> dict[str, dict[str, Any]]:
    path = project_root() / "results" / "processed" / "phase16_cases.jsonl"
    if not path.is_file():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            row = json.loads(text)
            key = str(row.get("case_key") or "")
            if key:
                rows[key] = row
    return rows


def aggregate_judge_rows(
    rows: list[dict[str, Any]],
    *,
    cpu_rows: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    cpu_rows = cpu_rows or {}
    by_arch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_arch[str(row.get("architecture"))].append(row)
    summary: list[dict[str, Any]] = []
    for arch in BENCHMARK_ARCHITECTURES:
        items = by_arch.get(arch) or []
        scored = [r for r in items if r.get("parsed_faithfulness_score") is not None]
        answered = [r for r in scored if str(r.get("decision") or "ANSWER") == "ANSWER"]
        cpu_faith = [
            float(cpu_rows[r["case_key"]]["faithfulness"])
            for r in items
            if r.get("case_key") in cpu_rows and cpu_rows[r["case_key"]].get("faithfulness") is not None
        ]
        summary.append(
            {
                "architecture": arch,
                "n_judge": len(items),
                "n_scored": len(scored),
                "n_parse_failure": sum(1 for r in items if r.get("parse_failure")),
                "n_error": sum(1 for r in items if r.get("error")),
                "n_answer_scored": len(answered),
                "faithfulness_llm": mean([float(r["parsed_faithfulness_score"]) for r in scored]),
                "faithfulness_llm_answered_only": mean(
                    [float(r["parsed_faithfulness_score"]) for r in answered]
                ),
                "faithfulness_token_overlap_secondary": mean(cpu_faith),
                "metric_label": METRIC_LABEL,
            }
        )
    return summary


def write_judge_metrics(rows: list[dict[str, Any]], metrics_root: Path) -> dict[str, str]:
    cpu_rows = load_cpu_rows()
    summary_rows = aggregate_judge_rows(rows, cpu_rows=cpu_rows)
    metrics_root.mkdir(parents=True, exist_ok=True)
    json_path = metrics_root / "phase16_judge_by_architecture.json"
    csv_path = metrics_root / "phase16_judge_summary.csv"
    md_path = metrics_root / "phase16_judge_summary.md"
    json_path.write_text(json.dumps({r["architecture"]: r for r in summary_rows}, indent=2) + "\n", encoding="utf-8")
    fields = [
        "architecture",
        "n_judge",
        "n_scored",
        "n_parse_failure",
        "n_error",
        "n_answer_scored",
        "faithfulness_llm",
        "faithfulness_llm_answered_only",
        "faithfulness_token_overlap_secondary",
        "metric_label",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)
    lines = [
        "# Phase 16 LLM-as-judge faithfulness",
        "",
        METRIC_LABEL + ". Not official RAGAS Faithfulness. Token-overlap remains secondary.",
        "Does not replace numeric answer correctness. Does not judge context precision/recall.",
        "",
        "| Architecture | n | scored | parse fail | LLM faithfulness | LLM faithfulness (ANSWER) | Token-overlap (secondary) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        llm = row.get("faithfulness_llm")
        ans = row.get("faithfulness_llm_answered_only")
        tok = row.get("faithfulness_token_overlap_secondary")
        lines.append(
            "| {arch} | {n} | {scored} | {fail} | {llm} | {ans} | {tok} |".format(
                arch=row["architecture"],
                n=row["n_judge"],
                scored=row["n_scored"],
                fail=row["n_parse_failure"],
                llm="—" if llm is None else f"{llm:.4f}",
                ans="—" if ans is None else f"{ans:.4f}",
                tok="—" if tok is None else f"{tok:.4f}",
            )
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "metrics_json": str(json_path.relative_to(project_root())),
        "metrics_csv": str(csv_path.relative_to(project_root())),
        "metrics_md": str(md_path.relative_to(project_root())),
    }


def run_judge(
    *,
    backend_name: str = "mock",
    n_cases: int = BENCHMARK_N_CASES,
    config: ExperimentConfig | None = None,
    backend: LLMBackend | None = None,
    raw_path: Path | None = None,
    run_id: str | None = None,
    resume: str | None = None,
    resume_latest: bool = False,
    retry_failed: bool = True,
    stop_after: int | None = None,
    fingerprint: dict[str, Any] | None = None,
    sync_drive: bool = True,
) -> dict[str, Any]:
    """Judge saved Phase 15 cases. Official path is n_cases=420 and llama_cpp."""
    cfg = config or load_experiment_config()
    mock_backend = str(backend_name).lower() in {"mock", "test"}
    if not mock_backend:
        if n_cases != BENCHMARK_N_CASES and not stop_after:
            raise RuntimeError("llama_cpp judge must plan all 420 cases (use --stop-after to pause).")
        n_cases = BENCHMARK_N_CASES
        official = True
        if str(backend_name).lower() in {"llama_cpp", "llamacpp", "gguf", "colab"}:
            _verify_official_gpu()
    else:
        official = False
        if n_cases == BENCHMARK_N_CASES:
            raise RuntimeError("Official 420-case judge cannot use a mock backend.")

    source = Path(raw_path) if raw_path else (project_root() / DEFAULT_RAW_REL)
    if not source.is_file():
        raise FileNotFoundError(f"Phase 15 raw JSONL not found: {source}")
    source_sha = verify_source_jsonl(source)
    gold = load_gold_rows()
    all_cases = load_raw_cases(source)
    completeness = assert_complete(all_cases, gold)
    if sha256_file(source) != source_sha:
        raise RuntimeError("Phase 15 raw JSONL changed while loading. Refusing to continue.")

    selected = all_cases if official else select_cases(all_cases, n_cases)
    planned = [str(c.get("case_key") or f"{c.get('architecture')}:{c.get('question_id')}") for c in selected]
    if official and len(planned) != BENCHMARK_N_CASES:
        raise ValueError(f"Official judge must cover {BENCHMARK_N_CASES} cases; got {len(planned)}")

    rid, run_dir, is_resume = resolve_judge_run_dir(
        config=cfg,
        run_id=run_id,
        resume=resume,
        resume_latest=resume_latest,
    )
    checkpoint_copy = get_path(cfg, "results_checkpoints") / JOB / f"{rid}.json"
    store = CaseStore(run_dir, checkpoint_copy=checkpoint_copy, raw_filename=JUDGE_FILENAME)
    log = get_logger(run_id=rid, phase="phase16_judge", architecture="judge")

    model_cfg = dict(cfg.section("model"))
    model_cfg["backend"] = backend_name
    model_cfg["temperature"] = JUDGE_TEMPERATURE
    model_cfg["max_new_tokens"] = JUDGE_MAX_NEW_TOKENS
    model_cfg["n_ctx"] = JUDGE_N_CTX
    fp = fingerprint or collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))
    llm = backend or create_backend(model_cfg)

    meta = {
        "phase": PHASE,
        "mode": "judge_faithfulness",
        "run_id": rid,
        "job": JOB,
        "backend": backend_name,
        "n_cases": len(planned),
        "n_planned": len(planned),
        "official_420": official,
        "source_raw_path": str(source.relative_to(project_root())) if source.is_relative_to(project_root()) else str(source),
        "source_raw_sha256": source_sha,
        "metric_label": METRIC_LABEL,
        "judge_model": "Qwen3-8B",
        "quantisation": "Q4_K_M",
        "n_ctx": JUDGE_N_CTX,
        "temperature": JUDGE_TEMPERATURE,
        "max_new_tokens": JUDGE_MAX_NEW_TOKENS,
        "used_rag_rerun": False,
        "used_gold_context": False,
        "used_gold_answer": False,
        "modifies_phase15_raw": False,
        "modifies_phase16_cpu": False,
        "resumed": is_resume,
        "device": fp.get("device"),
        "gpu": fp.get("gpu", {}).get("name") if isinstance(fp.get("gpu"), dict) else fp.get("gpu"),
        "completeness_source": completeness,
    }
    store.write_checkpoint(meta, planned)
    log.info(
        "Judge start run_id=%s resume=%s n=%s completed=%s official=%s used_rag_rerun=false",
        rid,
        is_resume,
        len(planned),
        len(store.completed_keys),
        official,
    )

    executed = 0
    skipped = 0
    by_key = {
        str(c.get("case_key") or f"{c.get('architecture')}:{c.get('question_id')}"): c for c in selected
    }
    for key in planned:
        if not store.should_run(key, retry_failed=retry_failed):
            skipped += 1
            continue
        if stop_after is not None and executed >= stop_after:
            break
        case = by_key[key]
        record = judge_one_case(
            case,
            llm,
            source_raw_sha256=source_sha,
            fingerprint=fp,
        )
        ok = record.get("error") is None and record.get("parse_failure") is False
        store.append_payload(key, record, ok=ok, error=record.get("error"))
        store.write_checkpoint(meta, planned)
        if sync_drive:
            sync_benchmark_run(run_dir, run_id=rid, checkpoint_copy=checkpoint_copy, job=JOB)
        executed += 1
        log.info(
            "Judge case %s status=%s score=%s parse_failure=%s",
            key,
            "COMPLETED" if ok else "FAILED",
            record.get("parsed_faithfulness_score"),
            record.get("parse_failure"),
        )

    if sha256_file(source) != source_sha:
        raise RuntimeError("Phase 15 raw JSONL changed during judging. Refusing to continue.")

    progress = store.progress(planned)
    judged = [store._records[k] for k in planned if k in store._records]
    metric_paths: dict[str, str] = {}
    status = "INCOMPLETE"
    if progress["n_completed"] == len(planned) and progress["n_failed"] == 0:
        status = "PASS"
    elif progress["n_pending"] == 0 and progress["n_failed"]:
        status = "FAIL"
    if judged and (official or status == "PASS"):
        if official:
            metric_paths = write_judge_metrics(judged, get_path(cfg, "results_metrics"))

    summary = {
        **meta,
        **progress,
        **metric_paths,
        "status": status,
        "executed_this_session": executed,
        "skipped_this_session": skipped,
        "n_parse_failure": sum(1 for r in judged if r.get("parse_failure")),
        "raw_path": str(store.raw_path.relative_to(project_root())) if store.raw_path.is_relative_to(project_root()) else str(store.raw_path),
        "updated_at_utc": utc_now(),
        "source_raw_unchanged": True,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    store.write_checkpoint(summary, planned)
    if sync_drive:
        summary["drive_sync"] = sync_benchmark_run(
            run_dir, run_id=rid, checkpoint_copy=checkpoint_copy, job=JOB
        )
        summary["drive_configs"] = sync_benchmark_configs(get_path(cfg, "results_config"), job=JOB)
    else:
        summary["drive_sync"] = {"synced": False, "reason": "disabled"}
    config_root = get_path(cfg, "results_config")
    config_root.mkdir(parents=True, exist_ok=True)
    if official:
        (config_root / "phase16_judge_summary.json").write_text(
            json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8"
        )
    log.info("Judge end status=%s completed=%s failed=%s pending=%s", status, progress["n_completed"], progress["n_failed"], progress["n_pending"])
    return summary
