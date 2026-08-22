from __future__ import annotations

import streamlit as st

from app.ui import inject_css


st.set_page_config(page_title="About", layout="wide")
inject_css()

st.title("About The Project")
st.write(
    "This MSc prototype evaluates whether multi-agent retrieval-augmented generation and uncertainty "
    "quantification improve reliability for enterprise knowledge systems."
)

st.subheader("Controlled Comparison")
st.write(
    "The same documents, embedding model, vector store, and local Ollama model are used across all systems. "
    "Only the workflow changes."
)

st.subheader("Systems")
st.table(
    [
        {"System": "Single-Agent RAG", "Workflow": "Retriever -> LLM"},
        {"System": "Multi-Agent RAG", "Workflow": "Retriever -> LLM -> Verifier"},
        {
            "System": "Multi-Agent RAG + UQ",
            "Workflow": "Retriever -> LLM -> Verifier -> Uncertainty -> Decision",
        },
    ]
)

st.subheader("Research Outputs")
st.write("The automated pipeline writes `results/experiment_results.csv`, `results/summary.csv`, and dissertation charts.")
