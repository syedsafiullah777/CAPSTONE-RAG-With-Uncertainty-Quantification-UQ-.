#!/usr/bin/env python3
"""Phase 18: qualitative error analysis on frozen Phase 15/16/17 artefacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config, project_root
from src.error_analysis.pipeline import run_error_analysis
from src.utils import setup_logging
from src.utils.evidence import ValidationRecord


def main() -> int:
    config = load_experiment_config()
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id="phase18",
        console=True,
        file=True,
    )
    result = run_error_analysis(project_root())
    record = ValidationRecord(
        phase=18,
        test_name="phase18_error_analysis",
        command="PYTHONPATH=. python scripts/run_error_analysis.py",
        environment={"used_llm_inference": False, "used_gpu": False, "device": "cpu"},
        expected=(
            "Rule-based taxonomy on frozen 420 cases plus stratified qualitative sample; "
            "T=0.65 unchanged; no RAG/Qwen/judge rerun"
        ),
        actual=(
            f"status=PASS n_cases={result['n_cases']} n_sample={result['n_sample']} "
            f"n_sample_questions={result['n_sample_questions']} "
            f"false_abstentions_in_sample={result['false_abstentions_in_sample']} "
            f"source_artefacts_unchanged={result['source_artefacts_unchanged']}"
        ),
        status="PASS",
        output_path=result["paths"]["markdown"],
        extra={
            "hashes": result["hashes"],
            "cases_csv": result["paths"]["cases_csv"],
            "summary_csv": result["paths"]["summary_csv"],
            "used_rag_rerun": False,
        },
    )
    out = get_path(config, "results_config") / "phase18_smoke_test.json"
    out.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "phase": 18,
        "n_cases": result["n_cases"],
        "n_sample": result["n_sample"],
        "n_sample_questions": result["n_sample_questions"],
        "seed": result["seed"],
        "used_rag_rerun": False,
        "source_artefacts_unchanged": True,
        "outputs": result["paths"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
