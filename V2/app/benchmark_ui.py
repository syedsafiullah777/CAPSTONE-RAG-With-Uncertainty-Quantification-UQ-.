"""Read-only Streamlit pages: frozen question catalogue and frozen metric tables.

Does not run RAG, call Qwen, or read per-question Phase 15 outputs.
"""

from __future__ import annotations

import csv
import html

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
_DESCRIPTIVE_REL = "results/metrics/phase17_descriptive.csv"
_TESTS_REL = "results/metrics/phase17_tests.csv"

_ARCH_ORDER = ("single_agent", "multi_agent", "multi_agent_uq")
_ARCH_LABELS = {
    "single_agent": "Single-Agent",
    "multi_agent": "Multi-Agent",
    "multi_agent_uq": "Multi-Agent + UQ",
}

_MAIN_COLUMNS = (
    ("Architecture", "system"),
    ("Correctness", "did it get the answer right?"),
    ("Coverage", "how often it answered"),
    ("Answered-case accuracy", "accuracy when it answered"),
    ("Unsupported-emitted", "wrong answers actually emitted"),
    ("Faithfulness", "support from retrieved evidence"),
    ("Avg latency", "mean runtime"),
)

# Presentation labels only. Values are read from frozen Phase 17 CSV rows.
_STAT_DISPLAY = (
    {
        "id": "rq1_mcnemar_displayed_sa_vs_ma",
        "rq": "RQ1 — Accuracy",
        "what": "Single-Agent vs Multi-Agent correctness",
        "include_rho": False,
        "meaning": "Evidence checking did not significantly improve overall accuracy",
    },
    {
        "id": "rq2_spearman_uq_confidence_vs_llm_faithfulness",
        "rq": "RQ2 — Confidence & Faithfulness",
        "what": "UQ confidence vs evidence faithfulness",
        "include_rho": True,
        "meaning": "Higher confidence was strongly associated with better evidence support",
    },
    {
        "id": "rq2_mannwhitney_uq_llm_answer_vs_abstain",
        "rq": "RQ2 — ANSWER vs ABSTAIN",
        "what": "Faithfulness of answered vs abstained cases",
        "include_rho": False,
        "meaning": "ANSWER cases had stronger evidence support",
    },
    {
        "id": "rq2_wilcoxon_llm_ma_vs_uq",
        "rq": "RQ2 — Mean Faithfulness",
        "what": "Multi-Agent vs Multi-Agent + UQ",
        "include_rho": False,
        "meaning": "UQ did not significantly change overall mean faithfulness",
    },
    {
        "id": "rq3_mcnemar_unsupported_ma_vs_uq",
        "rq": "RQ3 — Unsupported Answers",
        "what": "Multi-Agent vs Multi-Agent + UQ",
        "include_rho": False,
        "meaning": "UQ substantially reduced unsupported-emitted answers",
    },
    {
        "id": "rq3_mcnemar_unsupported_sa_vs_uq",
        "rq": "RQ3 — Unsupported Answers",
        "what": "Single-Agent vs Multi-Agent + UQ",
        "include_rho": False,
        "meaning": "UQ also reduced unsupported-emitted answers vs baseline",
    },
)

_RESULTS_CSS = """
<style>
.viva-bench { margin: 0.25rem 0 1.15rem 0; }
.viva-bench table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
.viva-bench th, .viva-bench td {
  text-align: left; vertical-align: top;
  padding: 0.62rem 0.7rem;
  border-bottom: 1px solid rgba(49, 51, 63, 0.16);
}
.viva-bench thead th { border-bottom: 1px solid rgba(49, 51, 63, 0.28); }
.viva-bench .sub {
  display: block; font-weight: 400; font-size: 0.75rem;
  color: rgba(49, 51, 63, 0.62); margin-top: 0.18rem;
}
.viva-bench .sig { color: #1a7a74; font-weight: 600; }
.viva-bench .ns { color: rgba(49, 51, 63, 0.72); }
.viva-bench .interp {
  margin: 0.35rem 0 0.2rem 0;
  padding: 0.85rem 1rem;
  background: rgba(240, 242, 246, 0.85);
  border-left: 3px solid rgba(26, 122, 116, 0.85);
}
</style>
"""


def _read_csv_rows(rel: str) -> list[dict[str, str]]:
    path = project_root() / rel
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _count_pct(count: int, total: int) -> str:
    pct = 100.0 * count / total
    if abs(pct - round(pct)) < 1e-9:
        return f"{count}/{total} ({int(round(pct))}%)"
    return f"{count}/{total} ({pct:.2f}%)"


def _html_table(headers: tuple[tuple[str, str], ...], rows: list[list[str]]) -> str:
    head_cells = []
    for title, subtitle in headers:
        sub = f"<span class='sub'>{html.escape(subtitle)}</span>" if subtitle else ""
        head_cells.append(f"<th>{html.escape(title)}{sub}</th>")
    body = []
    for row in rows:
        tds = "".join(f"<td>{cell}</td>" for cell in row)
        body.append(f"<tr>{tds}</tr>")
    return (
        "<div class='viva-bench'><table>"
        f"<thead><tr>{''.join(head_cells)}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody>"
        "</table></div>"
    )


