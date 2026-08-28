#!/usr/bin/env python3
"""Redraw Phase 17 dissertation figures from saved results. Does not recompute tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import project_root
from src.statistics.figures import APPENDIX, PRIMARY, render_from_saved
from src.statistics.load import sha256_file, verify_frozen_hashes

RESULT_FILES = (
    "results/metrics/phase17_descriptive.csv",
    "results/metrics/phase17_tests.csv",
    "results/metrics/phase17_effect_sizes.csv",
    "results/metrics/phase17_assumptions.csv",
    "results/metrics/phase17_summary.md",
    "results/config/phase17_statistics_summary.json",
    "results/final/phase17_interpretation.md",
    "results/processed/phase16_cases.jsonl",
)


def main() -> int:
    root = project_root()
    fig_dir = root / "results" / "metrics" / "phase17_figures"
    before_names = sorted(p.name for p in fig_dir.iterdir() if p.is_file()) if fig_dir.is_dir() else []
    hashes_before = verify_frozen_hashes(root)
    result_before = {rel: sha256_file(root / rel) for rel in RESULT_FILES}
    written = render_from_saved(root)
    hashes_after = verify_frozen_hashes(root)
    result_after = {rel: sha256_file(root / rel) for rel in RESULT_FILES}
    if hashes_before != hashes_after:
        raise RuntimeError("Frozen artefact hashes changed during figure render")
    if result_before != result_after:
        raise RuntimeError("Phase 17 result files changed during figure render")

    after_names = sorted(p.name for p in fig_dir.iterdir() if p.is_file())
    removed = sorted(set(before_names) - set(after_names))

    written_rel = {
        key: [str(Path(path).resolve().relative_to(root.resolve())) for path in paths]
        for key, paths in written.items()
    }

    payload = {
        "status": "PASS",
        "phase": 17,
        "task": "figure_cleanup_canonical_set",
        "used_rag_rerun": False,
        "used_llm_inference": False,
        "recomputed_statistics": False,
        "primary": list(PRIMARY),
        "appendix": list(APPENDIX),
        "written": written_rel,
        "removed_redundant": removed,
        "canonical_directory_listing": after_names,
        "frozen_hashes_unchanged": True,
        "result_file_hashes_unchanged": True,
        "result_file_sha256": result_after,
        "frozen_sha256": hashes_after,
    }
    out = root / "results" / "config" / "phase17_figure_render.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "recomputed_statistics": False,
        "primary": list(PRIMARY),
        "appendix": list(APPENDIX),
        "n_files_written": sum(len(v) for v in written.values()),
        "removed_redundant": removed,
        "result_files_unchanged": True,
        "output": str(out),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
