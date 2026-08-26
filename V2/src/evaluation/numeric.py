"""Numeric match against FinQA ``program_answer`` (calibration / later metrics)."""

from __future__ import annotations

import math
import re

_NUMBER_RE = re.compile(
    r"(?<![A-Za-z])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s*%)?",
    re.IGNORECASE,
)


def parse_numbers(text: str | None) -> list[float]:
    """Extract numeric tokens. Values with % are stored as given and as /100."""
    if not text:
        return []
    values: list[float] = []
    for match in _NUMBER_RE.finditer(str(text)):
        raw = match.group(0).strip()
        percent = raw.endswith("%")
        cleaned = raw.replace(",", "").replace("%", "").strip()
        try:
            number = float(cleaned)
        except ValueError:
            continue
        values.append(number)
        if percent:
            values.append(number / 100.0)
        else:
            values.append(number / 100.0)
            values.append(number * 100.0)
    return values


def numeric_match(
    predicted: str | None,
    gold: str | None,
    *,
    rel_tol: float = 0.01,
    abs_tol: float = 1e-4,
) -> bool:
    """True if any number in ``predicted`` matches ``gold`` within tolerance."""
    if gold is None or str(gold).strip() == "":
        return False
    gold_values = parse_numbers(str(gold))
    if not gold_values:
        return False
    gold_number = gold_values[0]
    for predicted_number in parse_numbers(predicted):
        if math.isclose(predicted_number, gold_number, rel_tol=rel_tol, abs_tol=abs_tol):
            return True
    return False
