from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PAGE_THEME = {
    "bg": "#f5f7fb",
    "panel": "#ffffff",
    "ink": "#182233",
    "muted": "#5f6b7a",
    "accent": "#1f5eff",
    "accent2": "#00a884",
    "warning": "#d97706",
    "danger": "#b42318",
}


def inject_dashboard_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{ background: linear-gradient(180deg, {PAGE_THEME['bg']} 0%, #ffffff 28%, #f8fafc 100%); }}
        .main .block-container {{ max-width: 1500px; padding-top: 1.4rem; padding-bottom: 3rem; }}
        .enterprise-hero {{
            padding: 1.4rem 1.6rem;
            border-radius: 22px;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 45%, #0f766e 100%);
            color: white;
            box-shadow: 0 20px 50px rgba(15, 23, 42, 0.18);
            margin-bottom: 1rem;
        }}
        .enterprise-hero h1 {{ color: white; margin: 0 0 .3rem 0; font-size: 2.2rem; }}
        .enterprise-hero p {{ color: rgba(255,255,255,.9); margin: 0; }}
        .section-card {{
            background: {PAGE_THEME['panel']};
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }}
        .kpi-title {{ font-size: .77rem; text-transform: uppercase; letter-spacing: .08em; color: {PAGE_THEME['muted']}; }}
        .kpi-value {{ font-size: 1.85rem; font-weight: 800; color: {PAGE_THEME['ink']}; line-height: 1.1; }}
        .kpi-subtitle {{ font-size: .85rem; color: {PAGE_THEME['muted']}; }}
        .muted-note {{ color: {PAGE_THEME['muted']}; font-size: .9rem; }}
        .pill {{
            display: inline-block;
            padding: .24rem .72rem;
            border-radius: 999px;
            background: rgba(248, 250, 252, 0.94);
            color: #0f172a;
            border: 1px solid rgba(15, 23, 42, 0.16);
            font-size: .78rem;
            font-weight: 700;
            margin-right: .4rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str, tags: Iterable[str] = ()) -> None:
    pills = "".join(f"<span class='pill'>{tag}</span>" for tag in tags)
    st.markdown(
        f"""
        <div class="enterprise-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <div style="margin-top:.8rem;">{pills}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(metrics: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(metrics))
    for column, (title, value, subtitle) in zip(cols, metrics):
        with column:
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-subtitle">{subtitle}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def empty_state(message: str) -> None:
    st.info(message)


def dataframe_frame(frame: pd.DataFrame, height: int | None = None) -> None:
    if height is None:
        st.dataframe(frame, use_container_width=True, hide_index=True)
    else:
        st.dataframe(frame, use_container_width=True, height=height, hide_index=True)


def bar_chart(frame: pd.DataFrame, x: str, y: str, color: str | None = None, title: str | None = None) -> go.Figure:
    figure = px.bar(frame, x=x, y=y, color=color, text_auto=True, title=title, template="plotly_white")
    figure.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return figure


def line_chart(frame: pd.DataFrame, x: str, y: str, color: str | None = None, title: str | None = None) -> go.Figure:
    figure = px.line(frame, x=x, y=y, color=color, markers=True, title=title, template="plotly_white")
    figure.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return figure


def scatter_chart(frame: pd.DataFrame, x: str, y: str, color: str | None = None, hover_name: str | None = None, title: str | None = None) -> go.Figure:
    figure = px.scatter(frame, x=x, y=y, color=color, hover_name=hover_name, title=title, template="plotly_white")
    figure.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return figure


def hist_chart(frame: pd.DataFrame, x: str, color: str | None = None, nbins: int = 25, title: str | None = None) -> go.Figure:
    figure = px.histogram(frame, x=x, color=color, nbins=nbins, marginal="box", title=title, template="plotly_white")
    figure.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return figure


def radar_chart(metrics: dict[str, float], title: str) -> go.Figure:
    categories = list(metrics.keys())
    values = list(metrics.values())
    figure = go.Figure()
    figure.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", name=title))
    figure.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False, template="plotly_white", title=title)
    return figure


def compare_metric_bars(frame: pd.DataFrame, metric: str, title: str) -> go.Figure:
    figure = px.bar(frame, x="system", y=metric, color="system", text=metric, title=title, template="plotly_white")
    figure.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    return figure


def timeline_chart(frame: pd.DataFrame, x: str, y: str, color: str, title: str) -> go.Figure:
    figure = px.line(frame.sort_values(x), x=x, y=y, color=color, markers=False, title=title, template="plotly_white")
    figure.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return figure


def download_button(label: str, frame: pd.DataFrame, filename: str, key: str) -> None:
    st.download_button(label, frame.to_csv(index=False).encode("utf-8"), file_name=filename, mime="text/csv", use_container_width=True, key=key)
