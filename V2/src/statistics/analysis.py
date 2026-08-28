"""Phase 17 RQ1–RQ3 analysis on frozen Phase 16 outputs."""

from __future__ import annotations

from typing import Any

from src.statistics.constants import (
    ALPHA,
    ARCH_LABELS,
    ARCH_MA,
    ARCH_SA,
    ARCH_UQ,
    ARCHITECTURES,
    JUDGE_METRIC_LABEL,
    LOCKED_T,
    N_QUESTIONS,
)
from src.statistics.load import load_joined, series
from src.statistics.tests import (
    bootstrap_mean_diff,
    bootstrap_selective_minus_baseline,
    holm_adjust,
    mannwhitney,
    mcnemar_exact,
    mean_sd,
    shapiro_wilk,
    significant,
    spearman_corr,
    t_ci_mean,
    wilcoxon_paired,
    wilson_ci,
)


def _i(values: list[Any]) -> list[int]:
    return [int(v) for v in values]


def _f(values: list[Any]) -> list[float]:
    return [float(v) for v in values]


def _f_optional(values: list[Any]) -> list[float]:
    return [float(v) for v in values if v is not None]


def _annotate_family(rows: list[dict[str, Any]], family: str) -> list[dict[str, Any]]:
    pvals = [row["p_value"] if row.get("p_value") is not None else float("nan") for row in rows]
    adjusted = holm_adjust(pvals)
    out = []
    for row, padj in zip(rows, adjusted):
        copied = dict(row)
        copied["family"] = family
        copied["p_value_holm"] = padj
        copied["significant_holm_0.05"] = significant(padj)
        copied["alpha"] = ALPHA
        out.append(copied)
    return out


