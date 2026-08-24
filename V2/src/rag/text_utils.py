"""Lightweight text helpers for verification scoring and generation cleanup."""

from __future__ import annotations

import re
from typing import Iterable

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
_INSTRUCTION_ECHO = re.compile(
    r"between\s+0(?:\.0+)?\s+and\s+1(?:\.0+)?|\b0\s*(?:to|-|/)\s*1\b",
    re.IGNORECASE,
)
_PROMPT_CHARS_SUFFIX = re.compile(r"\s*\|\s*prompt_chars=\d+\s*$")
_ECHO_LINE = re.compile(
    r"^(you are (answering|a financial)|use only the provided|give a concise|"
    r"do not repeat|if the evidence|cite the most|write only the|"
    r"return only|reply with only).*$",
    re.IGNORECASE,
)


def _normalize_span(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()).rstrip(" .;:")


def collapse_repeated_answers(text: str) -> str:
    """Keep one copy when the model repeats the same answer sentence or line."""
    if not (text or "").strip():
        return ""
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", text.strip()) if p.strip()]
    unique: list[str] = []
    seen: set[str] = set()
    for part in parts:
        key = _normalize_span(part)
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(part)
    return " ".join(unique).strip()


def clean_generated_answer(text: str) -> str:
    """Strip thinking blocks, instruction echo, and repeated answers.

    Does not change RAG architecture or retrieval.
    """
    cleaned = _THINK_BLOCK.sub(" ", text or "")
    cleaned = _PROMPT_CHARS_SUFFIX.sub("", cleaned)
    lines = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if not stripped:
            if lines:
                lines.append("")
            continue
        if _ECHO_LINE.match(stripped):
            continue
        if stripped.lower() in {"answer:", "draft answer:", "final answer:", "support score:"}:
            continue
        for prefix in ("final answer:", "draft answer:", "answer:"):
            if stripped.lower().startswith(prefix):
                stripped = stripped[len(prefix) :].strip()
                break
        if stripped:
            lines.append(stripped)
    return collapse_repeated_answers("\n".join(lines).strip())


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
    """Extract a 0–1 score from model output.

    Ignores instruction echoes such as "between 0 and 1" so a repeated
    prompt cannot become a contradictory 0.0 support score.
    """
    raw = clean_generated_answer(text or "")
    if not raw:
        return None
    cleaned = _INSTRUCTION_ECHO.sub(" ", raw)
    decimals = [float(m) for m in re.findall(r"\b(0\.\d+|1\.0+|1)\b", cleaned)]
    if decimals:
        value = decimals[-1]
        return max(0.0, min(1.0, value))
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    if not match:
        return None
    try:
        value = float(match.group(1))
    except ValueError:
        return None
    if value > 1.0 and value <= 100.0:
        value = value / 100.0
    if value in {0.0, 1.0} and _INSTRUCTION_ECHO.search(raw):
        return None
    return max(0.0, min(1.0, value))


def build_verification_rationale(
    *,
    status: str,
    verification_score: float,
    lexical_score: float,
    llm_score: float | None,
    verification_threshold: float,
) -> str:
    """Status and rationale are derived from the same scores (no free-text contradiction)."""
    llm_part = "n/a" if llm_score is None else f"{llm_score:.4f}"
    if status == "VERIFIED":
        return (
            f"VERIFIED: combined verification score {verification_score:.4f} "
            f"meets the informational threshold {verification_threshold:.2f} "
            f"(lexical={lexical_score:.4f}, llm={llm_part}). "
            f"This status describes evidence support only; it does not rewrite the draft answer."
        )
    return (
        f"WEAK_EVIDENCE: combined verification score {verification_score:.4f} "
        f"is below the informational threshold {verification_threshold:.2f} "
        f"(lexical={lexical_score:.4f}, llm={llm_part}). "
        f"This status describes evidence support only; it does not rewrite the draft answer."
    )
