"""Reproducible stratified sample of representative cases. Seed = 18."""

from __future__ import annotations

import random
from typing import Any

from src.error_analysis.constants import ARCH_MA, ARCH_SA, ARCH_UQ, SAMPLE_SEED


def _ids(cases: list[dict[str, Any]], pred) -> list[str]:
    return sorted({c["question_id"] for c in cases if pred(c)})


def _keys(cases: list[dict[str, Any]], pred) -> list[str]:
    return sorted(c["case_key"] for c in cases if pred(c))


def _take(values: list[str], k: int, rng: random.Random) -> list[str]:
    values = list(values)
    if len(values) <= k:
        return values
    return sorted(rng.sample(values, k))


def _add(selected: dict[str, list[str]], keys: list[str], stratum: str) -> None:
    for key in keys:
        bucket = selected.setdefault(key, [])
        if stratum not in bucket:
            bucket.append(stratum)


def _expand_questions(by_key: dict[str, dict[str, Any]], qids: list[str], arches: tuple[str, ...]) -> list[str]:
    keys = []
    for qid in qids:
        for arch in arches:
            key = f"{arch}:{qid}"
            if key in by_key:
                keys.append(key)
    return keys


def select_sample(universe: dict[str, Any], seed: int = SAMPLE_SEED) -> dict[str, Any]:
    """Stratified sample. Rare events are taken in full; remaining strata are sampled."""
    rng = random.Random(seed)
    cases = universe["cases"]
    by_key = universe["by_key"]
    selected: dict[str, list[str]] = {}
    notes: list[str] = []

    def add_q(qids: list[str], stratum: str, arches: tuple[str, ...] = (ARCH_SA, ARCH_MA, ARCH_UQ)) -> None:
        _add(selected, _expand_questions(by_key, qids, arches), stratum)

    def add_k(keys: list[str], stratum: str) -> None:
        _add(selected, keys, stratum)

    false_abs_q = _ids(cases, lambda c: c["architecture"] == ARCH_UQ and (not c["answered"]) and c["claim_correct"] == 1)
    add_q(false_abs_q, "census_false_abstention")
    notes.append(f"census_false_abstention questions={len(false_abs_q)} (all included)")

    sa_only_q = _ids(
        cases,
        lambda c: c["architecture"] == ARCH_SA and c["displayed_correct"] == 1,
    )
    ma_correct_q = set(_ids(cases, lambda c: c["architecture"] == ARCH_MA and c["displayed_correct"] == 1))
    sa_only = [q for q in sa_only_q if q not in ma_correct_q]
    ma_only_q = _ids(cases, lambda c: c["architecture"] == ARCH_MA and c["displayed_correct"] == 1)
    sa_correct_q = set(_ids(cases, lambda c: c["architecture"] == ARCH_SA and c["displayed_correct"] == 1))
    ma_only = [q for q in ma_only_q if q not in sa_correct_q]
    add_q(_take(sa_only, 3, rng), "rq1_discordant_sa_only")
    add_q(_take(ma_only, 3, rng), "rq1_discordant_ma_only")

    both_correct = [q for q in sa_only_q if q in ma_correct_q]
    add_q(_take(both_correct, 3, rng), "paired_both_correct")

    recall0 = _ids(cases, lambda c: c["architecture"] == ARCH_SA and c["context_recall"] == 0.0)
    add_q(_take(recall0, 4, rng), "retrieval_miss_questions")

    gold_in_ev_wrong_sa = _ids(
        cases,
        lambda c: c["architecture"] == ARCH_SA
        and c["displayed_correct"] == 0
        and c["context_recall_numeric"] == 1,
    )
    add_q(_take(gold_in_ev_wrong_sa, 3, rng), "gold_number_in_evidence_but_wrong")

    add_k(_take(_keys(cases, lambda c: c["architecture"] == ARCH_SA and c["displayed_correct"] == 1), 4, rng), "sa_correct")
    add_k(_take(_keys(cases, lambda c: c["architecture"] == ARCH_MA and c["displayed_correct"] == 1), 4, rng), "ma_correct")
    add_k(
        _take(_keys(cases, lambda c: c["architecture"] == ARCH_UQ and c["answered"] and c["displayed_correct"] == 1), 4, rng),
        "uq_answer_correct",
    )

    add_k(
        _take(
            _keys(
                cases,
                lambda c: c["architecture"] == ARCH_SA
                and c["answered"]
                and c["displayed_correct"] == 0
                and c["context_recall"] == 0.0,
            ),
            3,
            rng,
        ),
        "sa_incorrect_retrieval",
    )
    add_k(
        _take(
            _keys(
                cases,
                lambda c: c["architecture"] == ARCH_SA
                and c["answered"]
                and c["displayed_correct"] == 0
                and c["context_recall"] == 1.0
                and c["context_recall_numeric"] == 0,
            ),
            3,
            rng,
        ),
        "sa_incorrect_partial_evidence",
    )
    add_k(
        _take(
            _keys(
                cases,
                lambda c: c["architecture"] == ARCH_MA
                and c["answered"]
                and c["displayed_correct"] == 0
                and c["verification_status"] == "VERIFIED"
                and c.get("confidence") is not None
                and float(c["confidence"]) >= 0.65,
            ),
            4,
            rng,
        ),
        "ma_high_conf_verified_error",
    )
    add_k(
        _take(
            _keys(
                cases,
                lambda c: c["architecture"] == ARCH_UQ and c["answered"] and c["displayed_correct"] == 0,
            ),
            4,
            rng,
        ),
        "uq_answer_incorrect",
    )
    add_k(
        _take(
            _keys(
                cases,
                lambda c: c["architecture"] == ARCH_UQ
                and (not c["answered"])
                and c["claim_correct"] == 0
                and c.get("confidence") is not None
                and float(c["confidence"]) < 0.50,
            ),
            3,
            rng,
        ),
        "uq_low_conf_true_abstain",
    )
    add_k(
        _take(
            _keys(
                cases,
                lambda c: c["architecture"] == ARCH_UQ
                and (not c["answered"])
                and c["claim_correct"] == 0
                and c.get("confidence") is not None
                and 0.50 <= float(c["confidence"]) < 0.65,
            ),
            3,
            rng,
        ),
        "uq_near_threshold_true_abstain",
    )

    sample_cases = [by_key[k] for k in sorted(selected)]
    return {
        "seed": seed,
        "n_cases": len(sample_cases),
        "n_questions": len({c["question_id"] for c in sample_cases}),
        "strata_by_case": selected,
        "case_keys": sorted(selected),
        "notes": notes,
        "method": (
            "Stratified sample with random.Random(18). "
            "Both false-abstention questions are included in full (all three architectures). "
            "Other strata sample without replacement after sorting IDs. "
            "A case may belong to more than one stratum."
        ),
    }
