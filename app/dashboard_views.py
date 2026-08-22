from __future__ import annotations

import platform
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

import pandas as pd
import plotly.express as px
import streamlit as st

from config import (
    ANSWER_THRESHOLD,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    OLLAMA_MODEL,
    PROJECT_ROOT,
    RANDOM_SEED,
    RESULTS_DIR,
    TOP_K,
    WARNING_THRESHOLD,
)
from app.dashboard_components import (
    bar_chart,
    compare_metric_bars,
    dataframe_frame,
    download_button,
    empty_state,
    hist_chart,
    inject_dashboard_css,
    line_chart,
    radar_chart,
    render_hero,
    render_kpis,
    scatter_chart,
    timeline_chart,
)
from app.dashboard_data import (
    format_percentage,
    load_benchmark_question_count,
    load_error_analysis_text,
    load_error_cases,
    load_final_results,
    load_document_text,
    load_phase3_comparison,
    load_phase3_summary,
    load_phase3_threshold,
    load_phase5_bins,
    load_phase5_metrics,
    load_phase5_report,
    load_source_documents,
    load_summary_by_dataset,
    load_summary_by_system,
    pick_best_question,
    unique_questions,
)


ARCHITECTURE_ASSETS_DIR = PROJECT_ROOT / "assets" / "architecture"
ARCHITECTURE_MANIFEST_PATHS = [ARCHITECTURE_ASSETS_DIR / "architecture_manifest.md"]


def _resolve_architecture_image(file_name: str) -> Path | None:
    search_roots = [
        ARCHITECTURE_ASSETS_DIR,
        PROJECT_ROOT / "assets",
    ]
    for root in search_roots:
        candidate = root / file_name
        if candidate.exists():
            return candidate
    return None


def load_architecture_manifest() -> list[dict[str, str]]:
    manifest_path = next((path for path in ARCHITECTURE_MANIFEST_PATHS if path.exists()), None)
    if manifest_path is None:
        return [
            {
                "title": "System Architecture",
                "file": "system_architecture.png",
                "caption": "End-to-end system architecture.",
                "short_explanation": "Overall workflow from benchmark selection to evaluation and reporting.",
            }
        ]

    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    current_field: str | None = None

    def commit_current() -> None:
        nonlocal current
        if current.get("file") and current.get("title"):
            entries.append(
                {
                    "title": current.get("title", ""),
                    "file": current.get("file", ""),
                    "caption": current.get("caption", ""),
                    "short_explanation": current.get("short_explanation", ""),
                }
            )
        current = {}

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line == "---" or line.startswith("# Architecture Assets") or line.startswith("This file describes"):
            continue
        if line.startswith("# Diagram "):
            commit_current()
            current = {}
            current_field = None
            continue
        if line in {"File", "Title", "Caption", "Short explanation"}:
            current_field = line.lower().replace(" ", "_")
            continue
        if line.startswith("Flow") or line.startswith("---") or line.startswith("---") or line.startswith("----") or line.startswith("↓"):
            continue
        if current_field == "file" and line.endswith(".png"):
            current["file"] = line
            continue
        if current_field == "title":
            current["title"] = line
            continue
        if current_field == "caption":
            current["caption"] = line
            continue
        if current_field == "short_explanation":
            current["short_explanation"] = line
            continue

    commit_current()
    return entries