def _main_results_rows(
    summary: list[dict[str, str]],
    descriptive: list[dict[str, str]],
) -> list[list[str]] | None:
    by_arch = {row.get("architecture"): row for row in summary}
    desc_by = {row.get("architecture"): row for row in descriptive}
    out: list[list[str]] = []
    for arch in _ARCH_ORDER:
        row = by_arch.get(arch)
        desc = desc_by.get(arch)
        if not row or not desc:
            return None
        n = int(float(row["n"]))
        n_answer = int(float(row["n_answer"]))
        n_correct = int(float(row["n_correct_displayed"]))
        n_correct_answered = int(float(row["n_correct_answered"]))
        n_unsupported = n_answer - n_correct_answered
        faith = float(desc["llm_faithfulness_mean"])
        latency = float(row["mean_latency_seconds"])
        out.append(
            [
                html.escape(_ARCH_LABELS[arch]),
                html.escape(_count_pct(n_correct, n)),
                html.escape(_count_pct(n_answer, n)),
                html.escape(_count_pct(n_correct_answered, n_answer)),
                html.escape(_count_pct(n_unsupported, n)),
                html.escape(f"{faith:.4f}"),
                html.escape(f"{latency:.2f} s"),
            ]
        )
    return out


def _fmt_stat_result(row: dict[str, str], *, include_rho: bool) -> tuple[str, bool]:
    p_raw = row.get("p_value_holm") or row.get("p_value") or ""
    p_value = float(p_raw)
    significant = str(row.get("significant_holm_0.05") or "").strip().lower() == "true"
    label = "Significant" if significant else "Not significant"
    css = "sig" if significant else "ns"
    if p_value < 0.001:
        p_txt = "p < 0.001"
    else:
        p_txt = f"p = {p_value:.4f}"
    if include_rho:
        rho = float(row.get("statistic") or 0.0)
        p_txt = f"ρ = {rho:.4f} · {p_txt}"
    display = html.escape(f"{p_txt} · {label}")
    return f"<span class='{css}'>{display}</span>", significant


def _stat_rows(tests: list[dict[str, str]]) -> list[list[str]] | None:
    by_id = {row.get("id"): row for row in tests}
    out: list[list[str]] = []
    for spec in _STAT_DISPLAY:
        row = by_id.get(spec["id"])
        if not row:
            return None
        result_html, _ = _fmt_stat_result(row, include_rho=spec["include_rho"])
        out.append(
            [
                html.escape(spec["rq"]),
                html.escape(spec["what"]),
                result_html,
                html.escape(spec["meaning"]),
            ]
        )
    return out


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
    st.markdown(_RESULTS_CSS, unsafe_allow_html=True)

    summary = _read_csv_rows(_SUMMARY_REL)
    descriptive = _read_csv_rows(_DESCRIPTIVE_REL)
    main_rows = _main_results_rows(summary, descriptive) if summary and descriptive else None
    if main_rows:
        st.subheader("Main Results — Frozen 140-Question Test Set")
        st.caption("Three architectures, same 140 questions")
        st.markdown(_html_table(_MAIN_COLUMNS, main_rows), unsafe_allow_html=True)
        st.caption(
            "Counts and percentages are shown together. "
            "Faithfulness is the mean 0–1 score from the custom Qwen3-8B judge."
        )
        st.caption(
            "Unsupported-emitted is an operational metric: answered and numerically incorrect; "
            "it is not a ground-truth hallucination rate."
        )
        st.markdown(
            "- Single-Agent and Multi-Agent always answer (**140/140**). "
            "Overall correctness stays similar (**32/140** vs **29/140**).\n"
            "- Multi-Agent + UQ answers **78/140**. "
            "Answered-case accuracy rises to **32/78 (41.03%)**.\n"
            "- Unsupported-emitted falls from **108/140** and **111/140** to **46/140** "
            "when UQ can abstain."
        )
    elif not summary:
        st.warning("Frozen Phase 16 summary table is not present in this checkout.")
    else:
        st.warning("Frozen Phase 17 descriptive table is not present in this checkout.")

    st.markdown("&nbsp;")
    tests = _read_csv_rows(_TESTS_REL)
    stat_rows = _stat_rows(tests) if tests else None
    if stat_rows:
        st.subheader("Phase 17 — Statistical Findings (Frozen)")
        st.markdown(
            _html_table(
                (
                    ("RQ", ""),
                    ("What we tested", ""),
                    ("Result", ""),
                    ("Meaning", ""),
                ),
                stat_rows,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='viva-bench'><div class='interp'><strong>Interpretation:</strong> "
            "Multi-Agent verification alone did not improve overall correctness. "
            "UQ mainly changed response selection: confidence identified better-supported cases "
            "and abstention reduced unsupported-emitted answers at the cost of coverage."
            "</div></div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Detailed test statistics and Holm-adjusted results remain stored in the frozen "
            "Phase 17 evaluation outputs."
        )
    elif not tests:
        st.caption("Frozen Phase 17 test table is not present in this checkout.")
    else:
        st.caption("Frozen Phase 17 confirmatory rows are not present in this checkout.")



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
