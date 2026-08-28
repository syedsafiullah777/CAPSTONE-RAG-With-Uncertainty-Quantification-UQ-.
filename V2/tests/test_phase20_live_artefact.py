"""Phase 20 live artefact: locked T, no benchmark lookup, frozen artefacts unchanged."""

from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import patch

from src.evaluation.runner import sha256_file
from src.models.mock_backend import MockBackend
from src.rag.live import (
    FRESH_KB_QUESTION,
    INSUFFICIENT_EVIDENCE_QUESTION,
    LIVE_ARCHITECTURES,
    format_threshold_display,
    load_frozen_questions,
    resolve_live_locked_threshold,
    run_live_comparison,
)
from src.rag.schema import ARCHITECTURE_MULTI_AGENT_UQ, RAGCaseResult
from src.retrieval.retriever import RetrievedChunk
from src.statistics.constants import (
    EXPECTED_CAL40_SHA256,
    EXPECTED_FROZEN140_SHA256,
    EXPECTED_JUDGE_SHA256,
    EXPECTED_LOCK_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
)


def _chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="c1",
        text="Snap-on cumulative total shareholder return December 31, 2013 315.72.",
        score=0.88,
        doc_id="d1",
        file_name="pdf/SNA/2013/page_34.pdf",
        split="test",
        page=1,
        company_symbol="SNA",
        report_year="2013",
        role="test",
        context_id="finqa_test_ctx_130",
        source_type="pdf",
    )


