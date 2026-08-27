"""Phase 16 CPU metrics. Does not call RAG or Qwen."""

from __future__ import annotations

import json
from pathlib import Path

from src.evaluation.metrics import (
    context_precision,
    context_recall,
    files_match,
    score_case,
)
from src.evaluation.numeric import numeric_match
from src.evaluation.runner import BENCHMARK_N_CASES, assert_complete, sha256_file


def test_numeric_match_finqa_style() -> None:
    assert numeric_match("ROI is 45.51%", "0.4551")
    assert not numeric_match(
        "I cannot answer reliably because supporting evidence is insufficient.",
        "0.4551",
    )


def test_files_match_and_context_metrics() -> None:
    gold = {"file_name": "pdf/SNA/2013/page_34.pdf", "context_id": "finqa_test_ctx_130"}
    chunks = [
        {"file_name": "pdf/SNA/2013/page_34.pdf", "context_id": "finqa_test_ctx_130", "text": "return 0.455"},
        {"file_name": "pdf/OTHER/2013/page_1.pdf", "context_id": "other", "text": "unrelated"},
        {"file_name": "pdf/SNA/2013/page_34.pdf", "context_id": "finqa_test_ctx_130", "text": "more"},
        {"file_name": "pdf/DIST/2010/page_2.pdf", "context_id": "dist", "text": "distractor"},
    ]
    assert files_match("pdf/SNA/2013/page_34.pdf", "pdf/SNA/2013/page_34.pdf")
    assert context_precision(chunks, gold) == 0.5
    assert context_recall(chunks, gold) == 1.0


def test_score_case_uses_uq_draft_not_abstention_template() -> None:
    gold = {
        "file_name": "pdf/A/1.pdf",
        "context_id": "ctx",
        "program_answer": "12.5",
        "original_answer": "12.5",
    }
    case = {
        "architecture": "multi_agent_uq",
        "question_id": "finqa_test_1",
        "case_key": "multi_agent_uq:finqa_test_1",
        "decision": "ABSTAIN",
        "answer": "I cannot answer reliably because supporting evidence is insufficient.",
        "reference_answer": "12.5",
        "configuration": {"draft_answer": "The value is 12.5 percent."},
        "retrieved_evidence": [
            {"file_name": "pdf/A/1.pdf", "context_id": "ctx", "text": "value 12.5 percent"},
        ],
        "verification_result": {"verification_score": 0.8, "lexical_score": 0.7},
        "confidence": 0.4,
        "threshold": 0.65,
    }
    row = score_case(case, gold)
    assert row["answered"] is False
    assert row["answer_correctness"] == 0
    assert row["answer_correctness_claim"] == 1
    assert row["unsupported_emitted"] == 0
    assert row["used_llm_inference"] is False
    assert row["context_recall"] == 1.0


def test_cpu_evaluation_modules_do_not_call_rag_pipelines() -> None:
    import ast
    from pathlib import Path

    banned = {
        "llama_cpp",
        "src.run.benchmark",
        "src.rag.single_agent",
        "src.rag.multi_agent",
        "src.rag.multi_agent_uq",
        "src.models.factory",
    }
    imported: set[str] = set()
    cpu_files = ["__init__.py", "metrics.py", "numeric.py", "runner.py"]
    for name in cpu_files:
        py = Path("src/evaluation") / name
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    assert not (imported & banned)
    text = "\n".join((Path("src/evaluation") / name).read_text(encoding="utf-8") for name in cpu_files)
    for banned_call in ("run_single_agent", "run_multi_agent", "run_multi_agent_uq", "create_backend"):
        assert banned_call not in text


def test_canonical_raw_sha_stable_and_complete() -> None:
    raw = Path("results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl")
    if not raw.is_file():
        return
    before = sha256_file(raw)
    cases = [json.loads(line) for line in raw.read_text().splitlines() if line.strip()]
    gold_ids = {c["question_id"] for c in cases}
    gold = {qid: {"id": qid} for qid in gold_ids}
    info = assert_complete(cases, gold)
    after = sha256_file(raw)
    assert before == after
    assert info["n_unique_keys"] == BENCHMARK_N_CASES
    assert before == "f5256ae40fa8db0d6172ff9f4083bbde6c1c4fdb47916baa73529bc8215caafa"
