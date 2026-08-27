"""Phase 16: score saved Phase 15 cases. No RAG rerun, no Qwen generation, CPU only."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD, load_official_lock
from src.config import ExperimentConfig, get_path, load_experiment_config, project_root
from src.evaluation.metrics import aggregate_architecture, score_case
from src.rag.schema import (
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
    ARCHITECTURE_SINGLE_AGENT,
)
from src.run.subset import load_frozen_question_rows
from src.utils import create_run_id, get_logger

PHASE = 16
BENCHMARK_N_QUESTIONS = 140
BENCHMARK_N_CASES = 420
BENCHMARK_ARCHITECTURES = (
    ARCHITECTURE_SINGLE_AGENT,
    ARCHITECTURE_MULTI_AGENT,
    ARCHITECTURE_MULTI_AGENT_UQ,
)
DEFAULT_RAW_REL = (
    "results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl"
)
EXPECTED_RAW_SHA256 = "f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa"
FORBIDDEN_IMPORT_MODULES = {
    "llama_cpp",
    "src.run.benchmark",
    "src.rag.single_agent",
    "src.rag.multi_agent",
    "src.rag.multi_agent_uq",
    "src.models.factory",
}


def planned_case_keys(
    question_ids: list[str],
    architectures: tuple[str, ...] = BENCHMARK_ARCHITECTURES,
) -> list[str]:
    return [f"{architecture}:{qid}" for qid in question_ids for architecture in architectures]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def load_gold_rows(csv_path: Path | None = None) -> dict[str, dict[str, str]]:
    """Load freeze CSV including provenance fields. Does not write the freeze."""
    if csv_path is None:
        rows = load_frozen_question_rows()
        path = project_root() / "data" / "final" / "selected_140_questions.csv"
    else:
        path = csv_path
        rows = load_frozen_question_rows(path)
    extra: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            qid = str(row.get("id") or "").strip()
            extra[qid] = {
                "context_id": str(row.get("context_id") or ""),
                "file_name": str(row.get("file_name") or ""),
                "program_answer": str(row.get("program_answer") or ""),
                "original_answer": str(row.get("original_answer") or ""),
            }
    gold: dict[str, dict[str, str]] = {}
    for row in rows:
        qid = row["id"]
        merged = dict(row)
        merged.update(extra.get(qid) or {})
        gold[qid] = merged
    if len(gold) != BENCHMARK_N_QUESTIONS:
        raise ValueError(f"Gold freeze has {len(gold)} ids; expected {BENCHMARK_N_QUESTIONS}")
    return gold


def load_raw_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            cases.append(json.loads(text))
    return cases


CPU_EVAL_FILES = ("__init__.py", "metrics.py", "numeric.py", "runner.py")


def verify_no_generation_stack() -> None:
    """Refuse CPU evaluation modules that import RAG pipelines or the LLM factory.

    Judge modules (``judge.py``, ``judge_runner.py``) are a separate post-hoc job.
    """
    eval_dir = Path(__file__).resolve().parent
    imported: set[str] = set()
    for name in CPU_EVAL_FILES:
        path = eval_dir / name
        if path.is_file():
            imported |= _imported_modules(path)
    loaded = sorted(imported & FORBIDDEN_IMPORT_MODULES)
    if loaded:
        raise RuntimeError(f"Phase 16 CPU evaluation must not import RAG/LLM modules: {loaded}")


def assert_complete(cases: list[dict[str, Any]], gold: dict[str, dict[str, str]]) -> dict[str, Any]:
    keys = [c.get("case_key") or f"{c.get('architecture')}:{c.get('question_id')}" for c in cases]
    unique = set(keys)
    qids = [str(c.get("question_id") or "") for c in cases]
    planned = planned_case_keys(list(gold.keys()), BENCHMARK_ARCHITECTURES)
    missing = sorted(set(planned) - unique)
    extra = sorted(unique - set(planned))
    dups = len(keys) - len(unique)
    leaked_dev = [qid for qid in set(qids) if qid.startswith("finqa_dev_")]
    errors = [c.get("case_key") for c in cases if c.get("error")]
    info = {
        "n_lines": len(cases),
        "n_unique_keys": len(unique),
        "n_duplicates": dups,
        "n_missing": len(missing),
        "n_extra": len(extra),
        "n_errors": len(errors),
        "n_unique_questions": len(set(qids)),
        "leaked_dev": leaked_dev,
        "missing_keys": missing[:12],
        "extra_keys": extra[:12],
    }
    if (
        len(cases) != BENCHMARK_N_CASES
        or len(unique) != BENCHMARK_N_CASES
        or dups
        or missing
        or extra
        or leaked_dev
        or set(qids) != set(gold)
    ):
        raise ValueError(f"Phase 16 input is not a complete 420-case freeze: {info}")
    return info


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_evaluation(
    *,
    raw_path: Path | None = None,
    config: ExperimentConfig | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Score the frozen Phase 15 JSONL on CPU. Does not call RAG or Qwen."""
    verify_no_generation_stack()
    cfg = config or load_experiment_config()
    lock = load_official_lock()
    if abs(float(lock["threshold"]) - EXPECTED_LOCKED_THRESHOLD) > 1e-9:
        raise RuntimeError("Locked T is not 0.65. Do not recalibrate.")

    source = Path(raw_path) if raw_path else (project_root() / DEFAULT_RAW_REL)
    if not source.is_file():
        raise FileNotFoundError(f"Phase 15 raw JSONL not found: {source}")

    freeze_csv = project_root() / "data" / "final" / "selected_140_questions.csv"
    cal_csv = project_root() / "data" / "calibration" / "calibration_questions.csv"
    lock_file = project_root() / "results" / "config" / "threshold.lock.json"
    freeze_sha_before = sha256_file(freeze_csv)
    cal_sha_before = sha256_file(cal_csv)
    lock_sha_before = sha256_file(lock_file)

    input_sha_before = sha256_file(source)
    if input_sha_before != EXPECTED_RAW_SHA256:
        raise ValueError(
            "Phase 16 requires the canonical Phase 15 JSONL "
            f"(sha256={EXPECTED_RAW_SHA256}); got {input_sha_before} from {source}"
        )
    gold = load_gold_rows()
    cases = load_raw_cases(source)
    completeness = assert_complete(cases, gold)

    processed_root = get_path(cfg, "results_processed")
    metrics_root = get_path(cfg, "results_metrics") if "results_metrics" in cfg.section("paths") else (
        project_root() / "results" / "metrics"
    )
    config_root = get_path(cfg, "results_config")
    cases_out = processed_root / "phase16_cases.jsonl"
    if cases_out.is_file() and not force:
        raise FileExistsError(f"Refusing to overwrite {cases_out}. Pass force=True to replace.")

    scored: list[dict[str, Any]] = []
    for case in cases:
        qid = str(case.get("question_id") or "")
        scored.append(score_case(case, gold[qid]))

    by_arch: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        by_arch[str(row["architecture"])].append(row)
    summary_rows = []
    by_architecture: dict[str, Any] = {}
    for arch in BENCHMARK_ARCHITECTURES:
        rows = by_arch.get(arch) or []
        if len(rows) != BENCHMARK_N_QUESTIONS:
            raise ValueError(f"{arch} has {len(rows)} scored cases; expected {BENCHMARK_N_QUESTIONS}")
        agg = aggregate_architecture(rows)
        agg["architecture"] = arch
        by_architecture[arch] = agg
        summary_rows.append(agg)

    input_sha_after = sha256_file(source)
    if input_sha_after != input_sha_before:
        raise RuntimeError("Phase 15 raw JSONL changed during evaluation. Refusing to continue.")
    if sha256_file(freeze_csv) != freeze_sha_before:
        raise RuntimeError("Frozen 140 CSV changed during evaluation. Refusing to continue.")
    if sha256_file(cal_csv) != cal_sha_before:
        raise RuntimeError("Calibration 40 CSV changed during evaluation. Refusing to continue.")
    if sha256_file(lock_file) != lock_sha_before:
        raise RuntimeError("threshold.lock.json changed during evaluation. Refusing to continue.")

    rid = create_run_id("phase16")
    log = get_logger(run_id=rid, phase="phase16", architecture="evaluation")
    payload_meta = {
        "phase": PHASE,
        "mode": "evaluation",
        "run_id": rid,
        "source_raw_path": str(source.relative_to(project_root())) if source.is_relative_to(project_root()) else str(source),
        "source_raw_sha256": input_sha_before,
        "frozen_140_sha256": freeze_sha_before,
        "calibration_40_sha256": cal_sha_before,
        "threshold_lock_sha256": lock_sha_before,
        "n_cases": len(scored),
        "n_questions": BENCHMARK_N_QUESTIONS,
        "n_architectures": len(BENCHMARK_ARCHITECTURES),
        "threshold": float(lock["threshold"]),
        "threshold_locked": True,
        "threshold_not_retuned": True,
        "judge_model": None,
        "used_llm_inference": False,
        "used_gpu": False,
        "used_rag_rerun": False,
        "completeness": completeness,
        "metric_definitions": {
            "answer_correctness": (
                "Numeric match of the displayed answer to FinQA program_answer "
                "(rel_tol=0.01). UQ ABSTAIN displayed text is usually incorrect."
            ),
            "answer_correctness_claim": (
                "Numeric match of the UQ draft (or displayed answer) to program_answer."
            ),
            "faithfulness": (
                "CPU token-overlap of the model claim vs concatenated retrieved chunk text. "
                "Not official RAGAS LLM-as-judge faithfulness."
            ),
            "context_precision": (
                "Fraction of top-k chunks whose file_name or context_id matches the gold freeze."
            ),
            "context_recall": (
                "1 if any retrieved chunk matches the gold file_name or context_id, else 0."
            ),
            "selective_accuracy": "Displayed numeric accuracy among ANSWER decisions only.",
            "unsupported_emitted_rate": "Fraction of cases that ANSWERED and failed displayed numeric match.",
        },
        "by_architecture": by_architecture,
    }

    processed_root.mkdir(parents=True, exist_ok=True)
    metrics_root.mkdir(parents=True, exist_ok=True)
    with cases_out.open("w", encoding="utf-8") as handle:
        for row in scored:
            handle.write(json.dumps(row, default=str) + "\n")

    _write_json(metrics_root / "phase16_by_architecture.json", by_architecture)
    csv_fields = [
        "architecture",
        "n",
        "n_answer",
        "n_abstain",
        "coverage",
        "abstention_rate",
        "answer_correctness",
        "answer_correctness_claim",
        "selective_accuracy",
        "unsupported_emitted_rate",
        "faithfulness",
        "faithfulness_stored_verification_score",
        "context_precision",
        "context_recall",
        "context_recall_numeric",
        "mean_confidence",
        "mean_latency_seconds",
        "n_correct_displayed",
        "n_correct_claim",
        "n_correct_answered",
    ]
    _write_csv(metrics_root / "phase16_summary.csv", summary_rows, csv_fields)

    md_lines = [
        "# Phase 16 metric summary",
        "",
        "CPU scoring of saved Phase 15 cases. No RAG/Qwen rerun. Not official RAGAS LLM metrics.",
        "",
        "| Architecture | n | ANSWER | ABSTAIN | Answer correctness (displayed) | Claim correctness | Selective acc. | Faithfulness | Context P | Context R | Unsupported emitted |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        sel = row.get("selective_accuracy")
        sel_s = "—" if sel is None else f"{sel:.4f}"
        md_lines.append(
            "| {architecture} | {n} | {n_answer} | {n_abstain} | {answer_correctness:.4f} | "
            "{answer_correctness_claim:.4f} | {sel} | {faithfulness:.4f} | "
            "{context_precision:.4f} | {context_recall:.4f} | {unsupported_emitted_rate:.4f} |".format(
                architecture=row["architecture"],
                n=row["n"],
                n_answer=row["n_answer"],
                n_abstain=row["n_abstain"],
                answer_correctness=row["answer_correctness"],
                answer_correctness_claim=row["answer_correctness_claim"],
                sel=sel_s,
                faithfulness=row["faithfulness"],
                context_precision=row["context_precision"],
                context_recall=row["context_recall"],
                unsupported_emitted_rate=row["unsupported_emitted_rate"],
            )
        )
    (metrics_root / "phase16_summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    summary = {
        **payload_meta,
        "status": "PASS",
        "processed_path": str(cases_out.relative_to(project_root())),
        "metrics_json": str((metrics_root / "phase16_by_architecture.json").relative_to(project_root())),
        "metrics_csv": str((metrics_root / "phase16_summary.csv").relative_to(project_root())),
        "metrics_md": str((metrics_root / "phase16_summary.md").relative_to(project_root())),
        "raw_unchanged": True,
    }
    _write_json(config_root / "phase16_evaluation_summary.json", summary)
    log.info(
        "Phase 16 evaluation PASS n=%s sha=%s used_llm=false used_gpu=false",
        len(scored),
        input_sha_before[:12],
    )
    verify_no_generation_stack()
    return summary