def test_live_uses_locked_threshold_not_smoke() -> None:
    assert abs(resolve_live_locked_threshold() - 0.65) < 1e-9
    chunk = _chunk()
    with (
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        comparison = run_live_comparison(
            "What was Snap-on TSR in 2013?",
            question_source="fresh",
            backend=MockBackend(canned="315.72"),
            backend_name="mock",
            run_id="phase20_test",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
            threshold=0.55,
        )
    uq = comparison.results[ARCHITECTURE_MULTI_AGENT_UQ]
    assert abs(float(uq.threshold) - 0.65) < 1e-9
    assert (uq.configuration or {}).get("threshold_source") == "locked"
    assert "locked" in format_threshold_display(uq)
    assert "NOT LOCKED" not in format_threshold_display(uq)
    assert comparison.used_precomputed_benchmark_lookup is False
    assert abs(float(comparison.locked_threshold or 0) - 0.65) < 1e-9
    assert set(comparison.results) == set(LIVE_ARCHITECTURES)


def test_fresh_and_insufficient_questions_are_not_in_frozen_set() -> None:
    frozen_questions = {row["question"] for row in load_frozen_questions()}
    frozen_ids = {row["id"] for row in load_frozen_questions()}
    assert FRESH_KB_QUESTION not in frozen_questions
    assert INSUFFICIENT_EVIDENCE_QUESTION not in frozen_questions
    assert "live_insufficient_evidence" not in frozen_ids


def test_live_and_streamlit_do_not_lookup_phase15() -> None:
    forbidden_tokens = (
        "phase15_benchmark",
        "phase16_cases.jsonl",
        "phase16_judge",
        "results/raw/phase15",
    )
    for rel in (
        "src/rag/live.py",
        "src/rag/benchmark_catalogue.py",
        "app/streamlit_app.py",
        "app/benchmark_ui.py",
    ):
        text = Path(rel).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text
        tree = ast.parse(text)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
            elif isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
        assert "src.run.benchmark" not in imported
        assert "src.evaluation.runner" not in imported
        if rel in {"src/rag/benchmark_catalogue.py", "app/benchmark_ui.py"}:
            assert "src.rag.single_agent" not in imported
            assert "src.rag.multi_agent" not in imported
            assert "src.rag.multi_agent_uq" not in imported
            assert "src.models.factory" not in imported
            assert "src.rag.live" not in imported


def test_streamlit_exposes_locked_threshold_and_runtime_fields() -> None:
    text = Path("app/streamlit_app.py").read_text(encoding="utf-8")
    assert "UQ smoke/demo threshold (NOT LOCKED)" not in text
    assert "number_input" not in text
    assert "resolve_live_locked_threshold" in text
    assert "Retrieved evidence" in text
    assert "Verification" in text
    assert "Confidence" in text
    assert "Decision" in text
    assert "backend" in text
    assert "gpu" in text
    assert "No answer (run failed)" in text
    assert "run_live_comparison" in text
    assert "cases.jsonl" not in text
    assert "Benchmark Questions" in text
    assert "Live RAG Demo" in text
    ui = Path("app/benchmark_ui.py").read_text(encoding="utf-8")
    assert "Frozen FinQA Test Set — 140 Questions" in ui
    assert "Read-only reference for live demonstration" in ui
    assert "Use this question in Live Demo" in ui
    assert "run_live_comparison" not in ui
    assert "create_backend" not in ui


def test_live_comparison_does_not_rewrite_frozen_artefacts() -> None:
    watched = (
        Path("data/final/selected_140_questions.csv"),
        Path("data/calibration/calibration_questions.csv"),
        Path("results/config/threshold.lock.json"),
        Path("results/raw/phase15_benchmark/phase15_20260826T203744Z_dae9c3a4/cases.jsonl"),
        Path("results/processed/phase16_cases.jsonl"),
        Path("results/raw/phase16_judge/phase16_judge_20260828T152623Z_06661255/judge.jsonl"),
    )
    expected = {
        watched[0]: EXPECTED_FROZEN140_SHA256,
        watched[1]: EXPECTED_CAL40_SHA256,
        watched[2]: EXPECTED_LOCK_SHA256,
        watched[3]: EXPECTED_PHASE15_SHA256,
        watched[4]: EXPECTED_PROCESSED_SHA256,
        watched[5]: EXPECTED_JUDGE_SHA256,
    }
    before = {path: sha256_file(path) for path in watched}
    chunk = _chunk()
    with (
        patch("src.rag.single_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent.retrieve", return_value=[chunk]),
        patch("src.rag.multi_agent_uq.retrieve", return_value=[chunk]),
    ):
        run_live_comparison(
            INSUFFICIENT_EVIDENCE_QUESTION,
            question_source="insufficient",
            backend=MockBackend(canned="I cannot find this in the filings."),
            backend_name="mock",
            run_id="phase20_hash_guard",
            fingerprint={"device": "cpu", "gpu": {"available": False}},
        )
    after = {path: sha256_file(path) for path in watched}
    assert before == after
    assert before == expected


def test_locked_threshold_display_helper() -> None:
    result = RAGCaseResult(
        run_id="r",
        question_id="q",
        architecture=ARCHITECTURE_MULTI_AGENT_UQ,
        question="Q?",
        retrieved_evidence=[{"text": "e"}],
        retrieval_scores=[0.3],
        answer="Abstain",
        confidence=0.4,
        threshold=0.65,
        decision="ABSTAIN",
        configuration={"threshold_source": "locked"},
    )
    assert format_threshold_display(result) == "0.6500 (locked)"


def test_frozen_catalogue_loads_140_unique_matching_csv() -> None:
    from src.rag.benchmark_catalogue import (
        FROZEN_N,
        filter_catalogue,
        live_prefill_from_row,
        load_frozen_catalogue,
        paginate,
        validate_catalogue,
    )

    csv_path = Path("data/final/selected_140_questions.csv")
    before = sha256_file(csv_path)
    rows = load_frozen_catalogue()
    after = sha256_file(csv_path)
    assert before == after == EXPECTED_FROZEN140_SHA256
    check = validate_catalogue(rows)
    assert check["ok"] is True
    assert check["n"] == FROZEN_N
    assert check["unique_ids"] == FROZEN_N
    ids = [row["id"] for row in rows]
    assert ids[0] == "finqa_test_1000"
    assert len(ids) == len(set(ids))

    import csv as csv_mod

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        csv_ids = [row["id"] for row in csv_mod.DictReader(handle)]
    assert ids == csv_ids
    assert len(csv_ids) == FROZEN_N

    page2, showing_from, showing_to, n_total, page, n_pages = paginate(rows, 2, 20)
    assert n_total == FROZEN_N
    assert page == 2
    assert n_pages == 7
    assert showing_from == 21
    assert showing_to == 40
    assert len(page2) == 20
    assert page2[0]["id"] == csv_ids[20]

    snap = filter_catalogue(rows, id_query="finqa_test_1000")
    assert len(snap) == 1
    assert "S&P 500" in snap[0]["question"]
    text_hits = filter_catalogue(rows, text_query="shareholder return")
    assert 1 <= len(text_hits) < FROZEN_N
    company = rows[0]["company_name"]
    company_hits = filter_catalogue(rows, company=company)
    assert company_hits
    assert all(row["company_name"] == company for row in company_hits)

    prefill = live_prefill_from_row(snap[0])
    assert prefill["question"] == snap[0]["question"]
    assert prefill["source_id"] == "finqa_test_1000"
    assert "program_answer" not in prefill
    assert snap[0]["program_answer"]
    assert prefill["question"] != snap[0]["program_answer"]
