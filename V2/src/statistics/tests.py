"""Assumption-aware tests for Phase 17. No RAG / LLM imports."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy import stats

from src.statistics.constants import ALPHA, BOOTSTRAP_N, BOOTSTRAP_SEED


def _as_float_array(values: list[float] | np.ndarray) -> np.ndarray:
    return np.asarray(values, dtype=float)


def wilson_ci(k: int, n: int, alpha: float = ALPHA) -> dict[str, float | int | None]:
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return {"n": n, "k": k, "mean": None, "ci_low": None, "ci_high": None}
    p = k / n
    z = float(stats.norm.ppf(1 - alpha / 2))
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) / n) + z2 / (4 * n * n)) / denom
    return {
        "n": n,
        "k": k,
        "mean": p,
        "ci_low": max(0.0, centre - margin),
        "ci_high": min(1.0, centre + margin),
    }


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm–Bonferroni adjusted p-values, same order as input."""
    m = len(p_values)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        raw = p_values[idx]
        if math.isnan(raw):
            adjusted[idx] = float("nan")
            continue
        candidate = min(1.0, (m - rank) * raw)
        running = max(running, candidate)
        adjusted[idx] = running
    return adjusted


def mean_sd(values: list[float] | np.ndarray) -> dict[str, float | int | None]:
    arr = _as_float_array(values)
    n = int(arr.size)
    if n == 0:
        return {"n": 0, "mean": None, "sd": None}
    mean = float(arr.mean())
    sd = float(arr.std(ddof=1)) if n > 1 else None
    return {"n": n, "mean": mean, "sd": sd}


def t_ci_mean(values: list[float] | np.ndarray, alpha: float = ALPHA) -> dict[str, Any]:
    arr = _as_float_array(values)
    summary = mean_sd(arr)
    n = int(summary["n"] or 0)
    mean = summary["mean"]
    sd = summary["sd"]
    if n < 2 or mean is None or sd is None:
        return {**summary, "ci_low": None, "ci_high": None, "df": None}
    sem = sd / math.sqrt(n)
    df = n - 1
    tcrit = float(stats.t.ppf(1 - alpha / 2, df))
    return {
        **summary,
        "ci_low": mean - tcrit * sem,
        "ci_high": mean + tcrit * sem,
        "df": df,
    }


def shapiro_wilk(values: list[float] | np.ndarray) -> dict[str, Any]:
    arr = _as_float_array(values)
    arr = arr[np.isfinite(arr)]
    n = int(arr.size)
    if n < 3:
        return {"n": n, "statistic": None, "p_value": None, "normality_ok": False, "note": "n<3"}
    if np.unique(arr).size < 2:
        return {
            "n": n,
            "statistic": None,
            "p_value": None,
            "normality_ok": False,
            "note": "all values identical",
        }
    stat, p_value = stats.shapiro(arr)
    return {
        "n": n,
        "statistic": float(stat),
        "p_value": float(p_value),
        "normality_ok": bool(p_value >= ALPHA),
        "note": None,
    }


def cohen_dz(differences: list[float] | np.ndarray) -> float | None:
    arr = _as_float_array(differences)
    arr = arr[np.isfinite(arr)]
    if arr.size < 2:
        return None
    sd = float(arr.std(ddof=1))
    if sd == 0.0:
        return 0.0 if float(arr.mean()) == 0.0 else None
    return float(arr.mean() / sd)


def mcnemar_exact(left: list[int], right: list[int]) -> dict[str, Any]:
    """Exact McNemar test on paired binary outcomes (same questions).

    Table uses left/right correctness:
    n11 both 1, n10 left 1 right 0, n01 left 0 right 1, n00 both 0.
    """
    a = np.asarray(left, dtype=int)
    b = np.asarray(right, dtype=int)
    if a.size != b.size:
        raise ValueError("McNemar requires equal-length paired series")
    n = int(a.size)
    n11 = int(np.sum((a == 1) & (b == 1)))
    n10 = int(np.sum((a == 1) & (b == 0)))
    n01 = int(np.sum((a == 0) & (b == 1)))
    n00 = int(np.sum((a == 0) & (b == 0)))
    discordant = n10 + n01
    if discordant == 0:
        exact_p = 1.0
        chi2 = 0.0
        chi2_p = 1.0
    else:
        exact_p = float(stats.binomtest(n01, n=discordant, p=0.5, alternative="two-sided").pvalue)
        chi2 = (abs(n01 - n10) - 1) ** 2 / discordant
        chi2_p = float(stats.chi2.sf(chi2, 1))
    odds_num = n01 + 0.5
    odds_den = n10 + 0.5
    odds_ratio = odds_num / odds_den
    cohen_g = (n01 / discordant - 0.5) if discordant else 0.0
    mean_left = n11 / n + n10 / n
    mean_right = n11 / n + n01 / n
    return {
        "n": n,
        "n11_both_positive": n11,
        "n10_left_only": n10,
        "n01_right_only": n01,
        "n00_both_negative": n00,
        "n_discordant": discordant,
        "mean_left": mean_left,
        "mean_right": mean_right,
        "mean_difference": mean_right - mean_left,
        "test": "McNemar exact (binomial, two-sided)",
        "statistic": n01,
        "statistic_name": "n01 (right-only positives among discordant pairs)",
        "df": None,
        "p_value": exact_p,
        "chi2_continuity": chi2,
        "chi2_p_value": chi2_p,
        "effect_odds_ratio_haldane": odds_ratio,
        "effect_cohens_g": cohen_g,
        "ci_left": wilson_ci(n11 + n10, n),
        "ci_right": wilson_ci(n11 + n01, n),
    }


