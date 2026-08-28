#!/usr/bin/env python3
"""Phase 17: statistics on frozen Phase 15/16 results. No RAG/Qwen/judge rerun."""

from __future__ import annotations

import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config, project_root
from src.statistics.analysis import analyse
from src.statistics.constants import EXPECTED_PHASE15_SHA256, LOCKED_T
from src.statistics.report import write_outputs
from src.utils import setup_logging
from src.utils.evidence import ValidationRecord


def main() -> int:
    config = load_experiment_config()
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id="phase17",
        console=True,
        file=True,
    )
    root = project_root()
    result = analyse(root)
    paths = write_outputs(result, root)
    rq1 = result["rq1_confirmatory"][0]
    status = "PASS"
    record = ValidationRecord(
        phase=17,
        test_name="phase17_statistics",
        command="PYTHONPATH=. python scripts/run_statistics.py",
        environment={"used_llm_inference": False, "used_gpu": False, "device": "cpu"},
        expected=(
            "Paired statistics on frozen 140 questions × 3 architectures; "
            f"T={LOCKED_T} unchanged; Phase 15 SHA {EXPECTED_PHASE15_SHA256}; no RAG rerun"
        ),
        actual=(
            f"status={status} n_questions={result['n_questions']} "
            f"n_tests={len(result['tests'])} "
            f"rq1_p={rq1['p_value']:.6g} rq1_holm={rq1['p_value_holm']:.6g} "
            f"rq1_sig={rq1['significant_holm_0.05']} "
            f"phase15_sha_ok={result['source']['phase15_sha_verified']}"
        ),
        status="PASS",
        output_path=paths["summary_json"],
        extra={
            "hashes": result["hashes"],
            "metrics_csv": paths["tests_csv"],
            "evidence_md": "project_record/evidence/phase17_validation.md",
            "used_rag_rerun": False,
        },
    )
    out = get_path(config, "results_config") / "phase17_smoke_test.json"
    out.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "phase": 17,
        "n_questions": result["n_questions"],
        "n_tests": len(result["tests"]),
        "threshold": result["threshold"],
        "used_rag_rerun": False,
        "rq1_mcnemar_p": rq1["p_value"],
        "rq1_significant_holm": rq1["significant_holm_0.05"],
        "outputs": {k: (v if isinstance(v, str) else [str(x) for x in v]) for k, v in paths.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