def _arch_descriptive(joined: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for arch in ARCHITECTURES:
        displayed = _i(series(joined, arch, "answer_correctness"))
        claim = _i(series(joined, arch, "answer_correctness_claim"))
        answered = _i(series(joined, arch, "answered"))
        unsupported = _i(series(joined, arch, "unsupported_emitted"))
        llm = _f(series(joined, arch, "llm_faithfulness"))
        overlap = _f(series(joined, arch, "faithfulness"))
        ctx_p = _f(series(joined, arch, "context_precision"))
        ctx_r = _f(series(joined, arch, "context_recall"))
        n_answer = sum(answered)
        n_abstain = N_QUESTIONS - n_answer
        n_correct_answered = sum(d for d, a in zip(displayed, answered) if a)
        sel = wilson_ci(n_correct_answered, n_answer) if n_answer else {
            "n": 0, "k": 0, "mean": None, "ci_low": None, "ci_high": None
        }
        llm_answer = [s for s, a in zip(llm, answered) if a]
        llm_abstain = [s for s, a in zip(llm, answered) if not a]
        conf = series(joined, arch, "confidence")
        rows.append({
            "architecture": arch,
            "label": ARCH_LABELS[arch],
            "n": N_QUESTIONS,
            "n_answer": n_answer,
            "n_abstain": n_abstain,
            "coverage": n_answer / N_QUESTIONS,
            "coverage_wilson": wilson_ci(n_answer, N_QUESTIONS),
            "abstention_rate": n_abstain / N_QUESTIONS,
            "abstention_wilson": wilson_ci(n_abstain, N_QUESTIONS),
            "displayed_correct_k": sum(displayed),
            "displayed_correctness": wilson_ci(sum(displayed), N_QUESTIONS),
            "claim_correct_k": sum(claim),
            "claim_correctness": wilson_ci(sum(claim), N_QUESTIONS),
            "selective_accuracy_k": n_correct_answered,
            "selective_accuracy_n": n_answer,
            "selective_accuracy": sel,
            "unsupported_emitted_k": sum(unsupported),
            "unsupported_emitted": wilson_ci(sum(unsupported), N_QUESTIONS),
            "llm_faithfulness_all": {**mean_sd(llm), **{k: t_ci_mean(llm)[k] for k in ("ci_low", "ci_high", "df")}},
            "llm_faithfulness_answered": mean_sd(llm_answer) if llm_answer else {"n": 0, "mean": None, "sd": None},
            "llm_faithfulness_abstained": mean_sd(llm_abstain) if llm_abstain else {"n": 0, "mean": None, "sd": None},
            "token_overlap": {**mean_sd(overlap), **{k: t_ci_mean(overlap)[k] for k in ("ci_low", "ci_high", "df")}},
            "context_precision": mean_sd(ctx_p),
            "context_recall": mean_sd(ctx_r),
            "confidence": mean_sd(_f_optional(conf)),
        })
    return rows


def analyse(root=None) -> dict[str, Any]:
    joined = load_joined(root)
    descriptive = _arch_descriptive(joined)

    sa_disp = _i(series(joined, ARCH_SA, "answer_correctness"))
    ma_disp = _i(series(joined, ARCH_MA, "answer_correctness"))
    uq_disp = _i(series(joined, ARCH_UQ, "answer_correctness"))
    sa_claim = _i(series(joined, ARCH_SA, "answer_correctness_claim"))
    ma_claim = _i(series(joined, ARCH_MA, "answer_correctness_claim"))
    uq_claim = _i(series(joined, ARCH_UQ, "answer_correctness_claim"))
    sa_unsup = _i(series(joined, ARCH_SA, "unsupported_emitted"))
    ma_unsup = _i(series(joined, ARCH_MA, "unsupported_emitted"))
    uq_unsup = _i(series(joined, ARCH_UQ, "unsupported_emitted"))
    sa_llm = _f(series(joined, ARCH_SA, "llm_faithfulness"))
    ma_llm = _f(series(joined, ARCH_MA, "llm_faithfulness"))
    uq_llm = _f(series(joined, ARCH_UQ, "llm_faithfulness"))
    sa_ov = _f(series(joined, ARCH_SA, "faithfulness"))
    ma_ov = _f(series(joined, ARCH_MA, "faithfulness"))
    uq_ov = _f(series(joined, ARCH_UQ, "faithfulness"))
    uq_ans = _i(series(joined, ARCH_UQ, "answered"))
    uq_conf = _f(series(joined, ARCH_UQ, "confidence"))

    # RQ1 confirmatory: SA vs MA displayed numeric correctness
    rq1_primary = dict(mcnemar_exact(sa_disp, ma_disp))
    rq1_primary.update({
        "id": "rq1_mcnemar_displayed_sa_vs_ma",
        "rq": "RQ1",
        "role": "confirmatory",
        "left": ARCH_SA,
        "right": ARCH_MA,
        "outcome": "displayed numeric answer correctness",
        "layer": "numeric FinQA correctness (primary RQ1)",
        "unit": "frozen FinQA test question (n=140), paired across architectures",
    })
    rq1_conf = _annotate_family([rq1_primary], "rq1_confirmatory")

    rq1_expl_raw = [
        {
            **mcnemar_exact(sa_disp, uq_disp),
            "id": "rq1_mcnemar_displayed_sa_vs_uq",
            "rq": "RQ1",
            "role": "exploratory",
            "left": ARCH_SA,
            "right": ARCH_UQ,
            "outcome": "displayed numeric answer correctness",
            "layer": "numeric FinQA correctness",
            "note": "UQ ABSTAIN displayed text is the abstention template and is usually numerically incorrect.",
            "unit": "frozen FinQA test question (n=140), paired",
        },
        {
            **mcnemar_exact(ma_disp, uq_disp),
            "id": "rq1_mcnemar_displayed_ma_vs_uq",
            "rq": "RQ1",
            "role": "exploratory",
            "left": ARCH_MA,
            "right": ARCH_UQ,
            "outcome": "displayed numeric answer correctness",
            "layer": "numeric FinQA correctness",
            "unit": "frozen FinQA test question (n=140), paired",
        },
        {
            **mcnemar_exact(sa_claim, ma_claim),
            "id": "rq1_mcnemar_claim_sa_vs_ma",
            "rq": "RQ1",
            "role": "exploratory",
            "left": ARCH_SA,
            "right": ARCH_MA,
            "outcome": "claim numeric correctness (UQ uses draft)",
            "layer": "numeric FinQA correctness (claim)",
            "unit": "frozen FinQA test question (n=140), paired",
        },
        {
            **mcnemar_exact(sa_claim, uq_claim),
            "id": "rq1_mcnemar_claim_sa_vs_uq",
            "rq": "RQ1",
            "role": "exploratory",
            "left": ARCH_SA,
            "right": ARCH_UQ,
            "outcome": "claim numeric correctness (UQ uses draft)",
            "layer": "numeric FinQA correctness (claim)",
            "unit": "frozen FinQA test question (n=140), paired",
        },
        {
            **mcnemar_exact(ma_claim, uq_claim),
            "id": "rq1_mcnemar_claim_ma_vs_uq",
            "rq": "RQ1",
            "role": "exploratory",
            "left": ARCH_MA,
            "right": ARCH_UQ,
            "outcome": "claim numeric correctness (UQ uses draft)",
            "layer": "numeric FinQA correctness (claim)",
            "unit": "frozen FinQA test question (n=140), paired",
        },
    ]
    rq1_expl = _annotate_family(rq1_expl_raw, "rq1_exploratory")

    # RQ2 confirmatory
    llm_ans = [s for s, a in zip(uq_llm, uq_ans) if a]
    llm_abs = [s for s, a in zip(uq_llm, uq_ans) if not a]
    rq2_conf_raw = [
        {
            **spearman_corr(uq_conf, uq_llm),
            "id": "rq2_spearman_uq_confidence_vs_llm_faithfulness",
            "rq": "RQ2",
            "role": "confirmatory",
            "outcome": "UQ confidence vs LLM-as-judge faithfulness (all 140, draft claim)",
            "layer": JUDGE_METRIC_LABEL,
            "unit": "frozen FinQA test question (n=140) within multi_agent_uq",
        },
        {
            **mannwhitney(llm_ans, llm_abs, "UQ ANSWER", "UQ ABSTAIN"),
            "id": "rq2_mannwhitney_uq_llm_answer_vs_abstain",
            "rq": "RQ2",
            "role": "confirmatory",
            "outcome": "LLM-as-judge faithfulness, UQ ANSWER vs ABSTAIN",
            "layer": JUDGE_METRIC_LABEL,
            "unit": "question grouped by UQ decision (unpaired; n_ANSWER=78, n_ABSTAIN=62)",
        },
        {
            **wilcoxon_paired(ma_llm, uq_llm),
            "id": "rq2_wilcoxon_llm_ma_vs_uq",
            "rq": "RQ2",
            "role": "confirmatory",
            "left": ARCH_MA,
            "right": ARCH_UQ,
            "outcome": "LLM-as-judge faithfulness (all 140; UQ includes abstained drafts)",
            "layer": JUDGE_METRIC_LABEL,
            "unit": "frozen FinQA test question (n=140), paired",
        },
    ]
    rq2_conf = _annotate_family(rq2_conf_raw, "rq2_confirmatory")

    conf_ans = [c for c, a in zip(uq_conf, uq_ans) if a]
    llm_ans_only = [s for s, a in zip(uq_llm, uq_ans) if a]
    rq2_expl_raw = [
        {
            **wilcoxon_paired(sa_llm, ma_llm),
            "id": "rq2_wilcoxon_llm_sa_vs_ma",
            "rq": "RQ2",
            "role": "exploratory",
            "left": ARCH_SA,
            "right": ARCH_MA,
            "outcome": "LLM-as-judge faithfulness",
            "layer": JUDGE_METRIC_LABEL,
            "unit": "frozen FinQA test question (n=140), paired",
        },
        {
            **wilcoxon_paired(sa_llm, uq_llm),
            "id": "rq2_wilcoxon_llm_sa_vs_uq",
            "rq": "RQ2",
            "role": "exploratory",
            "left": ARCH_SA,
            "right": ARCH_UQ,
            "outcome": "LLM-as-judge faithfulness",
            "layer": JUDGE_METRIC_LABEL,
            "unit": "frozen FinQA test question (n=140), paired",
        },
        {
            **spearman_corr(uq_conf, _f(uq_claim)),
            "id": "rq2_spearman_uq_confidence_vs_claim_correctness",
            "rq": "RQ2",
            "role": "exploratory",
            "outcome": "UQ confidence vs numeric claim correctness",
            "layer": "numeric FinQA correctness (claim) vs UQ confidence",
            "unit": "frozen FinQA test question (n=140) within multi_agent_uq",
        },
        {
            **spearman_corr(conf_ans, llm_ans_only),
            "id": "rq2_spearman_uq_confidence_vs_llm_among_answered",
            "rq": "RQ2",
            "role": "exploratory",
            "outcome": "UQ confidence vs LLM-as-judge faithfulness (ANSWER only)",
            "layer": JUDGE_METRIC_LABEL,
            "unit": "UQ ANSWER questions only (n=78)",
        },
    ]
    rq2_expl = _annotate_family(rq2_expl_raw, "rq2_exploratory")

    # RQ3
    rq3_conf_raw = [
        {
            **mcnemar_exact(sa_unsup, uq_unsup),
            "id": "rq3_mcnemar_unsupported_sa_vs_uq",
            "rq": "RQ3",
            "role": "confirmatory",
            "left": ARCH_SA,
            "right": ARCH_UQ,
            "outcome": "unsupported_emitted (ANSWER and displayed numeric incorrect)",
            "layer": "coverage / selective accuracy / abstention (RQ3); not a hallucination label",
            "unit": "frozen FinQA test question (n=140), paired",
        },
        {
            **mcnemar_exact(ma_unsup, uq_unsup),
            "id": "rq3_mcnemar_unsupported_ma_vs_uq",
            "rq": "RQ3",
            "role": "confirmatory",
            "left": ARCH_MA,
            "right": ARCH_UQ,
            "outcome": "unsupported_emitted (ANSWER and displayed numeric incorrect)",
            "layer": "coverage / selective accuracy / abstention (RQ3); not a hallucination label",
            "unit": "frozen FinQA test question (n=140), paired",
        },
    ]
    rq3_conf = _annotate_family(rq3_conf_raw, "rq3_confirmatory")

    n_true_abstain = sum(1 for a, c in zip(uq_ans, uq_claim) if (not a) and (not c))
    n_false_abstain = sum(1 for a, c in zip(uq_ans, uq_claim) if (not a) and c)
    n_true_answer = sum(1 for a, d in zip(uq_ans, uq_disp) if a and d)
    n_false_answer = sum(1 for a, d in zip(uq_ans, uq_disp) if a and not d)

    sel_vs_sa = bootstrap_selective_minus_baseline(uq_ans, uq_disp, sa_disp)
    sel_vs_ma = bootstrap_selective_minus_baseline(uq_ans, uq_disp, ma_disp)

    secondary_overlap = _annotate_family(
        [
            {**wilcoxon_paired(sa_ov, ma_ov), "id": "sec_overlap_sa_vs_ma", "left": ARCH_SA, "right": ARCH_MA},
            {**wilcoxon_paired(sa_ov, uq_ov), "id": "sec_overlap_sa_vs_uq", "left": ARCH_SA, "right": ARCH_UQ},
            {**wilcoxon_paired(ma_ov, uq_ov), "id": "sec_overlap_ma_vs_uq", "left": ARCH_MA, "right": ARCH_UQ},
        ],
        "secondary_token_overlap",
    )
    for row in secondary_overlap:
        row["rq"] = "secondary"
        row["role"] = "secondary"
        row["outcome"] = "CPU token-overlap faithfulness"
        row["layer"] = "token-overlap (secondary; not official RAGAS; not RQ2 primary)"
        row["unit"] = "frozen FinQA test question (n=140), paired"

    ctx_p_sa = _f(series(joined, ARCH_SA, "context_precision"))
    ctx_p_ma = _f(series(joined, ARCH_MA, "context_precision"))
    ctx_p_uq = _f(series(joined, ARCH_UQ, "context_precision"))
    retrieval_note = (
        "Context precision and recall are identical across architectures by design "
        "(shared retrieval). They are retrieval-control metrics, not architecture tests."
    )
    ctx_identical = (
        ctx_p_sa == ctx_p_ma == ctx_p_uq
        and _f(series(joined, ARCH_SA, "context_recall"))
        == _f(series(joined, ARCH_MA, "context_recall"))
        == _f(series(joined, ARCH_UQ, "context_recall"))
    )

    assumptions = []
    for name, left, right in (
        ("llm_sa_vs_ma", sa_llm, ma_llm),
        ("llm_ma_vs_uq", ma_llm, uq_llm),
        ("llm_sa_vs_uq", sa_llm, uq_llm),
        ("overlap_sa_vs_ma", sa_ov, ma_ov),
        ("uq_confidence", uq_conf, uq_conf),
    ):
        if name == "uq_confidence":
            assumptions.append({"name": name, "shapiro": shapiro_wilk(uq_conf), "metric": "UQ confidence"})
        else:
            diff = [r - l for l, r in zip(left, right)]
            assumptions.append({"name": name, "shapiro": shapiro_wilk(diff), "metric": name})

    interpretation = {
        "statistical_unit": (
            "The statistical unit is the frozen FinQA test question (n=140). "
            "The same 140 questions were evaluated independently on three architectures "
            "(no RAG1→RAG2→RAG3 chaining). Between-architecture tests are paired on question_id. "
            "Do not treat 420 cases as independent samples for architecture comparisons."
        ),
        "layers": {
            "rq1": "numeric FinQA displayed answer correctness (rel_tol=0.01) is the primary RQ1 measure",
            "rq2": JUDGE_METRIC_LABEL + " — not official RAGAS",
            "rq3": "coverage, selective accuracy, abstention, unsupported_emitted at locked T=0.65",
            "retrieval": "context precision/recall (gold file_name / context_id)",
            "secondary": "CPU token-overlap faithfulness",
        },
        "rq1": None,
        "rq2": None,
        "rq3": None,
        "limitations": [
            "Same-model Qwen3-8B judge; not official RAGAS Faithfulness.",
            "unsupported_emitted is answered-and-numerically-wrong, not a labelled hallucination corpus.",
            "Selective accuracy uses a selected subset (UQ ANSWER); it is not a paired accuracy on all 140.",
            "T=0.65 was locked on DEV 40 only; it was not retuned on the frozen 140.",
            "Questions are a frozen sample of FinQA test; company repeats may induce weak dependence.",
            "Phase 17 does not rerun RAG, Qwen generation, or the judge.",
        ],
    }

    # Fill interpretation after seeing Holm results (honest)
    p_rq1 = rq1_conf[0]["p_value_holm"]
    rho_conf = rq2_conf[0].get("statistic")
    p_rho = rq2_conf[0]["p_value_holm"]
    p_mw = rq2_conf[1]["p_value_holm"]
    p_w = rq2_conf[2]["p_value_holm"]
    p_unsup_sa = rq3_conf[0]["p_value_holm"]
    p_unsup_ma = rq3_conf[1]["p_value_holm"]
    interpretation["rq1"] = (
        f"Confirmatory McNemar (exact binomial) on displayed FinQA numeric correctness, "
        f"Single-Agent vs Multi-Agent, n=140 paired questions: SA {sum(sa_disp)}/140 "
        f"(Wilson 95% CI {wilson_ci(sum(sa_disp), 140)['ci_low']:.4f}–{wilson_ci(sum(sa_disp), 140)['ci_high']:.4f}) "
        f"vs MA {sum(ma_disp)}/140 "
        f"(Wilson 95% CI {wilson_ci(sum(ma_disp), 140)['ci_low']:.4f}–{wilson_ci(sum(ma_disp), 140)['ci_high']:.4f}); "
        f"discordant pairs {rq1_conf[0]['n_discordant']} (SA-only {rq1_conf[0]['n10_left_only']}, "
        f"MA-only {rq1_conf[0]['n01_right_only']}); exact p={rq1_conf[0]['p_value']:.4g}; "
        f"Holm-adjusted p={p_rq1:.4g} (family size 1); Cohen's g={rq1_conf[0]['effect_cohens_g']:.4f}. "
        "This is not statistically significant at α=0.05. "
        "The data do not support a Multi-Agent accuracy improvement over Single-Agent."
    )
    interpretation["rq2"] = (
        f"UQ confidence is positively associated with {JUDGE_METRIC_LABEL} "
        f"(Spearman ρ={rho_conf:.4f}, df=138, p={rq2_conf[0]['p_value']:.4g}, "
        f"Holm p={p_rho:.4g}). "
        f"ANSWER cases have higher judge faithfulness than ABSTAIN cases "
        f"(means {sum(llm_ans)/len(llm_ans):.4f} vs {sum(llm_abs)/len(llm_abs):.4f}; "
        f"Mann–Whitney U={rq2_conf[1]['statistic']:.1f}, p={rq2_conf[1]['p_value']:.4g}, "
        f"Holm p={p_mw:.4g}). "
        f"Paired Wilcoxon of the same judge score, Multi-Agent vs UQ on all 140 questions, "
        f"is not significant (W={rq2_conf[2]['statistic']}, p={rq2_conf[2]['p_value']:.4g}, "
        f"Holm p={p_w:.4g}). "
        "Holm family size=3. "
        "Confidence therefore tracks support/abstention within UQ, but UQ does not significantly "
        "raise mean faithfulness versus always-answer Multi-Agent on the full paired set "
        "(abstained drafts pull the UQ mean down). Not official RAGAS."
    )
    interpretation["rq3"] = (
        f"At locked T=0.65, UQ coverage is {sum(uq_ans)}/140="
        f"{sum(uq_ans)/N_QUESTIONS:.4f} (Wilson 95% CI "
        f"{wilson_ci(sum(uq_ans), 140)['ci_low']:.4f}–{wilson_ci(sum(uq_ans), 140)['ci_high']:.4f}); "
        f"selective displayed accuracy {n_true_answer}/{sum(uq_ans)}="
        f"{n_true_answer/sum(uq_ans):.4f} (Wilson 95% CI "
        f"{wilson_ci(n_true_answer, sum(uq_ans))['ci_low']:.4f}–"
        f"{wilson_ci(n_true_answer, sum(uq_ans))['ci_high']:.4f}). "
        f"Abstention outcomes on the draft: true abstain (incorrect draft) {n_true_abstain}; "
        f"false abstain (correct draft withheld) {n_false_abstain}. "
        f"Unsupported-emitted rate falls from SA {sum(sa_unsup)}/140 and MA {sum(ma_unsup)}/140 "
        f"to UQ {sum(uq_unsup)}/140; confirmatory McNemar Holm p="
        f"{p_unsup_sa:.4g} vs SA and {p_unsup_ma:.4g} vs MA (both significant at α=0.05). "
        f"Bootstrap 95% CI for (UQ selective accuracy − SA accuracy) is "
        f"{sel_vs_sa['ci_low']:.4f} to {sel_vs_sa['ci_high']:.4f} "
        f"(observed {sel_vs_sa['observed_difference']:.4f}). "
        "Abstention therefore reduces emitted numeric errors at the cost of coverage; "
        "this is not a labelled hallucination corpus."
    )

    return {
        "phase": 17,
        "n_questions": N_QUESTIONS,
        "n_cases": 420,
        "threshold": LOCKED_T,
        "alpha": ALPHA,
        "judge_metric_label": JUDGE_METRIC_LABEL,
        "hashes": joined["hashes"],
        "source": {
            "processed": "results/processed/phase16_cases.jsonl",
            "judge": (
                "results/raw/phase16_judge/"
                "phase16_judge_20260828T152623Z_06661255/judge.jsonl"
            ),
            "phase15_sha_verified": True,
            "used_rag_rerun": False,
        },
        "descriptive": descriptive,
        "tests": rq1_conf + rq1_expl + rq2_conf + rq2_expl + rq3_conf + secondary_overlap,
        "rq1_confirmatory": rq1_conf,
        "rq1_exploratory": rq1_expl,
        "rq2_confirmatory": rq2_conf,
        "rq2_exploratory": rq2_expl,
        "rq3_confirmatory": rq3_conf,
        "secondary_token_overlap": secondary_overlap,
        "rq3_abstention_outcomes": {
            "n_answer": sum(uq_ans),
            "n_abstain": N_QUESTIONS - sum(uq_ans),
            "true_positive_answer_displayed_correct": n_true_answer,
            "false_positive_answer_displayed_incorrect": n_false_answer,
            "true_abstain_incorrect_draft": n_true_abstain,
            "false_abstain_correct_draft": n_false_abstain,
            "threshold": LOCKED_T,
        },
        "rq3_bootstrap": {
            "selective_minus_single_agent": sel_vs_sa,
            "selective_minus_multi_agent": sel_vs_ma,
        },
        "rq2_bootstrap_llm_ma_vs_uq": bootstrap_mean_diff(ma_llm, uq_llm),
        "assumptions": assumptions,
        "retrieval_control": {
            "context_precision_identical": ctx_identical,
            "note": retrieval_note,
            "mean_precision": descriptive[0]["context_precision"]["mean"],
            "mean_recall": descriptive[0]["context_recall"]["mean"],
        },
        "interpretation": interpretation,
        "series": {
            "question_ids": joined["question_ids"],
            "sa_disp": sa_disp,
            "ma_disp": ma_disp,
            "uq_disp": uq_disp,
            "uq_ans": uq_ans,
            "uq_conf": uq_conf,
            "sa_llm": sa_llm,
            "ma_llm": ma_llm,
            "uq_llm": uq_llm,
        },
    }
