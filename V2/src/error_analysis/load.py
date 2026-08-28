"""Load frozen Phase 15 raw + Phase 16 scores + official judge. Read-only."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from src.config import project_root
from src.error_analysis.constants import FORBIDDEN_ERROR_ANALYSIS_IMPORTS
from src.statistics.constants import ARCHITECTURES, PHASE15_REL
from src.statistics.load import load_joined, verify_frozen_hashes


def verify_no_generation_or_stats_rerun() -> None:
    pkg = Path(__file__).resolve().parent
    imported: set[str] = set()
    for py in pkg.glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    banned = imported & FORBIDDEN_ERROR_ANALYSIS_IMPORTS
    if banned:
        raise RuntimeError(f"Phase 18 must not import generation/stats-rerun stack: {sorted(banned)}")


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def load_universe(root: Path | None = None) -> dict[str, Any]:
    """Join frozen artefacts. Does not rewrite Phase 15/16 JSONL or statistics tables."""
    verify_no_generation_or_stats_rerun()
    root = root or project_root()
    hashes = verify_frozen_hashes(root)
    joined = load_joined(root)
    raw_rows = _jsonl(root / PHASE15_REL)
    raw_by_key = {str(row["case_key"]): row for row in raw_rows}
    if len(raw_by_key) != len(raw_rows):
        raise ValueError("Duplicate Phase 15 case_key")

    cases: list[dict[str, Any]] = []
    for qid in joined["question_ids"]:
        for arch in ARCHITECTURES:
            scored = joined["by_question"][qid][arch]
            key = str(scored["case_key"])
            raw = raw_by_key[key]
            chunks = list(raw.get("retrieved_evidence") or [])
            files = []
            for chunk in chunks:
                name = str(chunk.get("file_name") or "")
                if name and name not in files:
                    files.append(name)
            verify = raw.get("verification_result") if isinstance(raw.get("verification_result"), dict) else {}
            cfg = raw.get("configuration") or {}
            draft = cfg.get("draft_answer")
            cases.append({
                "case_key": key,
                "question_id": qid,
                "architecture": arch,
                "question": str(raw.get("question") or ""),
                "displayed_answer": str(raw.get("answer") or ""),
                "draft_answer": str(draft) if draft else "",
                "reference_answer": str(raw.get("reference_answer") or scored.get("gold_program_answer") or ""),
                "gold_program_answer": scored.get("gold_program_answer"),
                "gold_file_name": scored.get("gold_file_name"),
                "gold_context_id": scored.get("gold_context_id"),
                "retrieved_files": files,
                "retrieval_scores": list(raw.get("retrieval_scores") or []),
                "n_evidence": int(scored.get("n_evidence") or len(chunks)),
                "context_precision": float(scored["context_precision"]),
                "context_recall": float(scored["context_recall"]),
                "context_recall_numeric": int(scored["context_recall_numeric"]),
                "displayed_correct": int(scored["answer_correctness"]),
                "claim_correct": int(scored["answer_correctness_claim"]),
                "decision": str(scored.get("decision") or "ANSWER"),
                "answered": bool(scored.get("answered")),
                "confidence": scored.get("confidence"),
                "threshold": scored.get("threshold"),
                "llm_faithfulness": float(scored["llm_faithfulness"]),
                "token_overlap": float(scored["faithfulness"]),
                "verification_status": verify.get("status"),
                "verification_score": verify.get("verification_score"),
                "verification_lexical_score": verify.get("lexical_score"),
                "unsupported_emitted": int(scored["unsupported_emitted"]),
            })

    if len(cases) != 420:
        raise ValueError(f"Expected 420 cases, found {len(cases)}")
    return {
        "cases": cases,
        "by_key": {row["case_key"]: row for row in cases},
        "question_ids": list(joined["question_ids"]),
        "hashes": hashes,
        "threshold": joined["threshold"],
        "used_rag_rerun": False,
        "used_llm_inference": False,
    }