def wilcoxon_paired(left: list[float], right: list[float]) -> dict[str, Any]:
    """Wilcoxon signed-rank on paired continuous scores; Shapiro on differences."""
    a = _as_float_array(left)
    b = _as_float_array(right)
    if a.size != b.size:
        raise ValueError("Wilcoxon requires equal-length paired series")
    diff = b - a
    n = int(diff.size)
    n_nonzero = int(np.sum(diff != 0))
    shapiro = shapiro_wilk(diff)
    t_res = stats.ttest_rel(b, a, nan_policy="omit")
    try:
        w_res = stats.wilcoxon(b, a, zero_method="wilcox", alternative="two-sided", method="auto")
        w_stat = float(w_res.statistic)
        w_p = float(w_res.pvalue)
        w_note = None
    except ValueError as exc:
        w_stat, w_p = None, 1.0 if n_nonzero == 0 else None
        w_note = str(exc)
    selected = "Wilcoxon signed-rank"
    if shapiro.get("normality_ok") and n_nonzero >= 3:
        selected = "paired t-test (Shapiro p≥0.05); Wilcoxon also reported"
    dz = cohen_dz(diff)
    z = None
    rank_biserial = None
    if n_nonzero >= 1 and w_stat is not None:
        mean_w = n_nonzero * (n_nonzero + 1) / 4.0
        var_w = n_nonzero * (n_nonzero + 1) * (2 * n_nonzero + 1) / 24.0
        if var_w > 0:
            z = (float(w_stat) - mean_w) / math.sqrt(var_w)
            rank_biserial = z / math.sqrt(n_nonzero)
    t_ci = t_ci_mean(diff)
    return {
        "n": n,
        "n_nonzero_differences": n_nonzero,
        "mean_left": float(a.mean()) if n else None,
        "mean_right": float(b.mean()) if n else None,
        "mean_difference": float(diff.mean()) if n else None,
        "sd_difference": float(diff.std(ddof=1)) if n > 1 else None,
        "ci95_diff_low": t_ci["ci_low"],
        "ci95_diff_high": t_ci["ci_high"],
        "test": "Wilcoxon signed-rank (two-sided, zeros discarded)",
        "selected_test": selected,
        "statistic": w_stat,
        "statistic_name": "Wilcoxon W",
        "df": None,
        "p_value": w_p,
        "t_statistic": float(t_res.statistic) if t_res.statistic is not None else None,
        "t_df": int(n - 1) if n > 1 else None,
        "t_p_value": float(t_res.pvalue) if t_res.pvalue is not None else None,
        "shapiro": shapiro,
        "effect_cohens_dz": dz,
        "effect_rank_biserial_approx": rank_biserial,
        "z_approx": z,
        "note": w_note,
    }


def spearman_corr(x: list[float], y: list[float]) -> dict[str, Any]:
    a = _as_float_array(x)
    b = _as_float_array(y)
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    n = int(a.size)
    if n < 3 or np.unique(a).size < 2 or np.unique(b).size < 2:
        return {
            "n": n,
            "test": "Spearman rank correlation (two-sided)",
            "statistic": None,
            "statistic_name": "rho",
            "df": None,
            "p_value": None,
            "note": "insufficient variation or n<3",
        }
    rho, p_value = stats.spearmanr(a, b)
    return {
        "n": n,
        "test": "Spearman rank correlation (two-sided)",
        "statistic": float(rho),
        "statistic_name": "rho",
        "df": n - 2,
        "p_value": float(p_value),
        "mean_x": float(a.mean()),
        "mean_y": float(b.mean()),
        "sd_x": float(a.std(ddof=1)),
        "sd_y": float(b.std(ddof=1)),
        "note": None,
    }


