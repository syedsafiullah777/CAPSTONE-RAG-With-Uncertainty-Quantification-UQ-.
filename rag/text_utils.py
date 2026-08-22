from __future__ import annotations

import re
from typing import Iterable


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def token_overlap(reference: str, candidate: str) -> float:
    reference_tokens = {t for t in re.findall(r"[a-zA-Z0-9]+", reference.lower()) if len(t) > 2}
    candidate_tokens = {t for t in re.findall(r"[a-zA-Z0-9]+", candidate.lower()) if len(t) > 2}
    if not reference_tokens or not candidate_tokens:
        return 0.0
    return len(reference_tokens & candidate_tokens) / max(1, len(reference_tokens))


def average(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def similarity_from_distance(distance: float | None) -> float:
    if distance is None:
        return 0.0
    return max(0.0, min(1.0, 1.0 / (1.0 + float(distance))))
