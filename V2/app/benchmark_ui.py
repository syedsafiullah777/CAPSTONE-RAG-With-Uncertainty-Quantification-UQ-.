"""Read-only Streamlit pages: frozen question catalogue and frozen metric tables.

Does not run RAG, call Qwen, or read per-question Phase 15 outputs.
"""

from __future__ import annotations

import csv

import streamlit as st

from src.config import project_root
from src.rag.benchmark_catalogue import (
    ALL_COMPANIES,
    FROZEN_N,
    PAGE_SIZE,
    company_options,
    filter_catalogue,
    load_frozen_catalogue,
    paginate,
    queue_live_demo_navigation,
    validate_catalogue,
)

_SUMMARY_REL = "results/metrics/phase16_summary.csv"
_TESTS_REL = "results/metrics/phase17_tests.csv"
_SUMMARY_COLUMNS = (
    "architecture",
    "n",
    "n_answer",
    "n_abstain",
    "coverage",
    "answer_correctness",
    "selective_accuracy",
    "unsupported_emitted_rate",
)
_TEST_COLUMNS = ("id", "rq", "left", "right", "test", "p_value", "significant_holm_0.05")


def _read_csv_rows(rel: str) -> list[dict[str, str]]:
    path = project_root() / rel
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _on_use_in_live_demo(question_id: str, question: str) -> None:
    """Button callback: runs before widgets on the next rerun."""
    queue_live_demo_navigation(st.session_state, {"id": question_id, "question": question})


def render_benchmark_results_page() -> None:
    st.title("Benchmark Results")
    st.caption(
        "Read-only frozen metric tables. This page does not rerun experiments, "
        "does not call the LLM, and does not load per-question system answers."
    )
    st.info("Locked threshold T = 0.65 is unchanged. Faithfulness is custom/RAGAS-inspired, not official RAGAS.")

    summary = _read_csv_rows(_SUMMARY_REL)
    if summary:
        st.subheader("Phase 16 summary (frozen)")
        st.dataframe(
            [{key: row.get(key, "") for key in _SUMMARY_COLUMNS} for row in summary],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("Frozen Phase 16 summary table is not present in this checkout.")

    tests = _read_csv_rows(_TESTS_REL)
    confirmatory = [row for row in tests if row.get("role") == "confirmatory"]
    if confirmatory:
        st.subheader("Phase 17 confirmatory tests (frozen)")
        st.dataframe(
            [{key: row.get(key, "") for key in _TEST_COLUMNS} for row in confirmatory],
            use_container_width=True,
            hide_index=True,
        )
    elif not tests:
        st.caption("Frozen Phase 17 test table is not present in this checkout.")


def render_benchmark_questions_page() -> None:
    st.title("Frozen FinQA Test Set — 140 Questions")
    st.caption("Read-only reference for live demonstration")
    st.write(
        f"Complete frozen test set (**{FROZEN_N}** questions). "
        "Browse and inspect questions here. This page does not run RAG, "
        "does not call Qwen3-8B, and does not look up saved benchmark answers."
    )

    rows = load_frozen_catalogue()
    check = validate_catalogue(rows)
    if not check["ok"]:
        st.error(
            f"Frozen catalogue failed validation: n={check['n']} "
            f"unique_ids={check['unique_ids']} (expected {FROZEN_N})."
        )
        return
    st.success(f"Loaded {check['n']} questions · {check['unique_ids']} unique IDs · read-only")

    id_query = st.text_input("Search question ID", value="", placeholder="e.g. finqa_test_1000")
    text_query = st.text_input("Search question text", value="", placeholder="e.g. shareholder return")
    companies = company_options(rows)
    company = st.selectbox("Company", options=companies, index=0)

    filtered = filter_catalogue(
        rows,
        id_query=id_query,
        text_query=text_query,
        company=company or ALL_COMPANIES,
    )
    n_filtered = len(filtered)
    n_pages = max(1, (n_filtered + PAGE_SIZE - 1) // PAGE_SIZE) if n_filtered else 1

    filter_key = f"{id_query}|{text_query}|{company}"
    if st.session_state.get("_catalogue_filter_key") != filter_key:
        st.session_state["_catalogue_filter_key"] = filter_key
        st.session_state["catalogue_page"] = 1

    page_labels = [str(i) for i in range(1, n_pages + 1)]
    current = str(int(st.session_state.get("catalogue_page") or 1))
    if current not in page_labels:
        current = "1"
    nav_l, nav_m, nav_r = st.columns([1, 2, 1])
    with nav_l:
        if st.button("Previous", disabled=current == "1"):
            st.session_state["catalogue_page"] = max(1, int(current) - 1)
            st.rerun()
    with nav_m:
        chosen = st.selectbox("Page", options=page_labels, index=page_labels.index(current))
        if chosen != current:
            st.session_state["catalogue_page"] = int(chosen)
            st.rerun()
    with nav_r:
        if st.button("Next", disabled=current == page_labels[-1]):
            st.session_state["catalogue_page"] = min(n_pages, int(current) + 1)
            st.rerun()

    page_rows, showing_from, showing_to, n_total, page, _n_pages = paginate(
        filtered,
        int(st.session_state.get("catalogue_page") or 1),
        PAGE_SIZE,
    )
    st.markdown(f"**Showing {showing_from}–{showing_to} of {n_total}** (full frozen set: {FROZEN_N})")

    if not page_rows:
        st.info("No questions match the current filters.")
        return

    for row in page_rows:
        title = f"{row['id']} · {row.get('company_name') or 'n/a'} · {row.get('report_year') or 'n/a'}"
        with st.expander(title, expanded=False):
            st.write(row["question"])
            st.markdown(
                f"**Company:** {row.get('company_name') or 'n/a'} "
                f"(`{row.get('company_symbol') or 'n/a'}`) · "
                f"**Year:** {row.get('report_year') or 'n/a'} · "
                f"**Sector:** {row.get('company_sector') or 'n/a'}  \n"
                f"**Source file:** `{row.get('file_name') or 'n/a'}` · "
                f"**Page:** {row.get('page_number') or 'n/a'} · "
                f"**Split:** {row.get('split') or 'n/a'} · "
                f"**context_id:** `{row.get('context_id') or 'n/a'}`"
            )
            gold = row.get("program_answer") or ""
            if gold:
                st.caption(
                    f"FinQA gold program_answer (dataset reference, not a V2 RAG output): `{gold}`"
                )
            st.button(
                "Use this question in Live Demo",
                key=f"use_{row['id']}",
                on_click=_on_use_in_live_demo,
                args=(row["id"], row["question"]),
            )