def _section_header(title: str, subtitle: str | None = None) -> None:
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def _highlight_box(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="section-card" style="border-left:5px solid #1d4ed8; background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);">
            <div class="kpi-title">{title}</div>
            <div class="muted-note" style="margin-top:.35rem; line-height:1.55;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _card(title: str, body: str, footer: str | None = None, accent: str = "#1d4ed8") -> str:
    footer_html = f'<div class="muted-note" style="margin-top:.6rem;">{footer}</div>' if footer else ""
    return (
        f'<div class="section-card" style="height:100%; border-top:4px solid {accent};">'
        f'<div class="kpi-title">{title}</div>'
        f'<div style="margin-top:.45rem; line-height:1.55; color:#182233;">{body}</div>'
        f"{footer_html}"
        f'</div>'
    )


def _render_card_grid(cards: Sequence[tuple[str, str, str | None, str]], columns: int = 3) -> None:
    rows = [cards[index : index + columns] for index in range(0, len(cards), columns)]
    for row in rows:
        cols = st.columns(len(row))
        for column, card in zip(cols, row):
            title, body, footer, accent = card
            with column:
                st.markdown(_card(title, body, footer, accent), unsafe_allow_html=True)


def _workflow_diagram(steps: list[str]) -> None:
    html = ["<div class='section-card' style='padding:1rem 1.05rem;'>", "<div class='workflow'>"]
    for idx, step in enumerate(steps):
        html.append(f"<span class='step'>{step}</span>")
        if idx < len(steps) - 1:
            html.append("<span class='arrow'>→</span>")
    html.append("</div></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _comparison_table(headers: list[str], rows: list[list[str]]) -> None:
    table_html = ["<div class='home-guide-wrap'><table class='home-table'><thead><tr>"]
    for header in headers:
        table_html.append(f"<th>{header}</th>")
    table_html.append("</tr></thead><tbody>")
    for row in rows:
        table_html.append("<tr>")
        for cell in row:
            table_html.append(f"<td>{cell}</td>")
        table_html.append("</tr>")
    table_html.append("</tbody></table></div>")
    st.markdown("".join(table_html), unsafe_allow_html=True)


def _hardware_specs() -> dict[str, str]:
    specs = {
        "Host Machine": platform.node() or "Requires manual input",
        "CPU": platform.processor() or platform.machine() or "Requires manual input",
        "RAM": "Requires manual input",
        "GPU": "Requires manual input",
        "Operating System": platform.platform(),
        "Python Version": sys.version.split()[0],
    }
    try:
        if sys.platform == "darwin":
            raw_ram = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
            if raw_ram.isdigit():
                gb = int(raw_ram) / (1024 ** 3)
                specs["RAM"] = f"{gb:.0f} GB"
            gpu_info = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True, stderr=subprocess.DEVNULL, timeout=5)
            gpu_line = next((line.strip() for line in gpu_info.splitlines() if "Chipset Model" in line or "Model" in line), "")
            if gpu_line:
                specs["GPU"] = gpu_line.split(":", 1)[-1].strip()
    except Exception:
        pass
    return specs


def _results_summary() -> pd.DataFrame:
    results = load_final_results()
    if results.empty:
        return pd.DataFrame()
    metrics = [
        metric
        for metric in [
            "accuracy",
            "faithfulness",
            "context_precision",
            "context_recall",
            "confidence",
            "response_time",
            "hallucinated",
            "ragas_faithfulness",
            "ragas_answer_correctness",
            "ragas_context_precision",
            "ragas_context_recall",
            "consistency_score",
        ]
        if metric in results.columns
    ]
    summary = results.groupby("system", as_index=False)[metrics].mean(numeric_only=True)
    return summary


def _best_system_label(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "Requires manual input"
    metric_candidates = [column for column in ["accuracy", "faithfulness", "context_precision", "context_recall"] if column in frame.columns]
    if not metric_candidates:
        return str(frame.iloc[0].get("system", "Requires manual input"))
    score = frame.copy()
    score["research_score"] = score[metric_candidates].mean(axis=1)
    return str(score.sort_values("research_score", ascending=False).iloc[0].get("system", "Requires manual input"))


VIEW_ORDER = [
    "project_overview",
    "architecture",
    "research_methodology",
    "experimental_setup",
    "compared_systems",
    "evaluation_metrics",
    "technology_stack",
    "experimental_results",
    "comparative_analysis",
    "research_questions",
    "conclusions",
    "home",
    "live_question_answering",
    "three_system_comparison",
    "retrieval_explorer",
    "evidence_verification",
    "consistency_checker",
    "confidence_dashboard",
    "benchmark_browser",
    "evaluation_analytics",
    "error_analysis_explorer",
    "knowledge_base_statistics",
    "system_performance_dashboard",
    "response_timeline",
    "interactive_charts",
    "export_results",
    "source_document_viewer",
]

VIEW_LABELS = {
    "project_overview": "🏠 Project Overview",
    "architecture": "🏗 System Architecture",
    "research_methodology": "📖 Research Methodology",
    "experimental_setup": "⚙ Experimental Setup",
    "compared_systems": "🤖 Compared Systems",
    "evaluation_metrics": "📊 Evaluation Metrics",
    "technology_stack": "🧰 Technology Stack",
    "experimental_results": "📈 Experimental Results",
    "comparative_analysis": "📉 Comparative Analysis",
    "research_questions": "🎯 Research Questions",
    "conclusions": "📄 Conclusions",
    "home": "🏠 Home",
    "live_question_answering": "💬 Live Question Answering",
    "three_system_comparison": "⚖️ Three-System Comparison",
    "retrieval_explorer": "🔍 Retrieval Explorer",
    "evidence_verification": "✔ Evidence Verification",
    "consistency_checker": "🧠 Consistency Checker",
    "confidence_dashboard": "🎯 Confidence Dashboard",
    "benchmark_browser": "🧾 Benchmark Browser",
    "evaluation_analytics": "📈 Evaluation Analytics",
    "error_analysis_explorer": "🔍 Error Analysis Explorer",
    "knowledge_base_statistics": "📚 Knowledge Base Statistics",
    "system_performance_dashboard": "📊 System Performance Dashboard",
    "response_timeline": "⏱ Response Timeline",
    "interactive_charts": "📉 Interactive Charts",
    "export_results": "⬇ Export Results",
    "source_document_viewer": "📄 Source Document Viewer",
}


def _nav_card(icon: str, title: str, description: str, target_key: str) -> None:
    st.markdown(
        f"""
        <div class="section-card" style="min-height:110px;">
            <div style="display:flex; align-items:center; gap:.55rem; margin-bottom:.35rem;">
                <span style="font-size:1.2rem;">{icon}</span>
                <div style="font-weight:700; color:#0f172a;">{title}</div>
            </div>
            <div class="muted-note" style="line-height:1.25;">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(f"Open {title}", key=f"home_nav_{target_key}", use_container_width=True):
        st.session_state["selected_view"] = target_key
        st.rerun()


def render_view(view_key: str) -> None:
    renderer = VIEW_RENDERERS.get(view_key, render_home)
    renderer()


def app_shell(default_view: str = "home") -> None:
    inject_dashboard_css()
    st.set_page_config(page_title="Enterprise AI Evaluation Dashboard", layout="wide")
    if "selected_view" not in st.session_state:
        st.session_state["selected_view"] = default_view if default_view in VIEW_ORDER else "home"

    st.sidebar.title("Navigation")
    labels = [VIEW_LABELS[key] for key in VIEW_ORDER]
    current_label = VIEW_LABELS.get(st.session_state["selected_view"], VIEW_LABELS["home"])
    selected_label = st.sidebar.radio("Go to", labels, index=labels.index(current_label), key="dashboard_view_radio")
    selected_key = VIEW_ORDER[labels.index(selected_label)]
    st.session_state["selected_view"] = selected_key
    render_view(selected_key)


def render_home() -> None:
    st.markdown(
        """
        <style>
        .home-hero { padding: 1.05rem 1.25rem; border-radius: 20px; background: linear-gradient(135deg, #08213f 0%, #1d4ed8 52%, #0f766e 100%); color: #f8fafc; box-shadow: 0 18px 42px rgba(15, 23, 42, 0.18); margin-bottom: .8rem; }
        .home-subtle { color: rgba(248,250,252,.9); }
        .home-compact { margin: 0; line-height: 1.3; }
        .home-badge { display: inline-flex; align-items: center; gap: .35rem; padding: .32rem .72rem; border-radius: 999px; background: rgba(34,197,94,.16); border: 1px solid rgba(34,197,94,.34); color: #f8fafc; font-size: .82rem; font-weight: 700; margin-top: .35rem; }
        .home-section-title { font-size: 1.06rem; font-weight: 800; color: #0f172a; margin-bottom: .35rem; }
        .home-table, .home-step-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: .96rem; }
        .home-table th, .home-step-table th { background: #eff6ff; color: #0f172a; text-align: left; padding: .82rem .95rem; border-bottom: 1px solid #dbeafe; }
        .home-table td, .home-step-table td { padding: .82rem .95rem; vertical-align: top; border-bottom: 1px solid #e2e8f0; line-height: 1.45; }
        .home-table tr:nth-child(even) td, .home-step-table tr:nth-child(even) td { background: #fbfdff; }
        .home-guide-wrap, .home-frame-panel { overflow: hidden; border-radius: 18px; border: 1px solid rgba(191, 219, 254, 0.9); box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06); margin-top: .35rem; background: #ffffff; }
        .home-frame-panel { padding: .95rem .95rem .85rem .95rem; background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%); box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08); }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="home-hero">
            <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;">
                <div style="min-width:0;">
                    <h1 class="home-compact" style="font-size:2.15rem; margin:0 0 .2rem 0;">Enterprise AI Evaluation Dashboard</h1>
                    <p class="home-subtle home-compact" style="font-size:.95rem; margin:0; max-width: 980px;">Design and Evaluation of a Multi-Agent Retrieval-Augmented Generation Framework with Uncertainty Quantification for Enterprise Knowledge Systems</p>
                    <p class="home-subtle home-compact" style="margin-top:.45rem; font-size:.88rem;">MSc Artificial Intelligence • University of Roehampton<br/>Developed by<br/>Syed Safi Ullah</p>
                    <div style="margin-top:.65rem;"><span class="home-badge">🟢 Project Completed</span></div>
                </div>
                <div style="font-size:2rem; line-height:1;">🤖</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpis([("📄 Benchmark Questions", "140", "RAGBench benchmark")])
    with k2:
        render_kpis([("🤖 RAG Architectures", "3", "Single-Agent, Multi-Agent, Multi-Agent + UQ")])
    with k3:
        render_kpis([("💬 Generated Responses", "420", "Three systems × 140 questions")])
    with k4:
        render_kpis([("📊 Evaluation Scores", "1680", "RAGAS metric evaluations")])

    st.markdown(
        """
        <div class="section-card" style="margin-top:.75rem;">
            <div class="kpi-title">Project Overview</div>
            <p class="muted-note" style="margin:.45rem 0 0 0; line-height:1.45;">This dashboard presents the implementation and evaluation of three Retrieval-Augmented Generation (RAG) architectures for enterprise knowledge systems. The proposed framework compares a traditional Single-Agent RAG system, a Multi-Agent RAG system with specialised Retrieval, Verification and Reasoning agents, and a Multi-Agent RAG framework enhanced with Uncertainty Quantification. Performance was evaluated using the RAGBench benchmark, RAGAS metrics, statistical validation and confidence calibration.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Benchmark Dataset")
    bench_left, bench_right = st.columns([1.1, 0.9])
    with bench_left:
        st.markdown(
            """
            <div class="section-card" style="margin-top:.25rem;">
                <div class="kpi-title">Benchmark</div>
                <div style="font-size:1.18rem; font-weight:800; color:#0f172a; margin-top:.2rem;">RAGBench</div>
                <div class="kpi-title" style="margin-top:.65rem;">Selected Subsets</div>
                <div class="muted-note" style="margin-top:.15rem; line-height:1.55;">TechQA<br/>EManual<br/>CUAD<br/>FinQA<br/>ExpertQA</div>
                <div class="kpi-title" style="margin-top:.65rem;">Question Distribution</div>
                <div class="muted-note" style="margin-top:.15rem; line-height:1.55;">TechQA — 40<br/>EManual — 40<br/>CUAD — 20<br/>FinQA — 20<br/>ExpertQA — 20</div>
                <div class="kpi-title" style="margin-top:.65rem;">Sampling Strategy</div>
                <div class="muted-note" style="margin-top:.15rem; line-height:1.55;">Random sampling without replacement<br/>Random Seed = 42<br/>Fixed quota sampling<br/>Total Questions = 140</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with bench_right:
        benchmark_df = pd.DataFrame(
            [("TechQA", 40), ("EManual", 40), ("CUAD", 20), ("FinQA", 20), ("ExpertQA", 20)],
            columns=["Subset", "Questions"],
        )
        donut = px.pie(benchmark_df, names="Subset", values="Questions", hole=0.66, color_discrete_sequence=["#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"])
        donut.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
        donut.update_traces(textinfo="value", textfont_size=16)
        st.plotly_chart(donut, use_container_width=True)
        st.caption("40 · 40 · 20 · 20 · 20")

    _section_header("Benchmark Sampling Strategy", "Fixed-quota sampling used to create the final benchmark evaluation set.")
    st.markdown(
        """
        <div class="section-card" style="margin-top:.25rem;">
            <div class="kpi-title">Workflow</div>
            <div style="margin-top:.5rem; line-height:1.65; color:#182233; font-weight:600; white-space:pre-line;">Complete RAGBench
        ↓
Five Representative Subsets
        ↓
Fixed-Quota Random Sampling
(Random Seed = 42)
        ↓
140 Benchmark Questions
        ↓
420 Generated Responses</div>
            <div class="kpi-title" style="margin-top:.85rem;">Summary</div>
            <div class="muted-note" style="margin-top:.2rem; line-height:1.55;">Source Dataset: RAGBench<br/>Selected Subsets: TechQA, EManual, CUAD, FinQA, ExpertQA<br/>Sampling Method: Fixed-Quota Random Sampling<br/>Random Seed: 42<br/>Final Evaluation Set: 140 Questions</div>
            <div style="margin-top:.85rem; padding:.85rem 1rem; border-left:4px solid #1d4ed8; background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%); border-radius:14px;">
                <div class="kpi-title">Why 140 Questions?</div>
                <div class="muted-note" style="margin-top:.35rem; line-height:1.55;">To ensure a computationally feasible and reproducible evaluation, a balanced sample of 140 benchmark questions was selected from five representative RAGBench subsets using a fixed-quota random sampling strategy (Random Seed = 42). The identical question set was evaluated across all three RAG architectures to ensure a fair and controlled comparison.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Overall Experimental Framework")
    diagrams = load_architecture_manifest()
    first = diagrams[0] if diagrams else None
    image_path = _resolve_architecture_image(first["file"]) if first else None
    st.markdown("<div class='home-frame-panel'>", unsafe_allow_html=True)
    if image_path is None:
        empty_state("Architecture diagram not found.")
    else:
        frame_left, frame_mid, frame_right = st.columns([0.05, 0.90, 0.05])
        with frame_mid:
            st.image(str(image_path), use_container_width=True)
    step_rows = [
        ("Step 1", "Benchmark Selection", "Select five RAGBench subsets using a reproducible quota sampling strategy."),
        ("Step 2", "Knowledge Base Construction", "Parse, clean, chunk and embed enterprise documents before indexing them in ChromaDB."),
        ("Step 3", "Semantic Retrieval", "Retrieve the most relevant document chunks using dense vector similarity search."),
        ("Step 4", "Three RAG Architectures", "Evaluate Single-Agent RAG, Multi-Agent RAG and Multi-Agent RAG + Uncertainty Quantification."),
        ("Step 5", "Benchmark Evaluation", "140 benchmark questions and 420 generated responses are evaluated."),
        ("Step 6", "RAGAS Evaluation", "Measure Faithfulness, Answer Correctness, Context Precision and Context Recall."),
        ("Step 7", "Research Analysis", "Perform statistical analysis, confidence calibration, threshold analysis and error analysis."),
        ("Step 8", "Final Conclusions", "Interpret experimental findings and answer the research questions."),
    ]
    step_html = ["<table class='home-step-table'><thead><tr><th style='width:15%;'>Step</th><th style='width:28%;'>Stage</th><th>Explanation</th></tr></thead><tbody>"]
    for step, stage, explanation in step_rows:
        step_html.append(f"<tr><td><strong>{step}</strong></td><td><strong>{stage}</strong></td><td>{explanation}</td></tr>")
    step_html.append("</tbody></table>")
    st.markdown("".join(step_html), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Dashboard Guide")
    guide_rows = [
        ("🏗️ Architecture", "View system architecture, workflow diagrams and implementation overview."),
        ("💬 Live Question Answering", "Compare responses generated by the three RAG systems for individual benchmark questions."),
        ("⚖️ Three-System Comparison", "Compare overall performance across Single-Agent, Multi-Agent and Multi-Agent + UQ systems."),
        ("🔍 Retrieval Explorer", "Inspect retrieved document chunks and semantic retrieval behaviour."),
        ("✔ Evidence Verification", "Review supporting evidence selected by the Verification Agent."),
        ("🧠 Consistency Checker", "Compare reasoning consistency between generated responses."),
        ("🎯 Confidence Dashboard", "Explore confidence distributions, reliability curves, calibration metrics and threshold analysis."),
        ("🧾 Benchmark Browser", "Browse all 140 benchmark questions and associated benchmark datasets."),
        ("📈 Evaluation Analytics", "Visualise RAGAS metrics, summary statistics and evaluation outputs."),
        ("🔍 Error Analysis Explorer", "Investigate qualitative error patterns, warning cases and failure examples."),
        ("📚 Knowledge Base Statistics", "Display document, chunk, embedding and vector database statistics."),
        ("📊 System Performance Dashboard", "Overall system performance comparison across all architectures."),
        ("⏱ Response Timeline", "Visualise response times and execution behaviour."),
        ("📉 Interactive Charts", "Interactive publication-quality figures and visual analytics."),
        ("⬇ Export Results", "Download evaluation outputs, reports and figures."),
        ("📄 Source Document Viewer", "Browse benchmark source documents used during evaluation."),
    ]
    guide_html = ["<div class='home-guide-wrap'><table class='home-table'><thead><tr><th style='width:33%;'>Dashboard Section</th><th>Purpose</th></tr></thead><tbody>"]
    for section, purpose in guide_rows:
        guide_html.append(f"<tr><td><strong>{section}</strong></td><td>{purpose}</td></tr>")
    guide_html.append("</tbody></table></div>")
    st.markdown("".join(guide_html), unsafe_allow_html=True)
    st.caption("Use the navigation menu on the left sidebar to explore each module.")

    st.markdown(
        """
        <div class="section-card" style="padding:.75rem .95rem; margin-top:.6rem;">
            <div style="display:flex; flex-wrap:wrap; gap:.7rem 1.1rem; justify-content:space-between; align-items:center;">
                <div>
                    <div class="kpi-title">Prepared for</div>
                    <div class="muted-note">MSc Artificial Intelligence<br/>University of Roehampton<br/>2026</div>
                </div>
                <div style="text-align:right;">
                    <div class="kpi-title">Project Status</div>
                    <div class="muted-note">✅ Implementation Completed · ✅ Benchmark Evaluation Completed · ✅ Statistical Validation Completed · ✅ Confidence Calibration Completed</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_architecture() -> None:
    st.subheader("Architecture")
    diagrams = load_architecture_manifest()
    if not diagrams:
        empty_state("Architecture manifest is empty.")
        return

    for idx, item in enumerate(diagrams, start=1):
        title = item.get("title", f"Diagram {idx}")
        explanation = item.get("short_explanation", "")
        caption = item.get("caption", "")
        file_name = item.get("file", "")
        image_path = _resolve_architecture_image(file_name) if file_name else None

        with st.expander(f"Diagram {idx}: {title}", expanded=idx == 1):
            st.markdown(f"**{title}**")
            if image_path is None:
                empty_state(f"Image not found: {file_name}")
            else:
                st.image(str(image_path), width=700)
                with st.expander("Click to enlarge"):
                    st.image(str(image_path), use_container_width=True)
            if explanation:
                st.write(explanation)
            if caption:
                st.caption(caption)


def _question_selector(results: pd.DataFrame, key_prefix: str) -> pd.DataFrame:
    unique = unique_questions(results)
    if unique.empty:
        empty_state("No benchmark questions are available.")
        return pd.DataFrame()
    question_col = "question" if "question" in unique.columns else "Question"
    search = st.text_input("Search questions", key=f"{key_prefix}_search", placeholder="Type a question fragment to filter the benchmark browser")
    if search.strip():
        best = pick_best_question(results, search)
        filtered = unique[unique[question_col].str.contains(search, case=False, na=False)]
        if filtered.empty:
            filtered = unique[unique[question_col].eq(best[question_col])]
    else:
        filtered = unique
    if filtered.empty:
        empty_state("No benchmark questions match the current search.")
        return pd.DataFrame()
    labels = [f"Q{idx + 1:03d} · {row.dataset}" for idx, row in enumerate(filtered.itertuples(index=False))]
    chosen = st.selectbox("Benchmark question", labels, key=f"{key_prefix}_question")
    chosen_index = labels.index(chosen)
    chosen_question = str(filtered.iloc[chosen_index][question_col])
    chosen_dataset = str(filtered.iloc[chosen_index]["dataset"])
    source_question_col = "question" if "question" in results.columns else "Question"
    return results[
        (results[source_question_col].astype(str) == chosen_question)
        & (results["dataset"].astype(str) == chosen_dataset)
    ].copy()


def _system_ordered_summary(results: pd.DataFrame, metric: str, systems: list[str]) -> pd.DataFrame:
    if results.empty or metric not in results.columns:
        return pd.DataFrame({"system": systems, metric: [0.0] * len(systems)})
    summary = results.groupby("system", as_index=False)[metric].mean(numeric_only=True)
    summary[metric] = pd.to_numeric(summary[metric], errors="coerce")
    summary = summary.set_index("system").reindex(systems).reset_index()
    summary[metric] = summary[metric].fillna(0.0)
    return summary


def render_live_question_answering() -> None:
    results = load_final_results()
    st.subheader("Live Question Answering")
    st.caption("Search the benchmark and compare the three systems on the selected question.")
    selected = _question_selector(results, "live")
    if selected.empty:
        return
    question = selected.iloc[0]["question"]
    st.markdown(f"**Question**: {question}")
    for system in ["Single-Agent RAG", "Multi-Agent RAG", "Multi-Agent RAG + UQ"]:
        row = selected[selected["system"] == system].head(1)
        if row.empty:
            continue
        row = row.iloc[0]
        with st.expander(system, expanded=system == "Multi-Agent RAG + UQ"):
            cols = st.columns(3)
            cols[0].metric("Confidence", format_percentage(row.get("confidence")))
            cols[1].metric("Decision", str(row.get("decision", "Requires manual input.")))
            cols[2].metric("Latency", f"{float(row.get('response_time', 0.0)):.2f}s")
            st.write("**Answer**")
            st.write(row.get("answer", "Requires manual input."))
            st.write("**Retrieved context**")
            st.write(row.get("retrieved_context", row.get("sources", "Requires manual input.")))


def render_three_system_comparison() -> None:
    results = load_final_results()
    st.subheader("Three-System Comparison")
    selected_metric = st.selectbox(
        "Metric",
        [
            "ragas_answer_correctness",
            "ragas_faithfulness",
            "ragas_context_precision",
            "ragas_context_recall",
            "response_time",
            "confidence",
        ],
        key="comparison_metric",
    )
    systems = ["Single-Agent RAG", "Multi-Agent RAG", "Multi-Agent RAG + UQ"]
    summary = _system_ordered_summary(results, selected_metric, systems)
    st.plotly_chart(bar_chart(summary, x="system", y=selected_metric, title=f"Average {selected_metric.replace('_', ' ').title()} by system"), use_container_width=True)
    st.dataframe(summary, use_container_width=True, hide_index=True)
    comparison = load_phase3_comparison()
    if not comparison.empty:
        dataframe_frame(comparison)


def render_compared_systems() -> None:
    st.subheader("Compared Systems")
    _render_card_grid(
        [
            (
                "Single-Agent RAG",
                "<strong>Role:</strong> Baseline<br/><strong>Pipeline:</strong> Query → Retriever → LLM → Answer<br/><strong>Characteristics:</strong> Single reasoning step, simple architecture, fast, lower computational cost.",
                "Baseline architecture for comparison.",
                "#1d4ed8",
            ),
            (
                "Multi-Agent RAG",
                "<strong>Role:</strong> Proposed architecture<br/><strong>Pipeline:</strong> Planner → Retriever → Generator → Reviewer → Answer<br/><strong>Characteristics:</strong> Task decomposition, collaborative reasoning, improved retrieval quality, higher accuracy.",
                "Introduces specialised agents to improve reasoning.",
                "#0f766e",
            ),
            (
                "Multi-Agent + Uncertainty Quantification",
                "<strong>Role:</strong> Proposed architecture + confidence estimation<br/><strong>Pipeline:</strong> Planner → Retriever → Generator → Reviewer → Uncertainty Module → Confidence Score → Final Answer<br/><strong>Characteristics:</strong> Confidence estimation, hallucination mitigation, reliable responses, supports abstention, highest research contribution.",
                "Adds calibrated confidence and abstention.",
                "#7c3aed",
            ),
        ],
        columns=3,
    )

    _section_header("Agent Responsibilities", "How each architecture distributes planning, retrieval, generation, verification and confidence estimation.")

    def _responsibility_table(rows: list[tuple[str, str]]) -> str:
        table_rows = ["<table class='home-table'><thead><tr><th style='width:34%;'>Agent</th><th>Responsibility</th></tr></thead><tbody>"]
        for agent, responsibility in rows:
            table_rows.append(f"<tr><td><strong>{agent}</strong></td><td>{responsibility}</td></tr>")
        table_rows.append("</tbody></table>")
        return "".join(table_rows)

    _render_card_grid(
        [
            (
                "Single-Agent RAG",
                _responsibility_table(
                    [
                        ("LLM Agent", "• Retrieves relevant context from the vector database.<br/>• Performs reasoning over the retrieved evidence.<br/>• Generates the final response in a single reasoning step."),
                    ]
                ),
                "Single-model pipeline",
                "#1d4ed8",
            ),
            (
                "Multi-Agent RAG",
                _responsibility_table(
                    [
                        ("Planner Agent", "• Analyses the user query.<br/>• Plans the reasoning workflow."),
                        ("Retriever Agent", "• Retrieves the most relevant document chunks."),
                        ("Generator Agent", "• Generates the answer using retrieved evidence."),
                        ("Reviewer Agent", "• Checks factual consistency.<br/>• Verifies completeness.<br/>• Reduces hallucinations before returning the answer."),
                    ]
                ),
                "Specialised reasoning roles",
                "#0f766e",
            ),
            (
                "Multi-Agent RAG + UQ",
                _responsibility_table(
                    [
                        ("Planner Agent", "• Plans the reasoning workflow."),
                        ("Retriever Agent", "• Retrieves semantically relevant evidence."),
                        ("Generator Agent", "• Produces the candidate answer."),
                        ("Reviewer Agent", "• Validates factual grounding.<br/>• Reviews coherence and consistency."),
                        ("Uncertainty Agent", "• Estimates confidence.<br/>• Performs confidence calibration.<br/>• Applies the abstention threshold.<br/>• Determines whether the response should be returned or withheld."),
                    ]
                ),
                "Confidence-aware decision making",
                "#7c3aed",
            ),
        ],
        columns=3,
    )

    _highlight_box(
        "Why Multiple Agents?",
        "Instead of relying on a single model to perform every stage of Retrieval-Augmented Generation, specialised agents divide the workflow into planning, retrieval, answer generation, verification and confidence estimation. This modular architecture improves reasoning quality, increases response reliability and enables uncertainty-aware decision making while maintaining a fair comparison with the Single-Agent baseline.",
    )


def render_retrieval_explorer() -> None:
    results = load_final_results()
    st.subheader("Retrieval Explorer")
    selected = _question_selector(results, "retrieval")
    if selected.empty:
        return
    row = selected.iloc[0]
    st.write(f"**Selected question**: {row.get('question', 'Requires manual input.')}")
    st.write(f"**Retrieved context**: {row.get('retrieved_context', row.get('sources', 'Requires manual input.'))}")
    source_counts = Counter(str(value).split("; ")[0] for value in selected.get("sources", pd.Series(dtype=str)).dropna())
    if source_counts:
        source_frame = pd.DataFrame({"source": list(source_counts.keys()), "count": list(source_counts.values())})
        st.plotly_chart(bar_chart(source_frame, x="source", y="count", title="Retrieved source frequency"), use_container_width=True)


def render_evidence_verification() -> None:
    results = load_final_results()
    st.subheader("Evidence Verification")
    selected = _question_selector(results, "verification")
    if selected.empty:
        return
    row = selected.iloc[0]
    cols = st.columns(4)
    cols[0].metric("Faithfulness", format_percentage(row.get("faithfulness")))
    cols[1].metric("RAGAS faithfulness", format_percentage(row.get("ragas_faithfulness")))
    cols[2].metric("Hallucinated", str(bool(row.get("hallucinated"))))
    cols[3].metric("Ground truth match", format_percentage(row.get("ragas_answer_correctness")))
    st.write("**Generated answer**")
    st.write(row.get("answer", "Requires manual input."))
    st.write("**Ground truth**")
    st.write(row.get("ground_truth", row.get("Ground Truth", "Requires manual input.")))


def render_consistency_checker() -> None:
    results = load_final_results()
    st.subheader("Consistency Checker")
    selected = _question_selector(results, "consistency")
    if selected.empty:
        return
    metrics = selected[["system", "consistency_score"]].copy()
    st.plotly_chart(bar_chart(metrics, x="system", y="consistency_score", title="Consistency score by system"), use_container_width=True)
    st.write("**Answer text comparison**")
    for row in selected.itertuples(index=False):
        st.markdown(f"- **{row.system}**: {getattr(row, 'answer', 'Requires manual input.')}")


def render_confidence_dashboard() -> None:
    results = load_final_results()
    st.subheader("Confidence Dashboard")
    report = load_phase5_report()
    bins = load_phase5_bins()
    metrics = load_phase5_metrics()
    systems = ["Single-Agent RAG", "Multi-Agent RAG", "Multi-Agent RAG + UQ"]
    selected_metric = st.selectbox(
        "Confidence view",
        [
            "confidence",
            "ragas_answer_correctness",
            "ragas_faithfulness",
            "ragas_context_precision",
            "ragas_context_recall",
        ],
        index=1,
        key="confidence_metric",
    )
    confidence_summary = _system_ordered_summary(results, selected_metric, systems)
    st.plotly_chart(bar_chart(confidence_summary, x="system", y=selected_metric, title=f"Average {selected_metric.replace('_', ' ').title()} by system"), use_container_width=True)
    if {"confidence", "ragas_answer_correctness"}.issubset(results.columns):
        scatter_data = results[["system", "confidence", "ragas_answer_correctness"]].dropna()
        if not scatter_data.empty:
            st.plotly_chart(scatter_chart(scatter_data, x="confidence", y="ragas_answer_correctness", color="system", title="Confidence versus RAGAS answer correctness"), use_container_width=True)
    if not report.empty:
        st.markdown("**Calibration report**")
        dataframe_frame(report)
    if not metrics.empty:
        st.markdown("**Calibration metrics**")
        dataframe_frame(metrics)
    if not bins.empty:
        st.markdown("**Calibration bins**")
        dataframe_frame(bins)
        if {"bin", "mean_target"}.issubset(bins.columns):
            st.plotly_chart(bar_chart(bins, x="bin", y="mean_target", color="system", title="Mean target by confidence bin"), use_container_width=True)


def render_benchmark_browser() -> None:
    results = load_final_results()
    st.subheader("Benchmark Browser (140 questions)")
    frame = unique_questions(results)
    if frame.empty:
        empty_state("Benchmark data is not available.")
        return
    dataset = st.selectbox("Dataset", ["All"] + sorted(frame["dataset"].dropna().unique().tolist()), key="benchmark_dataset")
    filtered = frame if dataset == "All" else frame[frame["dataset"] == dataset]
    search = st.text_input("Search text", key="benchmark_search")
    if search.strip():
        filtered = filtered[filtered["question"].str.contains(search, case=False, na=False)]
    if filtered.empty:
        empty_state("No benchmark questions match the current filters.")
        return
    dataframe_frame(filtered)


def render_evaluation_analytics() -> None:
    results = load_final_results()
    st.subheader("Evaluation Analytics")
    tabs = st.tabs(["System summary", "Dataset summary", "Thresholds"])
    with tabs[0]:
        system_summary = load_summary_by_system()
        if system_summary.empty:
            empty_state("System summary data is unavailable.")
        else:
            dataframe_frame(system_summary)
            metric = next((column for column in ["answer_correctness_mean", "accuracy_mean", "faithfulness_mean"] if column in system_summary.columns), None)
            if metric:
                st.plotly_chart(bar_chart(system_summary, x="system", y=metric, title=f"{metric.replace('_', ' ').title()} by system"), use_container_width=True)
        phase3_summary = load_phase3_summary()
        if not phase3_summary.empty:
            st.caption("Phase 3 summary reference")
            dataframe_frame(phase3_summary)
    with tabs[1]:
        dataset_summary = load_summary_by_dataset()
        if dataset_summary.empty:
            empty_state("Dataset summary data is unavailable.")
        else:
            dataframe_frame(dataset_summary)
            if "dataset" in dataset_summary.columns:
                numeric = [column for column in dataset_summary.columns if column.endswith("mean")][:4]
                if numeric:
                    melted = dataset_summary.melt(id_vars=["dataset"], value_vars=numeric, var_name="metric", value_name="value")
                    st.plotly_chart(bar_chart(melted, x="dataset", y="value", color="metric", title="Dataset-level means"), use_container_width=True)
    with tabs[2]:
        threshold = load_phase3_threshold()
        if threshold.empty:
            empty_state("Threshold analysis data is unavailable.")
        else:
            dataframe_frame(threshold)
            st.plotly_chart(line_chart(threshold, x="answer_threshold", y="answered_accuracy", title="Answered accuracy by answer threshold"), use_container_width=True)


def render_error_analysis_explorer() -> None:
    st.subheader("Error Analysis Explorer")
    cases = load_error_cases()
    if cases.empty:
        text = load_error_analysis_text()
        if text:
            st.markdown(text)
        else:
            st.text("Requires manual input.")
        return
    st.markdown(load_error_analysis_text())
    dataframe_frame(cases)


def render_knowledge_base_statistics() -> None:
    results = load_final_results()
    st.subheader("Knowledge Base Statistics")
    source_series = results.get("sources", pd.Series(dtype=str)).dropna().astype(str)
    source_counter: Counter[str] = Counter()
    for item in source_series:
        for source in item.split("; "):
            source_counter[source.split(":")[0]] += 1
    source_frame = pd.DataFrame({"source": list(source_counter.keys()), "count": list(source_counter.values())})
    cols = st.columns(3)
    cols[0].metric("Documents", str(len(load_source_documents())))
    cols[1].metric("Unique sources in evaluation", str(len(source_counter)))
    cols[2].metric("Unique benchmark questions", str(len(unique_questions(results))))
    if not source_frame.empty:
        st.plotly_chart(bar_chart(source_frame.sort_values("count", ascending=False).head(15), x="source", y="count", title="Top sources referenced by the final evaluation"), use_container_width=True)


def render_system_performance_dashboard() -> None:
    results = load_final_results()
    st.subheader("System Performance Dashboard")
    systems = ["Single-Agent RAG", "Multi-Agent RAG", "Multi-Agent RAG + UQ"]
    metrics = results.groupby("system", as_index=False)[["ragas_answer_correctness", "ragas_faithfulness", "ragas_context_precision", "ragas_context_recall", "response_time"]].mean(numeric_only=True)
    metrics = metrics.set_index("system").reindex(systems).reset_index().fillna(0.0)
    st.plotly_chart(bar_chart(metrics, x="system", y="ragas_answer_correctness", title="Mean RAGAS answer correctness by system"), use_container_width=True)
    st.plotly_chart(bar_chart(metrics, x="system", y="ragas_faithfulness", title="Mean RAGAS faithfulness by system"), use_container_width=True)
    st.plotly_chart(bar_chart(metrics, x="system", y="ragas_context_precision", title="Mean context precision by system"), use_container_width=True)
    st.plotly_chart(bar_chart(metrics, x="system", y="ragas_context_recall", title="Mean context recall by system"), use_container_width=True)
    st.plotly_chart(bar_chart(metrics, x="system", y="response_time", title="Mean response time by system"), use_container_width=True)
    dataframe_frame(metrics)


def render_response_timeline() -> None:
    results = load_final_results()
    st.subheader("Response Timeline")
    if "question_id" not in results.columns:
        empty_state("No question timeline available.")
        return
    timeline = pd.DataFrame(results.groupby(["question_id", "system"], as_index=False)["response_time"].mean())
    st.plotly_chart(line_chart(timeline, x="question_id", y="response_time", color="system", title="Average response time across questions"), use_container_width=True)


def render_interactive_charts() -> None:
    results = load_final_results()
    st.subheader("Interactive Charts")
    chart_type = st.selectbox("Chart type", ["Histogram", "Scatter", "Bar"], key="chart_type")
    columns = [column for column in ["accuracy", "faithfulness", "context_precision", "context_recall", "confidence", "response_time", "retrieval_score", "verification_score", "consistency_score"] if column in results.columns]
    if chart_type == "Histogram":
        column = st.selectbox("Column", columns, key="hist_column")
        st.plotly_chart(hist_chart(results, x=column, color="system", title=f"Distribution of {column}"), use_container_width=True)
    elif chart_type == "Scatter":
        x = st.selectbox("X axis", columns, index=columns.index("confidence") if "confidence" in columns else 0, key="scatter_x")
        y = st.selectbox("Y axis", columns, index=columns.index("accuracy") if "accuracy" in columns else 0, key="scatter_y")
        st.plotly_chart(scatter_chart(results, x=x, y=y, color="system", title=f"{x} vs {y}"), use_container_width=True)
    else:
        metric = st.selectbox("Metric", columns, key="bar_metric")
        summary = pd.DataFrame(results.groupby("system", as_index=False)[metric].mean())
        st.plotly_chart(bar_chart(summary, x="system", y=metric, title=f"Mean {metric} by system"), use_container_width=True)


def render_export_results() -> None:
    results = load_final_results()
    st.subheader("Export Results")
    selected_system = st.selectbox("System", ["All"] + sorted(results["system"].dropna().unique().tolist()), key="export_system")
    export_frame = results if selected_system == "All" else results[results["system"] == selected_system]
    st.dataframe(export_frame.head(20), use_container_width=True, hide_index=True)
    download_button("Download CSV", export_frame, "evaluation_export.csv", key="download_csv")
    download_button("Download benchmark browser export", unique_questions(results), "benchmark_browser_export.csv", key="download_browser_csv")


def render_source_document_viewer() -> None:
    st.subheader("Source Document Viewer")
    documents = load_source_documents()
    if documents.empty:
        empty_state("No source documents were found.")
        return
    chosen = st.selectbox("Document", documents["path"].astype(str).tolist(), key="source_document")
    preview = load_document_text(chosen)
    st.write(Path(chosen).name)
    st.text_area("Document preview", preview[:12000], height=500)


def render_home_overview() -> None:
    results = load_final_results()
    st.subheader("Overview")
    if results.empty:
        empty_state("Final evaluation data is unavailable.")
        return
    overview = results.groupby("system", as_index=False)[["accuracy", "faithfulness", "confidence", "response_time"]].mean()
    st.plotly_chart(bar_chart(overview, x="system", y="accuracy", title="Average accuracy by system"), use_container_width=True)
    st.plotly_chart(bar_chart(overview, x="system", y="response_time", title="Average response time by system"), use_container_width=True)


def render_project_overview() -> None:
    st.subheader("Project Overview")
    render_hero(
        "Project Overview",
        "Design and Evaluation of a Multi-Agent Retrieval-Augmented Generation Framework with Uncertainty Quantification for Enterprise Knowledge Systems",
        tags=["MSc Artificial Intelligence", "RAGBench", "RAGAS", "Multi-Agent RAG", "Uncertainty Quantification"],
    )
    render_kpis(
        [
            ("📚 Dataset", f"RAGBench ({load_benchmark_question_count()} queries)", "Five fixed-quota subsets"),
            ("🤖 Compared Systems", "3", "Single-Agent, Multi-Agent, Multi-Agent + UQ"),
            ("📊 Evaluation Metrics", "4 + calibration", "Faithfulness, Answer Relevancy, Context Precision, Context Recall"),
            ("🧾 Number of Queries", "140", "Reproducible benchmark set"),
            ("🎯 Research Questions", "4", "Performance, threshold trade-offs, calibration, error patterns"),
            ("⚙ Evaluation Framework", "RAGAS", "Quantitative + qualitative evaluation"),
        ]
    )
    _section_header("Benchmark Sampling Strategy", "Fixed-quota sampling used to create the final benchmark evaluation set.")
    st.markdown(
        """
        <div class="section-card" style="margin-top:.25rem;">
            <div class="kpi-title">Workflow</div>
            <div style="margin-top:.5rem; line-height:1.65; color:#182233; font-weight:600; white-space:pre-line;">Complete RAGBench
        ↓
Five Representative Subsets
        ↓
Fixed-Quota Random Sampling
(Random Seed = 42)
        ↓
140 Benchmark Questions
        ↓
420 Generated Responses</div>
            <div class="kpi-title" style="margin-top:.85rem;">Summary</div>
            <div class="muted-note" style="margin-top:.2rem; line-height:1.55;">Source Dataset: RAGBench<br/>Selected Subsets: TechQA, EManual, CUAD, FinQA, ExpertQA<br/>Sampling Method: Fixed-Quota Random Sampling<br/>Random Seed: 42<br/>Final Evaluation Set: 140 Questions</div>
            <div style="margin-top:.85rem; padding:.85rem 1rem; border-left:4px solid #1d4ed8; background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%); border-radius:14px;">
                <div class="kpi-title">Why 140 Questions?</div>
                <div class="muted-note" style="margin-top:.35rem; line-height:1.55;">To ensure a computationally feasible and reproducible evaluation, a balanced sample of 140 benchmark questions was selected from five representative RAGBench subsets using a fixed-quota random sampling strategy (Random Seed = 42). The identical question set was evaluated across all three RAG architectures to ensure a fair and controlled comparison.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="section-card" style="margin-top:.8rem; overflow-x:auto;">
            <div class="kpi-title">Workflow Table</div>
            <table style="width:100%; border-collapse:collapse; margin-top:.6rem; font-size:.95rem;">
                <thead>
                    <tr style="text-align:left; border-bottom:1px solid rgba(148,163,184,.35);">
                        <th style="padding:.55rem .4rem;">Stage</th>
                        <th style="padding:.55rem .4rem;">What happens</th>
                        <th style="padding:.55rem .4rem;">Output</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom:1px solid rgba(148,163,184,.18);">
                        <td style="padding:.55rem .4rem; font-weight:600;">1. Dataset selection</td>
                        <td style="padding:.55rem .4rem;">Five RAGBench subsets are sampled using a fixed quota and random seed.</td>
                        <td style="padding:.55rem .4rem;">Balanced benchmark set</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,.18);">
                        <td style="padding:.55rem .4rem; font-weight:600;">2. Knowledge base</td>
                        <td style="padding:.55rem .4rem;">Documents are chunked, embedded and stored in the vector database.</td>
                        <td style="padding:.55rem .4rem;">Queryable ChromaDB store</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,.18);">
                        <td style="padding:.55rem .4rem; font-weight:600;">3. Answer generation</td>
                        <td style="padding:.55rem .4rem;">Single-Agent, Multi-Agent and Multi-Agent + UQ produce answers from the same questions.</td>
                        <td style="padding:.55rem .4rem;">Three comparable outputs</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(148,163,184,.18);">
                        <td style="padding:.55rem .4rem; font-weight:600;">4. Evaluation</td>
                        <td style="padding:.55rem .4rem;">RAGAS metrics, calibration and qualitative review assess answer quality.</td>
                        <td style="padding:.55rem .4rem;">Metrics and analysis files</td>
                    </tr>
                    <tr>
                        <td style="padding:.55rem .4rem; font-weight:600;">5. Reporting</td>
                        <td style="padding:.55rem .4rem;">Final results are summarized in the dashboard, figures and error analysis.</td>
                        <td style="padding:.55rem .4rem;">Research-ready report</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _highlight_box(
        "Research Objective",
        "Determine whether multi-agent reasoning and explicit uncertainty quantification improve Retrieval-Augmented Generation for enterprise knowledge systems, and whether those improvements remain consistent across accuracy, faithfulness, calibration and latency.",
    )


def render_research_methodology() -> None:
    st.subheader("Research Methodology")
    _render_card_grid(
        [
            ("Research Design", "Comparative Experimental Study", "Tests three architectures under the same benchmark conditions.", "#1d4ed8"),
            ("Research Goal", "Evaluate whether Multi-Agent reasoning and Uncertainty Quantification improve Retrieval-Augmented Generation.", "Focused on quality, reliability and calibration.", "#0f766e"),
            ("Independent Variable", "RAG Architecture: Single-Agent, Multi-Agent, Multi-Agent + UQ.", "Architecture is the only intentionally changed factor.", "#2563eb"),
            ("Dependent Variables", "Faithfulness, Answer Relevancy, Context Precision, Context Recall, Latency, Confidence.", "These are the observed outputs across systems.", "#7c3aed"),
        ],
        columns=2,
    )
    _section_header("Evaluation Procedure", "The same dataset, retrieval path and evaluation methodology are used for every architecture.")
    _workflow_diagram(["Dataset", "Knowledge Base", "Three RAG Systems", "RAGAS Evaluation", "Performance Comparison", "Dashboard"])
    _section_header("Research Questions", "The repository preserves the evidence themes rather than a verbatim dissertation wording.")
    _render_card_grid(
        [
            ("RQ1", "Does the proposed multi-agent approach improve overall system performance compared with the baseline?", "Supported by the final system comparison tables and summary statistics.", "#1d4ed8"),
            ("RQ2", "What threshold and coverage trade-off best balances accuracy against abstention?", "Supported by the threshold analysis outputs.", "#0f766e"),
            ("RQ3", "Are the confidence scores well calibrated?", "Supported by calibration reports, bins and reliability curves.", "#2563eb"),
            ("RQ4", "What qualitative error patterns and limitations remain?", "Supported by the error analysis chapter and supporting notes.", "#7c3aed"),
        ],
        columns=2,
    )


def render_system_architecture() -> None:
    st.subheader("System Architecture")
    _section_header("Overall Pipeline", "From RAGBench sampling to evaluation and reporting.")
    _workflow_diagram([
        "RAGBench Dataset",
        "Knowledge Base Construction",
        "Embedding Generation",
        "Vector Database",
        "Semantic Retrieval",
        "Single-Agent",
        "Multi-Agent",
        "Multi-Agent + UQ",
        "Evaluation Engine",
        "Results Dashboard",
    ])
    diagrams = load_architecture_manifest()
    if diagrams:
        first = diagrams[0]
        image_path = _resolve_architecture_image(first.get("file", ""))
        if image_path is not None:
            st.markdown("<div class='home-frame-panel'>", unsafe_allow_html=True)
            st.image(str(image_path), use_container_width=True)
            st.caption(first.get("caption", ""))
            st.markdown("</div>", unsafe_allow_html=True)
    _section_header("Components and Purpose", "Each component plays a defined role in the research pipeline.")
    _render_card_grid(
        [
            ("Dataset", "RAGBench benchmark set used as the evaluation corpus.", "Ensures a reproducible academic benchmark.", "#1d4ed8"),
            ("Chunking", f"Chunk size {CHUNK_SIZE} with overlap {CHUNK_OVERLAP}.", "Preserves context while keeping retrieval units compact.", "#0f766e"),
            ("Embedding Model", EMBEDDING_MODEL, "Produces dense vector representations for semantic search.", "#2563eb"),
            ("Retriever", f"Top-k retrieval with k={TOP_K}.", "Selects the most relevant evidence for answering.", "#7c3aed"),
            ("Vector Database", f"ChromaDB collection: {COLLECTION_NAME}.", "Stores embeddings for fast semantic retrieval.", "#0ea5e9"),
            ("LLM", OLLAMA_MODEL, "Generates answers from retrieved context.", "#059669"),
            ("Agent Layer", "Single-Agent, Multi-Agent, Multi-Agent + UQ.", "Enables comparative reasoning strategies.", "#b45309"),
            ("Uncertainty Module", "Confidence estimation and abstention logic.", "Improves reliability and reduces hallucination risk.", "#7c3aed"),
            ("Evaluation", "RAGAS metrics, calibration analysis and qualitative review.", "Measures answer quality and reliability.", "#1d4ed8"),
            ("Dashboard", "Streamlit + Plotly research dashboard.", "Communicates the study to examiners and researchers.", "#dc2626"),
        ],
        columns=2,
    )


def render_experimental_setup() -> None:
    st.subheader("Experimental Setup")
    _section_header("Dataset", "Research dataset configuration and selection rationale.")
    _render_card_grid(
        [
            ("Dataset Name", "RAGBench fixed-quota benchmark set.", "Used because it provides a reproducible research benchmark.", "#1d4ed8"),
            ("Purpose", "Evaluate retrieval, generation and confidence behaviour across three architectures.", "Targets enterprise knowledge answering.", "#0f766e"),
            ("Why Selected", "Broad coverage of enterprise-style question types.", "Matches the dissertation objective and evaluation scope.", "#2563eb"),
        ],
        columns=3,
    )
    _section_header("Model Configuration", "Automatically loaded from the project configuration where available.")
    _render_card_grid(
        [
            ("Embedding Model", EMBEDDING_MODEL, "Creates semantic embeddings for retrieval.", "#1d4ed8"),
            ("LLM", OLLAMA_MODEL, "Local generation model used in evaluation.", "#0f766e"),
            ("Vector Database", "ChromaDB persistent vector store", "Persists dense vectors for semantic retrieval.", "#2563eb"),
            ("Retriever", f"Top-k = {TOP_K}", "Controls the number of retrieved evidence chunks.", "#7c3aed"),
            ("Framework", "Streamlit + Python", "Dashboard and evaluation workflow runtime.", "#0ea5e9"),
            ("Visualization Library", "Plotly", "Interactive presentation-quality charts.", "#059669"),
        ],
        columns=3,
    )
    _section_header("Retrieval Configuration", "Current values are pulled from config.py.")
    _comparison_table(
        ["Parameter", "Value", "Note"],
        [
            ["Chunk Size", str(CHUNK_SIZE), "Source: config.py"],
            ["Chunk Overlap", str(CHUNK_OVERLAP), "Source: config.py"],
            ["Top-k", str(TOP_K), "Source: config.py"],
            ["Embedding Dimensions", "Requires manual input", "Update this if the embedding backend changes."],
            ["Retriever Type", "Dense semantic retriever", "Matches the current RAG pipeline."],
        ],
    )
    _section_header("Hardware Configuration", "Detected automatically where possible.")
    hardware = _hardware_specs()
    _comparison_table(["Component", "Value"], [[key, value] for key, value in hardware.items()])
    _section_header("Evaluation Configuration", "Experimental design used across all systems.")
    _comparison_table(
        ["Setting", "Value"],
        [
            ["Compared Systems", "Single-Agent RAG, Multi-Agent RAG, Multi-Agent + UQ"],
            ["Evaluation Framework", "RAGAS + calibration + qualitative review"],
            ["Number of Queries", "140 benchmark questions"],
            ["Evaluation Metrics", "Faithfulness, Answer Relevancy, Context Precision, Context Recall"],
            ["Confidence Estimation", "Confidence scores with thresholding"],
            ["Abstention Strategy", f"Answer threshold {ANSWER_THRESHOLD:.2f}, warning threshold {WARNING_THRESHOLD:.2f}"],
        ],
    )
    _section_header("Experimental Workflow", "Identical processing for every architecture.")
    _workflow_diagram(["Dataset", "Chunking", "Embeddings", "Vector Store", "Retriever", "Three Systems", "RAGAS", "Comparison", "Dashboard"])
    _highlight_box(
        "Reproducibility",
        "Every system uses the same benchmark set, embeddings, retrieval configuration and evaluation methodology so that the comparison is fair, reproducible and defensible in an MSc dissertation setting.",
    )


def render_evaluation_metrics() -> None:
    st.subheader("Evaluation Metrics")
    _highlight_box(
        "Why RAGAS",
        "RAGAS provides a research-friendly evaluation framework for retrieval-augmented generation because it measures answer quality, retrieval quality and grounding in a consistent way across systems.",
    )
    _render_card_grid(
        [
            ("Faithfulness", "Measures whether the answer is grounded in retrieved context.", "Selected because hallucination control is central to the dissertation.", "#1d4ed8"),
            ("Answer Relevancy", "Measures how directly the generated answer addresses the question.", "Selected to assess response usefulness and precision.", "#0f766e"),
            ("Context Precision", "Measures how much retrieved context is relevant.", "Selected to evaluate retriever quality.", "#2563eb"),
            ("Context Recall", "Measures whether the retrieved context covers the necessary information.", "Selected to assess evidence completeness.", "#7c3aed"),
        ],
        columns=2,
    )
    results = load_final_results()
    if not results.empty:
        metric_map = [
            ("ragas_faithfulness", "Faithfulness"),
            ("ragas_answer_correctness", "Answer Relevancy"),
            ("ragas_context_precision", "Context Precision"),
            ("ragas_context_recall", "Context Recall"),
        ]
        charts = []
        for column, label in metric_map:
            if column in results.columns:
                chart_data = results.groupby("system", as_index=False)[column].mean(numeric_only=True)
                charts.append((label, chart_data, column))
        if charts:
            for label, chart_data, column in charts:
                st.plotly_chart(compare_metric_bars(chart_data, column, f"Average {label} by system"), use_container_width=True)


def render_technology_stack() -> None:
    st.subheader("Technology Stack")
    tech_cards = [
        ("Dataset", "RAGBench", "Provides the research benchmark and question set.", "Chosen for reproducible academic evaluation.", "#1d4ed8"),
        ("Programming", "Python", "Implements the pipeline, evaluation and dashboard logic.", "Chosen for the research ecosystem and tooling.", "#0f766e"),
        ("Frontend", "Streamlit", "Renders the interactive academic dashboard.", "Chosen for rapid, reproducible research presentation.", "#2563eb"),
        ("LLM", OLLAMA_MODEL, "Generates responses for the compared systems.", "Chosen to keep evaluation local and controllable.", "#7c3aed"),
        ("Framework", "Multi-Agent RAG", "Controls the retrieval and reasoning workflow.", "Chosen because it is the dissertation contribution.", "#0ea5e9"),
        ("Embeddings", EMBEDDING_MODEL, "Creates semantic vector representations.", "Chosen for strong retrieval quality.", "#059669"),
        ("Vector Database", "ChromaDB", "Stores embeddings for retrieval and lookup.", "Chosen for local persistent vector search.", "#b45309"),
        ("Evaluation", "RAGAS", "Measures faithfulness and retrieval quality.", "Chosen for research-grade comparative evaluation.", "#dc2626"),
        ("Visualization", "Plotly", "Produces interactive publication-quality charts.", "Chosen for clear research communication.", "#9333ea"),
    ]
    _render_card_grid([(title, f"<strong>Technology:</strong> {tech}<br/><strong>Purpose:</strong> {purpose}", why, accent) for title, tech, purpose, why, accent in tech_cards], columns=3)


def render_experimental_results() -> None:
    st.subheader("Experimental Results")
    summary = _results_summary()
    if summary.empty:
        empty_state("Final evaluation data is unavailable.")
        return
    best_system = _best_system_label(summary)
    _highlight_box(
        "Best Performing System",
        f"Based on the available summary metrics, the strongest overall profile is <strong>{best_system}</strong>.",
    )
    metric_cards = [
        ("Accuracy", "Average accuracy across the compared systems.", "Higher is better.", "#1d4ed8"),
        ("Faithfulness", "Grounding quality against retrieved context.", "Higher is better.", "#0f766e"),
        ("Latency", "Average response time across systems.", "Lower is better.", "#7c3aed"),
        ("Hallucination Rate", f"{float(summary['hallucinated'].mean()):.3f}" if "hallucinated" in summary.columns else "Requires manual input", "Lower is better.", "#dc2626"),
    ]
    _render_card_grid(metric_cards, columns=4)
    for column in ["accuracy", "faithfulness", "ragas_answer_correctness", "ragas_context_precision", "ragas_context_recall", "confidence", "response_time", "hallucinated"]:
        if column in summary.columns:
            st.plotly_chart(compare_metric_bars(summary, column, f"Average {column.replace('_', ' ').title()} by system"), use_container_width=True)
    report = load_phase5_report()
    if not report.empty:
        st.markdown("**Calibration summary**")
        dataframe_frame(report)


def render_comparative_analysis() -> None:
    st.subheader("Comparative Analysis")
    summary = _results_summary()
    if summary.empty:
        empty_state("Final evaluation data is unavailable.")
        return
    profile_columns = [column for column in ["accuracy", "faithfulness", "ragas_answer_correctness", "ragas_context_precision", "ragas_context_recall"] if column in summary.columns]
    if profile_columns:
        radar_data = {column: float(summary[column].mean()) for column in profile_columns}
        st.plotly_chart(radar_chart(radar_data, "Average Research Profile"), use_container_width=True)
    ranking = summary.copy()
    ranking["research_score"] = ranking[profile_columns].mean(axis=1) if profile_columns else 0.0
    ranking = ranking.sort_values("research_score", ascending=False)
    _comparison_table(
        ["Rank", "System", "Research Score", "Latency", "Confidence"],
        [
            [
                str(idx + 1),
                str(row.system),
                f"{float(pd.to_numeric(getattr(row, 'research_score', 0.0), errors='coerce') if not pd.isna(getattr(row, 'research_score', 0.0)) else 0.0):.3f}",
                f"{float(pd.to_numeric(getattr(row, 'response_time', 0.0), errors='coerce') if not pd.isna(getattr(row, 'response_time', 0.0)) else 0.0):.3f}",
                f"{float(pd.to_numeric(getattr(row, 'confidence', 0.0), errors='coerce') if not pd.isna(getattr(row, 'confidence', 0.0)) else 0.0):.3f}",
            ]
            for idx, row in enumerate(ranking.itertuples(index=False))
        ],
    )
    if {"confidence", "ragas_answer_correctness"}.issubset(summary.columns):
        st.plotly_chart(scatter_chart(summary, x="confidence", y="ragas_answer_correctness", color="system", title="Confidence versus answer relevancy"), use_container_width=True)
    if "response_time" in summary.columns:
        timeline_frame = summary[["system", "response_time"]].copy()
        timeline_frame["order"] = range(1, len(timeline_frame) + 1)
        st.plotly_chart(line_chart(timeline_frame, x="order", y="response_time", color="system", title="Latency trend across systems"), use_container_width=True)


def render_research_questions() -> None:
    st.subheader("Research Questions")
    summary = _results_summary()
    best_system = _best_system_label(summary)
    _render_card_grid(
        [
            ("RQ1", "Comparative system performance", f"Evidence: final results and comparison tables. Conclusion: {best_system} is strongest in the current summary view.", "#1d4ed8"),
            ("RQ2", "Threshold and coverage trade-offs", "Evidence: threshold analysis tables and plots. Conclusion: higher thresholds improve precision while reducing coverage.", "#0f766e"),
            ("RQ3", "Confidence calibration", "Evidence: calibration report, calibration bins and reliability curve. Conclusion: the UQ system supports the strongest calibration narrative.", "#2563eb"),
            ("RQ4", "Qualitative error patterns and limitations", "Evidence: error analysis chapter and supporting notes. Conclusion: weak-evidence and abstention cases remain the main failure modes.", "#7c3aed"),
        ],
        columns=2,
    )


def render_conclusions() -> None:
    st.subheader("Conclusions")
    _render_card_grid(
        [
            ("Key Findings", "Multi-agent reasoning and confidence estimation provide a more research-appropriate profile than a single-agent baseline.", "Derived from the final results and calibration outputs.", "#1d4ed8"),
            ("Research Contributions", "A reproducible MSc research platform, a comparative multi-agent RAG evaluation, and an uncertainty-aware abstention workflow.", "Aligned with the dissertation title.", "#0f766e"),
            ("Limitations", "The benchmark is fixed and the study remains bounded to the available evaluation corpus and local model stack.", "Typical for an MSc-scale experimental dissertation.", "#2563eb"),
            ("Future Work", "Extend benchmark coverage, add stronger LLM baselines, and validate on broader enterprise document collections.", "Natural next steps after submission.", "#7c3aed"),
        ],
        columns=2,
    )

    _section_header("Research Contributions", "The principal academic and technical contributions of this dissertation.")
    _render_card_grid(
        [
            (
                "🎓 Methodological Contribution",
                "Developed a reproducible comparative evaluation framework that assesses Single-Agent RAG, Multi-Agent RAG and Multi-Agent RAG with Uncertainty Quantification under identical experimental conditions.",
                "Ensures a fair and scientifically rigorous comparison by changing only the reasoning architecture while keeping the dataset, retrieval pipeline and evaluation methodology constant.",
                "#1d4ed8",
            ),
            (
                "🧠 Technical Contribution",
                "Designed and evaluated a Multi-Agent Retrieval-Augmented Generation architecture enhanced with an Uncertainty Quantification module for confidence estimation and response reliability.",
                "Demonstrates how specialised reasoning agents and confidence estimation can improve the robustness and trustworthiness of Retrieval-Augmented Generation systems.",
                "#0f766e",
            ),
            (
                "🧪 Experimental Contribution",
                "Implemented a fully reproducible evaluation pipeline using the RAGBench benchmark dataset together with RAGAS metrics and confidence calibration analysis.",
                "Provides objective and repeatable evaluation of retrieval quality, answer quality and uncertainty across all compared architectures.",
                "#2563eb",
            ),
            (
                "📊 Practical Contribution",
                "Developed an interactive research dashboard that presents architecture, methodology, evaluation results and comparative analysis in a clear and reproducible manner.",
                "Improves transparency, interpretability and communication of experimental findings for researchers, examiners and AI practitioners.",
                "#7c3aed",
            ),
        ],
        columns=2,
    )
    _highlight_box(
        "Overall Research Contribution",
        "This dissertation contributes a reproducible framework for evaluating Retrieval-Augmented Generation architectures while demonstrating that collaborative multi-agent reasoning combined with uncertainty quantification can improve answer quality, confidence estimation and system reliability under controlled experimental conditions.",
    )


VIEW_RENDERERS = {
    "project_overview": render_project_overview,
    "architecture": render_system_architecture,
    "research_methodology": render_research_methodology,
    "experimental_setup": render_experimental_setup,
    "compared_systems": render_compared_systems,
    "evaluation_metrics": render_evaluation_metrics,
    "technology_stack": render_technology_stack,
    "experimental_results": render_experimental_results,
    "comparative_analysis": render_comparative_analysis,
    "research_questions": render_research_questions,
    "conclusions": render_conclusions,
    "home": render_home,
    "live_question_answering": render_live_question_answering,
    "three_system_comparison": render_three_system_comparison,
    "retrieval_explorer": render_retrieval_explorer,
    "evidence_verification": render_evidence_verification,
    "consistency_checker": render_consistency_checker,
    "confidence_dashboard": render_confidence_dashboard,
    "benchmark_browser": render_benchmark_browser,
    "evaluation_analytics": render_evaluation_analytics,
    "error_analysis_explorer": render_error_analysis_explorer,
    "knowledge_base_statistics": render_knowledge_base_statistics,
    "system_performance_dashboard": render_system_performance_dashboard,
    "response_timeline": render_response_timeline,
    "interactive_charts": render_interactive_charts,
    "export_results": render_export_results,
    "source_document_viewer": render_source_document_viewer,
}
