"""V2 live artefact: run all three RAG architectures on a fresh or frozen question.

Uses the existing Phase 6 knowledge base and Phase 8–10 pipelines.
Does not look up precomputed benchmark answers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

import streamlit as st

from src.config import get_path, load_experiment_config, project_root
from src.models.factory import create_backend
from src.rag.live import (
    ARCHITECTURE_LABELS,
    LIVE_ARCHITECTURES,
    LIVE_FAILURE_DECISIONS,
    format_optional,
    load_frozen_questions,
    run_live_comparison,
)
from src.rag.schema import RAGCaseResult
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight
from src.utils import create_run_id


@st.cache_resource
def _cached_backend(backend_name: str):
    config = load_experiment_config()
    model_cfg = dict(config.section("model"))
    model_cfg["backend"] = backend_name
    return create_backend(model_cfg)


@st.cache_data
def _cached_frozen_questions() -> list[dict[str, str]]:
    return load_frozen_questions()


def _index_preflight() -> dict:
    config = load_experiment_config()
    retrieval_cfg = config.section("retrieval")
    index_dir = get_path(config, "kb_index")
    manifest_rel = str(retrieval_cfg.get("index_manifest") or "knowledge_base/index/index_manifest.json")
    manifest_file = (project_root() / manifest_rel).resolve()
    collection_name = str(retrieval_cfg.get("collection_name") or COLLECTION_NAME)
    return validate_index_preflight(
        index_dir,
        manifest_path=manifest_file,
        collection_name=collection_name,
    )


def _save_live_result(comparison) -> Path:
    out_dir = get_path(load_experiment_config(), "results_raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "live_sessions.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(comparison.to_dict()) + "\n")
    return path


def render_evidence(chunks: list[dict]) -> None:
    if not chunks:
        st.caption("No evidence retrieved.")
        return
    for idx, chunk in enumerate(chunks, start=1):
        score = chunk.get("score")
        title = f"[{idx}] {chunk.get('file_name') or chunk.get('doc_id') or 'chunk'}"
        if score is not None:
            title += f" · score {float(score):.4f}"
        with st.expander(title, expanded=idx == 1):
            st.markdown(
                f"**chunk_id:** `{chunk.get('chunk_id')}`  \n"
                f"**company:** {chunk.get('company_symbol')} · **year:** {chunk.get('report_year')}  \n"
                f"**role:** {chunk.get('role')} · **split:** {chunk.get('split')}"
            )
            st.write(chunk.get("text") or "")


def render_architecture(result: RAGCaseResult) -> None:
    label = ARCHITECTURE_LABELS.get(result.architecture, result.architecture)
    st.subheader(label)
    st.caption(f"`{result.architecture}` · `{result.case_key}`")

    failed = result.decision in LIVE_FAILURE_DECISIONS or bool(result.error) or not result.retrieved_evidence
    if failed:
        st.error(f"Status: {result.decision if result.decision in LIVE_FAILURE_DECISIONS else 'ERROR / UNAVAILABLE'}")
        st.error(result.error or "Retrieval or generation failed; this is not a successful RAG run.")
        st.markdown("**Generated answer**")
        st.caption("No answer (run failed). Nothing was fabricated.")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Confidence", "n/a")
        col_b.metric("Threshold", format_optional(result.threshold))
        col_c.metric("Latency (s)", format_optional(result.latency_seconds))
        col_d.metric("Evidence chunks", str(len(result.retrieved_evidence or [])))
        st.markdown("**Verification**")
        st.caption("Not available — run failed.")
        st.markdown("**Runtime**")
        st.write(
            {
                "backend": result.backend,
                "model": result.model,
                "device": result.device,
                "error": result.error,
            }
        )
        st.markdown("**Retrieved evidence / scores / metadata**")
        render_evidence(result.retrieved_evidence or [])
        return

    decision = result.decision or "n/a"
    if decision == "ABSTAIN":
        st.error(f"Decision: {decision}")
    else:
        st.success(f"Decision: {decision}")

    st.markdown("**Generated answer**")
    st.write(result.answer)

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Confidence", format_optional(result.confidence))
    col_b.metric("Threshold", format_optional(result.threshold))
    col_c.metric("Latency (s)", format_optional(result.latency_seconds))
    col_d.metric("Evidence chunks", str(len(result.retrieved_evidence or [])))

    st.markdown("**Verification**")
    verify = result.verification_result
    if not verify:
        st.caption("Not applicable for this architecture.")
    else:
        st.write(
            {
                "status": verify.get("status"),
                "verification_score": verify.get("verification_score"),
                "lexical_score": verify.get("lexical_score"),
                "llm_score": verify.get("llm_score"),
                "verification_threshold": verify.get("verification_threshold"),
            }
        )

    uq = (result.configuration or {}).get("uncertainty_result")
    if uq:
        st.markdown("**Uncertainty**")
        st.write(uq)

    st.markdown("**Runtime**")
    st.write(
        {
            "backend": result.backend,
            "model": result.model,
            "quantisation": result.quantisation,
            "device": result.device,
            "gpu": result.gpu,
            "latency_seconds": result.latency_seconds,
        }
    )

    st.markdown("**Retrieved evidence / scores / metadata**")
    if result.retrieval_scores:
        st.caption("Retrieval scores: " + ", ".join(f"{s:.4f}" for s in result.retrieval_scores))
    render_evidence(result.retrieved_evidence or [])


def main() -> None:
    st.set_page_config(page_title="V2 Live RAG Comparison", layout="wide")
    st.title("V2 Live RAG Comparison")
    st.write(
        "Ask a **fresh question** or replay a **frozen FinQA test case**. "
        "Each architecture runs independently on the same original question "
        "using the shared Phase 6 knowledge base. This is not a benchmark lookup."
    )

    config = load_experiment_config()
    uq_cfg = config.section("uncertainty")
    default_threshold = float(uq_cfg.get("smoke_threshold") or 0.55)

    with st.sidebar:
        st.header("Runtime")
        backend_name = st.selectbox(
            "LLM backend",
            options=["auto", "ollama_dev", "llama_cpp", "mock"],
            index=0,
            help="mock is for UI/testing only and does not replace a real LLM. Colab/GPU: llama_cpp.",
        )
        if backend_name == "mock":
            st.warning("Mock backend is for UI/testing only. It must not be treated as a real RAG answer.")
        threshold = st.number_input(
            "UQ smoke threshold",
            min_value=0.0,
            max_value=1.0,
            value=default_threshold,
            step=0.05,
            help="Demo/smoke only. The locked benchmark threshold is not set yet and must be calibrated on the 40-question DEV set.",
        )
        save_raw = st.checkbox("Append raw result to results/raw/live_sessions.jsonl", value=True)
        st.caption("Frozen 140 / calibration 40 are not modified.")

        try:
            preflight = _index_preflight()
            st.success(
                f"KB preflight PASS · {preflight['actual_count']} chunks"
            )
        except IndexPreflightError as exc:
            st.error(str(exc))
            st.stop()

    source = st.radio("Question source", options=["Fresh question", "Frozen test case"], horizontal=True)
    frozen = _cached_frozen_questions()
    reference_answer = None
    question_id = None
    question_source = "fresh"

    if source == "Frozen test case":
        labels = [f"{row['id']}: {row['question'][:90]}" for row in frozen]
        chosen = st.selectbox("Frozen 140 question", options=labels)
        row = frozen[labels.index(chosen)]
        question = row["question"]
        question_id = row["id"]
        reference_answer = row.get("program_answer")
        question_source = "frozen"
        st.info(f"Using frozen question `{question_id}` (read-only).")
        st.write(question)
    else:
        question = st.text_area(
            "Fresh question",
            placeholder="Ask a financial-document question over the shared FinQA source-PDF index.",
            height=120,
        )
        question_source = "fresh"

    if st.button("Run all three architectures", type="primary"):
        if not (question or "").strip():
            st.warning("Enter a question first.")
            st.stop()

        with st.spinner("Running Single-Agent, Multi-Agent, and Uncertainty/Abstention independently…"):
            backend = _cached_backend(backend_name)
            comparison = run_live_comparison(
                question.strip(),
                question_id=question_id,
                question_source=question_source,
                reference_answer=reference_answer,
                backend=backend,
                backend_name=backend_name,
                run_id=create_run_id("phase11"),
                threshold=float(threshold),
            )

        st.session_state["live_comparison"] = comparison.to_dict()
        if save_raw:
            path = _save_live_result(comparison)
            st.caption(f"Saved raw comparison to `{path}`.")

    payload = st.session_state.get("live_comparison")
    if not payload:
        st.caption("No live run yet.")
        return

    st.divider()
    st.markdown(f"**Run:** `{payload.get('run_id')}` · **question_id:** `{payload.get('question_id')}` · **source:** {payload.get('question_source')}")
    st.markdown(f"**Question:** {payload.get('question')}")
    if payload.get("error"):
        st.error(f"Live comparison error: {payload.get('error')}")

    cols = st.columns(3)
    results = payload.get("results") or {}
    for col, architecture in zip(cols, LIVE_ARCHITECTURES, strict=True):
        with col:
            data = results.get(architecture)
            if not data:
                st.warning(f"Missing result for {architecture}")
                continue
            render_architecture(RAGCaseResult(**data))

    st.divider()
    st.subheader("Side-by-side summary")
    rows = []
    for architecture in LIVE_ARCHITECTURES:
        data = results.get(architecture) or {}
        verify = data.get("verification_result") or {}
        failed = data.get("decision") in LIVE_FAILURE_DECISIONS or data.get("error")
        rows.append(
            {
                "Architecture": ARCHITECTURE_LABELS.get(architecture, architecture),
                "Decision": data.get("decision"),
                "Confidence": None if failed else data.get("confidence"),
                "Threshold": data.get("threshold"),
                "Verification": None if failed else verify.get("verification_score"),
                "n_evidence": len(data.get("retrieved_evidence") or []),
                "Latency (s)": data.get("latency_seconds"),
                "Error": data.get("error"),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