def mannwhitney(left: list[float], right: list[float], label_left: str, label_right: str) -> dict[str, Any]:
    a = _as_float_array(left)
    b = _as_float_array(right)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    n1, n2 = int(a.size), int(b.size)
    if n1 < 1 or n2 < 1:
        return {
            "n_left": n1,
            "n_right": n2,
            "test": "Mann–Whitney U (two-sided, unpaired)",
            "statistic": None,
            "p_value": None,
            "note": "empty group",
        }
    res = stats.mannwhitneyu(a, b, alternative="two-sided")
    # rank-biserial: r = 1 - 2U/(n1 n2)
    r_rb = (2.0 * float(res.statistic)) / (n1 * n2) - 1.0
    return {
        "n_left": n1,
        "n_right": n2,
        "label_left": label_left,
        "label_right": label_right,
        "mean_left": float(a.mean()),
        "mean_right": float(b.mean()),
        "sd_left": float(a.std(ddof=1)) if n1 > 1 else None,
        "sd_right": float(b.std(ddof=1)) if n2 > 1 else None,
        "test": "Mann–Whitney U (two-sided, unpaired)",
        "statistic": float(res.statistic),
        "statistic_name": "U",
        "df": None,
        "p_value": float(res.pvalue),
        "effect_rank_biserial": r_rb,
        "note": "Groups are disjoint questions (ANSWER vs ABSTAIN), not paired.",
    }


def bootstrap_mean_diff(
    left: list[float],
    right: list[float],
    n_boot: int = BOOTSTRAP_N,
    seed: int = BOOTSTRAP_SEED,
    alpha: float = ALPHA,
) -> dict[str, Any]:
    """Paired bootstrap percentile CI for mean(right-left)."""
    a = _as_float_array(left)
    b = _as_float_array(right)
    n = int(a.size)
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        diffs[i] = float((b[idx] - a[idx]).mean())
    lo, hi = np.quantile(diffs, [alpha / 2, 1 - alpha / 2])
    observed = float((b - a).mean())
    return {
        "n": n,
        "n_boot": n_boot,
        "seed": seed,
        "observed_mean_difference": observed,
        "ci_low": float(lo),
        "ci_high": float(hi),
    }


def bootstrap_selective_minus_baseline(
    uq_answered: list[int],
    uq_correct_displayed: list[int],
    baseline_correct: list[int],
    n_boot: int = BOOTSTRAP_N,
    seed: int = BOOTSTRAP_SEED,
    alpha: float = ALPHA,
) -> dict[str, Any]:
    """Bootstrap CI for UQ selective accuracy minus baseline accuracy (question resampling)."""
    ans = np.asarray(uq_answered, dtype=int)
    corr = np.asarray(uq_correct_displayed, dtype=int)
    base = np.asarray(baseline_correct, dtype=int)
    n = int(ans.size)
    rng = np.random.default_rng(seed)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        n_ans = int(ans[idx].sum())
        if n_ans == 0:
            continue
        sel = float(corr[idx][ans[idx] == 1].sum() / n_ans)
        acc = float(base[idx].mean())
        deltas.append(sel - acc)
    arr = np.asarray(deltas, dtype=float)
    n_ans_obs = int(ans.sum())
    sel_obs = float(corr[ans == 1].sum() / n_ans_obs) if n_ans_obs else None
    acc_obs = float(base.mean())
    lo, hi = np.quantile(arr, [alpha / 2, 1 - alpha / 2]) if arr.size else (None, None)
    return {
        "n": n,
        "n_boot": int(arr.size),
        "seed": seed,
        "selective_accuracy": sel_obs,
        "baseline_accuracy": acc_obs,
        "observed_difference": (sel_obs - acc_obs) if sel_obs is not None else None,
        "ci_low": float(lo) if lo is not None else None,
        "ci_high": float(hi) if hi is not None else None,
        "note": (
            "Question-level bootstrap. Selective accuracy uses the ANSWER subset; "
            "this is not a paired McNemar on all 140 questions."
        ),
    }


def significant(p_adjusted: float | None, alpha: float = ALPHA) -> bool:
    if p_adjusted is None or (isinstance(p_adjusted, float) and math.isnan(p_adjusted)):
        return False
    return bool(p_adjusted < alpha)
