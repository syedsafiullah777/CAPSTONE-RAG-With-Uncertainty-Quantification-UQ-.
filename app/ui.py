from __future__ import annotations

import pandas as pd
import streamlit as st

from rag.schema import RAGResult, RetrievedChunk


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .main .block-container { padding-top: 1.4rem; max-width: 1280px; }
        h1, h2, h3 { letter-spacing: 0 !important; }
        .system-title {
            font-size: 0.9rem;
            font-weight: 700;
            color: #25324a;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        .answer-box {
            border-left: 4px solid #3366cc;
            background: #f7f9fc;
            padding: 12px;
            border-radius: 4px;
            min-height: 130px;
        }
        .small-label {
            font-size: 0.78rem;
            color: #5d6678;
            font-weight: 600;
            margin-top: 12px;
        }
        .decision-answer { color: #16784f; font-weight: 700; }
        .decision-warning { color: #9a6700; font-weight: 700; }
        .decision-abstain { color: #b42318; font-weight: 700; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def confidence_text(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "Not calculated"
    return f"{value * 100:.0f}%"


def decision_class(decision: str) -> str:
    decision_lower = decision.lower()
    if "abstain" in decision_lower or "weak" in decision_lower:
        return "decision-abstain"
    if "warning" in decision_lower:
        return "decision-warning"
    return "decision-answer"


def render_chunks(chunks: list[RetrievedChunk]) -> None:
    if not chunks:
        st.caption("No evidence retrieved.")
        return
    for chunk in chunks[:3]:
        score = f" · score {chunk.score:.2f}" if chunk.score is not None else ""
        with st.expander(f"{chunk.source} · page {chunk.page}{score}"):
            st.write(chunk.text[:1200])


def render_result(result: RAGResult) -> None:
    st.markdown(f"<div class='system-title'>{result.system_name}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='answer-box'>{result.answer}</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    col_a.metric("Confidence", confidence_text(result.confidence))
    col_b.metric("Latency", f"{result.response_time:.2f}s")

    st.markdown("<div class='small-label'>Decision</div>", unsafe_allow_html=True)
    st.markdown(
        f"<span class='{decision_class(result.decision)}'>{result.decision}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='small-label'>Signals</div>", unsafe_allow_html=True)
    signals = {
        "Retrieval": result.retrieval_score,
        "Verification": result.verification_score,
        "Self-consistency": result.consistency_score,
    }
    for label, value in signals.items():
        if value is not None:
            st.progress(max(0.0, min(1.0, value)), text=f"{label}: {value:.2f}")

    st.markdown("<div class='small-label'>Retrieved Sources</div>", unsafe_allow_html=True)
    render_chunks(result.retrieved_chunks)


def render_results_table(results: list[RAGResult]) -> None:
    rows = []
    for result in results:
        rows.append(
            {
                "System": result.system_name,
                "Decision": result.decision,
                "Confidence": confidence_text(result.confidence),
                "Retrieval": "" if result.retrieval_score is None else f"{result.retrieval_score:.2f}",
                "Verification": "" if result.verification_score is None else f"{result.verification_score:.2f}",
                "Latency": f"{result.response_time:.2f}s",
                "Hallucination Risk": result.hallucination_risk,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def demo_result(system_name: str, decision: str, confidence: float | None) -> RAGResult:
    return RAGResult(
        system_name=system_name,
        answer="Demo mode: upload PDFs, build the knowledge base, and connect Ollama to generate real answers.",
        confidence=confidence,
        decision=decision,
        retrieved_chunks=[
            RetrievedChunk(
                source="Example_HR_Policy.pdf",
                page=7,
                text="Example evidence will appear here after retrieval from your uploaded enterprise PDFs.",
                score=0.82,
            )
        ],
        response_time=0.0,
        retrieval_score=0.82,
        verification_score=confidence,
        consistency_score=confidence,
        hallucination_risk="Demo",
    )
