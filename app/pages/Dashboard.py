from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui import inject_css
from config import CHARTS_DIR, RESULTS_DIR


st.set_page_config(page_title="Research Dashboard", layout="wide")
inject_css()

st.title("Research Dashboard")
st.caption("Loads saved experiment results. It does not rerun the benchmark.")

results_path = RESULTS_DIR / "experiment_results.csv"
summary_path = RESULTS_DIR / "summary.csv"

if summary_path.exists():
    summary = pd.read_csv(summary_path)
    st.subheader("Summary Metrics")
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.subheader("Charts")
    chart_files = [
        ("Accuracy", CHARTS_DIR / "accuracy.png"),
        ("Hallucination", CHARTS_DIR / "hallucination.png"),
        ("Confidence", CHARTS_DIR / "confidence.png"),
        ("Response Time", CHARTS_DIR / "response_time.png"),
    ]
    cols = st.columns(2)
    for index, (label, path) in enumerate(chart_files):
        with cols[index % 2]:
            if path.exists():
                st.image(str(path), caption=label, use_container_width=True)
            else:
                st.info(f"{label} chart has not been generated yet.")
else:
    st.info("No summary file found yet. Run: python -m evaluation.experiment")

if results_path.exists():
    st.subheader("Experiment Results")
    results = pd.read_csv(results_path)
    st.dataframe(results, use_container_width=True, hide_index=True)
