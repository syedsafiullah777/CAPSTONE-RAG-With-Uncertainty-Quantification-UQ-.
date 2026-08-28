#!/usr/bin/env python3
"""Phase 19: read-only reproducibility audit. Does not rerun RAG, judge, or statistics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.audit.checks import run_audit
from src.audit.report import write_audit_documents
from src.config import get_path, load_experiment_config, project_root
from src.utils import setup_logging
from src.utils.evidence import ValidationRecord


def main() -> int:
    config = load_experiment_config()
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id="phase19",
        console=True,
        file=True,
    )
    root = project_root()
    result = run_audit(root)
    paths = write_audit_documents(result, root)
    record = ValidationRecord(
        phase=19,
        test_name="phase19_reproducibility_audit",
        command="PYTHONPATH=. python scripts/run_reproducibility_audit.py",
        environment={
            "used_llm_inference": False,
            "used_gpu": False,
            "used_rag_rerun": False,
            "recomputed_statistics": False,
            "device": "cpu",
        },
        expected=(
            "Read-only consistency of frozen 40 DEV → T=0.65 → 140 test → 420 cases → "
            "Phase 16/17/18 artefacts; no RAG/Qwen/judge/stats rerun"
        ),
        actual=(
            f"overall={result['overall']} n_pass={result['n_pass']} "
            f"n_fail={result['n_fail']} n_needs_verification={result['n_needs_verification']} "
            f"chain_fail={result['chain_fail']}"
        ),
        status="PASS" if result["overall"] == "PASS" else (
            "FAIL" if result["overall"] == "FAIL" else "NEEDS_VERIFICATION"
        ),
        output_path=str(root / paths["evidence"]),
        extra={
            "hashes": result.get("hashes"),
            "manifest": paths["manifest"],
            "used_rag_rerun": False,
            "recomputed_statistics": False,
        },
    )
    out = get_path(config, "results_config") / "phase19_audit.json"
    payload = record.to_dict()
    payload["checks"] = result["checks"]
    payload["overall"] = result["overall"]
    payload["paths"] = paths
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["overall"],
        "phase": 19,
        "n_pass": result["n_pass"],
        "n_fail": result["n_fail"],
        "n_needs_verification": result["n_needs_verification"],
        "chain_fail": result["chain_fail"],
        "used_rag_rerun": False,
        "recomputed_statistics": False,
        "outputs": paths,
        "audit_json": str(out.relative_to(root)),
    }, indent=2))
    return 0 if result["overall"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
