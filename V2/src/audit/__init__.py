"""Phase 19 read-only reproducibility audit. Does not rerun RAG, judge, or statistics."""

from __future__ import annotations

import ast
from pathlib import Path

from src.statistics.constants import FORBIDDEN_IMPORT_MODULES

FORBIDDEN_AUDIT_IMPORTS = FORBIDDEN_IMPORT_MODULES | {
    "src.statistics.analysis",
    "src.evaluation.judge_runner",
    "src.error_analysis.pipeline",
}


def verify_audit_does_not_import_generation() -> None:
    pkg = Path(__file__).resolve().parent
    imported: set[str] = set()
    for py in pkg.glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    banned = imported & FORBIDDEN_AUDIT_IMPORTS
    if banned:
        raise RuntimeError(f"Phase 19 audit must not import generation/stats-rerun stack: {sorted(banned)}")
