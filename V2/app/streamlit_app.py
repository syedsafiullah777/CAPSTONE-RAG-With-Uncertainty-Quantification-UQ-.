"""V2 live artefact: run all three RAG architectures on a fresh or frozen question.

Uses the existing Phase 6 knowledge base and Phase 8–10 pipelines.
Does not look up precomputed benchmark answers.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

import streamlit as st

from src.config import get_path, load_experiment_config, project_root
from src.models.factory import create_backend
from src.models.runtime_guard import (
    LiveRuntimeError,
    live_demo_locked,
    verify_live_llama_cpp_runtime,
)
from src.rag.live import (
    ARCHITECTURE_LABELS,
    INSUFFICIENT_EVIDENCE_QUESTION,
    INSUFFICIENT_EVIDENCE_QUESTION_ID,
    LIVE_ARCHITECTURES,
    LIVE_FAILURE_DECISIONS,
    format_confidence_display,
    format_optional,
    format_threshold_display,
    load_frozen_questions,
    resolve_displayed_confidence,
    run_live_comparison,
)
from src.rag.schema import ARCHITECTURE_MULTI_AGENT_UQ, RAGCaseResult
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight
from src.utils import create_run_id


@st.cache_resource
def _cached_backend(backend_name: str):
    if live_demo_locked():
        backend_name = "llama_cpp"
    if backend_name in {"mock", "test", "ollama", "ollama_dev"} and live_demo_locked():
        raise LiveRuntimeError("Mock/Ollama are forbidden for the Colab live demo. Use llama_cpp.")
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
        col_b.markdown("**Threshold**")
        col_b.write(format_threshold_display(result))
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

    if result.architecture == ARCHITECTURE_MULTI_AGENT_UQ and resolve_displayed_confidence(result) is None:
        st.error("UQ confidence could not be calculated. Displaying n/a — this is not a valid 0.0 confidence.")

    col_a, col_b, col_c, col_d = st.columns(4)
    # Do not use st.metric for 0–1 scores: Streamlit can render 0.7688 / 0.55 as 0.
    col_a.markdown("**Confidence**")
    col_a.write(format_confidence_display(result))
    col_b.markdown("**Threshold**")
    col_b.write(format_threshold_display(result))
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
                "rationale": verify.get("rationale"),
                "verification_score": verify.get("verification_score"),
                "lexical_score": verify.get("lexical_score"),
                "llm_score": verify.get("llm_score"),
                "verification_threshold": verify.get("verification_threshold"),
            }
        )
        if verify.get("rationale") and not str(verify.get("rationale", "")).startswith(str(verify.get("status") or "")):
            st.error("Verification status and rationale are inconsistent.")

    uq = (result.configuration or {}).get("uncertainty_result")
    if uq:
        st.markdown("**Uncertainty**")
        st.write(
            {
                "method": uq.get("method"),
                "retrieval_score": uq.get("retrieval_score"),
                "verification_score": uq.get("verification_score"),
                "confidence": uq.get("confidence"),
                "displayed_confidence": format_confidence_display(result),
                "displayed_threshold": format_threshold_display(result),
                "decision": result.decision,
            }
        )

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
        require_cuda = os.environ.get("V2_REQUIRE_CUDA", "1") == "1" or live_demo_locked()
        if live_demo_locked():
            try:
                runtime = verify_live_llama_cpp_runtime(require_cuda=True)
            except LiveRuntimeError as exc:
                st.error(str(exc))
                st.error("Do not open http://127.0.0.1:8501 on the Mac. Use the Colab notebook proxy URL.")
                st.stop()
            backend_name = "llama_cpp"
            st.success(f"Backend locked: llama_cpp · GPU: {runtime.get('gpu')} · chunks: {runtime.get('index_chunks')}")
            st.caption("Mock and Ollama are disabled. This process must be Colab CUDA, not mps_capable_host.")
        else:
            backend_options = ["auto", "ollama_dev", "llama_cpp", "mock"]
            env_backend = os.environ.get("V2_LIVE_BACKEND", "auto").strip().lower()
            if env_backend not in backend_options:
                env_backend = "auto"
            backend_name = st.selectbox(
                "LLM backend",
                options=backend_options,
                index=backend_options.index(env_backend),
                help="Colab live demo locks llama_cpp. mock/ollama_dev are local UI/testing only.",
            )
            if backend_name == "llama_cpp":
                try:
                    runtime = verify_live_llama_cpp_runtime(require_cuda=require_cuda)
                    st.success(f"llama_cpp on {runtime.get('gpu')} · device={runtime.get('device')}")
                except LiveRuntimeError as exc:
                    st.error(str(exc))
                    st.error("llama_cpp live demo requires Colab CUDA. This Mac process would report mps_capable_host.")
                    st.stop()
            if backend_name == "mock":
                st.warning("Mock backend is for UI/testing only. It must not be treated as a real RAG answer.")
            if backend_name in {"ollama", "ollama_dev"}:
                st.warning("Ollama is local-dev only. The Colab live demo must use llama_cpp.")
        threshold = st.number_input(
            "UQ smoke/demo threshold (NOT LOCKED)",
            min_value=0.0,
            max_value=1.0,
            value=default_threshold,
            step=0.05,
            help="Smoke/demo gate only. The experimental threshold is NOT LOCKED and must be calibrated later on the 40-question DEV set.",
        )
        st.caption("Threshold status: **NOT LOCKED**. This is not the final research threshold.")
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

    source = st.radio(
        "Question source",
        options=["Fresh question", "Frozen test case", "Insufficient-evidence demo"],
        horizontal=True,
    )
    frozen = _cached_frozen_questions()
    reference_answer = None
    question_id = None
    question_source = "fresh"

    if source == "Insufficient-evidence demo":
        question = INSUFFICIENT_EVIDENCE_QUESTION
        question_id = INSUFFICIENT_EVIDENCE_QUESTION_ID
        question_source = "insufficient"
        st.warning(
            "This question is outside the FinQA source-PDF corpus. "
            "It is for demonstrating weak support / possible ABSTAIN. Abstention is not forced."
        )
        st.write(question)
    elif source == "Frozen test case":
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

        payload = comparison.to_dict()
        devices = {((payload.get("results") or {}).get(name) or {}).get("device") for name in LIVE_ARCHITECTURES}
        if "mps_capable_host" in devices:
            st.error(
                "device=mps_capable_host means this browser hit the Mac Streamlit process "
                "(127.0.0.1:8501), not Colab T4. Close this tab and open the Colab proxy URL."
            )
            st.stop()
        st.session_state["live_comparison"] = payload
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
                "Confidence": "n/a" if failed else format_confidence_display(RAGCaseResult(**data)),
                "Threshold": format_threshold_display(RAGCaseResult(**data)),
                "Verification": None if failed else verify.get("verification_score"),
                "n_evidence": len(data.get("retrieved_evidence") or []),
                "Latency (s)": data.get("latency_seconds"),
                "Error": data.get("error"),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
