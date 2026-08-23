"""Lightweight text helpers for verification scoring."""

from __future__ import annotations

import re
from typing import Iterable


def token_overlap(reference: str, candidate: str) -> float:
    reference_tokens = {t for t in re.findall(r"[a-zA-Z0-9]+", reference.lower()) if len(t) > 2}
    candidate_tokens = {t for t in re.findall(r"[a-zA-Z0-9]+", candidate.lower()) if len(t) > 2}
    if not reference_tokens or not candidate_tokens:
        return 0.0
    return len(reference_tokens & candidate_tokens) / max(1, len(reference_tokens))


def average(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def parse_unit_score(text: str) -> float | None:
    """Extract a 0–1 score from model output."""
    raw = (text or "").strip()
    if not raw:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", raw)
    if not match:
        return None
    try:
        value = float(match.group(1))
    except ValueError:
        return None
    if value > 1.0 and value <= 100.0:
        value = value / 100.0
    return max(0.0, min(1.0, value))
