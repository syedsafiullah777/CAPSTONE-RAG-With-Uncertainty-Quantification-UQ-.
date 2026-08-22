#!/usr/bin/env python3
"""Phase 7 smoke: fingerprint + one generation through the LLM backend abstraction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config, project_root
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.utils import create_run_id, get_logger, setup_logging


DEFAULT_PROMPT = (
    "Answer briefly using one short sentence. "
    "What is 2 + 2? Reply with only the number."
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test Qwen3-8B backend generation")
    parser.add_argument(
        "--backend",
        default=None,
        help="Override backend: auto|llama_cpp|transformers|ollama_dev|mock",
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON path (default: results/config/phase7_smoke_generate.json)",
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
    if args.backend:
        model_cfg["backend"] = args.backend

    fingerprint = collect_fingerprint(model_config=model_cfg, project_root=str(project_root()))
    fp_path = get_path(config, "results_config") / "phase7_runtime_fingerprint.json"
    fp_path.parent.mkdir(parents=True, exist_ok=True)
    fp_path.write_text(json.dumps(fingerprint, indent=2) + "\n", encoding="utf-8")
    log.info(
        "Fingerprint saved device=%s cuda=%s backend_cfg=%s",
        fingerprint.get("device"),
        fingerprint.get("torch", {}).get("cuda_available"),
        model_cfg.get("backend"),
    )

    backend = create_backend(model_cfg)
    log.info("Using backend=%s available=%s", getattr(backend, "name", type(backend)), backend.is_available())
    if not backend.is_available() and getattr(backend, "name", "") != "llama_cpp":
        # llama_cpp reports available before download; others should be truly available.
        raise RuntimeError(f"Backend not available: {backend.name}")

    result = backend.generate(
        args.prompt,
        temperature=float(model_cfg.get("temperature") or 0.1),
        max_new_tokens=int(model_cfg.get("max_new_tokens") or 64),
        top_p=model_cfg.get("top_p"),
    )
    out_path = Path(args.out) if args.out else get_path(config, "results_config") / "phase7_smoke_generate.json"
    payload = {
        "phase": 7,
        "run_id": run_id,
        "prompt": args.prompt,
        "generation": result.to_dict(),
        "fingerprint_path": str(fp_path),
        "notes": {
            "primary_remote_strategy": "standard Google Colab GPU notebooks (notebooks/colab_phase7_smoke.ipynb)",
            "colab_cli": False,
            "primary_benchmark_backend": "llama_cpp or transformers on Colab GPU",
            "ollama_dev": "optional local smoke only; not required for final 420-case benchmark",
            "next_validation_step": "Colab GPU verification NEEDS_VERIFICATION",
        },
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    log.info(
        "Generation ok backend=%s model=%s latency=%.2fs text_preview=%r",
        result.backend,
        result.model,
        result.latency_seconds,
        result.text[:120],
    )
    print(json.dumps({"status": "ok", "backend": result.backend, "model": result.model, "out": str(out_path), "text": result.text}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
