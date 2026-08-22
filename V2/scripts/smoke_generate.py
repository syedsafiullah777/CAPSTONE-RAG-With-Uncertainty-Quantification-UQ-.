#!/usr/bin/env python3
"""Phase 7 smoke: fingerprint + one generation; writes validation evidence JSON."""

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
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.utils import create_run_id, get_logger, setup_logging
from src.utils.evidence import ValidationRecord, summarize_environment


DEFAULT_PROMPT = (
    "Answer briefly using one short sentence. "
    "What is 2 + 2? Reply with only the number."
)

EVIDENCE_MD = "project_record/evidence/phase7_validation.md"
SMOKE_TEST_JSON = "results/config/phase7_smoke_test.json"
FINGERPRINT_JSON = "results/config/phase7_runtime_fingerprint.json"


def _command_line(args: argparse.Namespace, backend: str | None) -> str:
    parts = ["PYTHONPATH=.", "python", "scripts/smoke_generate.py"]
    if backend:
        parts.extend(["--backend", backend])
    if args.prompt != DEFAULT_PROMPT:
        parts.extend(["--prompt", repr(args.prompt)])
    return " ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test Qwen3-8B backend with validation evidence")
    parser.add_argument(
        "--backend",
        default=None,
        help="Override backend: auto|llama_cpp|transformers|ollama_dev|mock",
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--out",
        default=None,
        help=f"Validation JSON path (default: {SMOKE_TEST_JSON})",
    )
    parser.add_argument(
        "--notebook",
        default=None,
        help="Notebook path if run from Colab (e.g. notebooks/colab_phase7_smoke.ipynb)",
    )
    args = parser.parse_args()

    config = load_experiment_config()
    run_id = create_run_id("phase7")
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=run_id,
        console=True,
        file=True,
    )
    log = get_logger(run_id=run_id, phase="phase7", model=str(config.get("model", "name")))

    model_cfg = dict(config.section("model"))
    backend_name = args.backend or str(model_cfg.get("backend") or "auto")
    if args.backend:
        model_cfg["backend"] = args.backend

    command = _command_line(args, args.backend)
    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))
    fp_path = get_path(config, "results_config") / Path(FINGERPRINT_JSON).name
    fp_path.parent.mkdir(parents=True, exist_ok=True)
    fp_path.write_text(json.dumps(fingerprint, indent=2) + "\n", encoding="utf-8")

    out_path = Path(args.out) if args.out else get_path(config, "results_config") / Path(SMOKE_TEST_JSON).name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    status = "FAIL"
    error: str | None = None
    actual = ""
    generation_dict: dict | None = None
    backend_used: str | None = None
    model_used: str | None = None

    try:
        backend = create_backend(model_cfg)
        backend_used = getattr(backend, "name", type(backend).__name__)
        log.info("Using backend=%s available=%s", backend_used, backend.is_available())
        if not backend.is_available() and backend_used != "llama_cpp":
            raise RuntimeError(f"Backend not available: {backend_used}")

        result = backend.generate(
            args.prompt,
            temperature=float(model_cfg.get("temperature") or 0.1),
            max_new_tokens=int(model_cfg.get("max_new_tokens") or 64),
            top_p=model_cfg.get("top_p"),
        )
        generation_dict = result.to_dict()
        actual = result.text.strip()
        model_used = result.model
        if actual:
            status = "PASS"
        else:
            error = "Generation returned empty text"
    except Exception as exc:  # noqa: BLE001 — record actual failure in evidence
        error = f"{type(exc).__name__}: {exc}"

    rel = lambda p: str(p.relative_to(project_root())) if str(p).startswith(str(project_root())) else str(p)

    validation = ValidationRecord(
        phase=7,
        test_name="phase7_llm_generation_smoke",
        command=command,
        notebook=args.notebook,
        environment=summarize_environment(fingerprint),
        expected="Configured backend produces non-empty text for the smoke prompt",
        actual=actual if actual else (error or "no output"),
        status=status,  # type: ignore[arg-type]
        error=error,
        output_path=rel(out_path),
        extra={
            "evidence_type": "smoke_test",
            "run_id": run_id,
            "prompt": args.prompt,
            "backend_used": backend_used,
            "model_used": model_used,
            "fingerprint_path": rel(fp_path),
            "evidence_md": EVIDENCE_MD,
            "generation": generation_dict,
        },
    )

    payload = validation.to_dict()
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    log.info("Validation evidence saved status=%s path=%s", status, out_path)

    summary = {
        "status": status.lower() if status == "PASS" else status,
        "phase": 7,
        "test_name": validation.test_name,
        "backend": backend_used,
        "model": model_used,
        "out": str(out_path),
        "text": actual,
        "error": error,
    }
    print(json.dumps(summary, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
