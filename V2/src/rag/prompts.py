"""Prompt construction for V2 RAG architectures."""

from __future__ import annotations

from typing import Any

from src.config import load_prompts_config
from src.retrieval.retriever import RetrievedChunk


DEFAULT_BASELINE_SYSTEM = (
    "Answer the financial question using only the evidence below. "
    "Write the final answer once, in one short sentence or one number with its unit. "
    "Do not repeat the answer. Do not repeat these instructions. Do not write reasoning. "
    "Distinguish the quantity the question asks for: final/ending/cumulative value is not "
    "the same as absolute change, and neither is the same as percentage change or ROI. "
    "If the question asks for ROI or percentage change, do not report the ending investment value. "
    "If the evidence does not contain the answer, write exactly: Evidence is insufficient."
)

DEFAULT_BASELINE_USER = """Evidence:
{evidence}

Question:
{question}

Final answer (once only):"""

DEFAULT_MULTI_AGENT_DRAFT_SYSTEM = (
    "Draft a financial answer using only the evidence below. "
    "Write the final answer once, in one short sentence or one number with its unit. "
    "Do not repeat the answer. Do not repeat these instructions. Do not write reasoning. "
    "Distinguish the quantity the question asks for: final/ending/cumulative value is not "
    "the same as absolute change, and neither is the same as percentage change or ROI. "
    "If the question asks for ROI or percentage change, do not report the ending investment value. "
    "If the evidence does not contain the answer, write exactly: Evidence is insufficient."
)

DEFAULT_MULTI_AGENT_DRAFT_USER = """Evidence:
{evidence}

Question:
{question}

Final answer (once only):"""

DEFAULT_MULTI_AGENT_VERIFY_SYSTEM = (
    "Score how well the draft answer is supported by the evidence and "
    "whether it reports the quantity the question asked for "
    "(final value vs absolute change vs percentage change/ROI). "
    "Reply with only one number from 0.00 to 1.00. "
    "Do not repeat these instructions and do not write words before or after the number."
)

DEFAULT_MULTI_AGENT_VERIFY_USER = """Evidence:
{evidence}

Question:
{question}

Draft answer:
{answer}

Support score:"""


def format_evidence(chunks: list[RetrievedChunk] | list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        if isinstance(chunk, dict):
            text = str(chunk.get("text") or "")
            file_name = str(chunk.get("file_name") or "")
            score = chunk.get("score")
        else:
            text = chunk.text
            file_name = chunk.file_name
            score = chunk.score
        header = f"[{i}] file={file_name} score={score:.4f}" if score is not None else f"[{i}] file={file_name}"
        parts.append(f"{header}\n{text.strip()}")
    return "\n\n".join(parts) if parts else "(no evidence retrieved)"


def build_baseline_prompt(
    question: str,
    chunks: list[RetrievedChunk] | list[dict[str, Any]],
    *,
    prompts_cfg: dict[str, Any] | None = None,
) -> str:
    cfg = prompts_cfg if prompts_cfg is not None else load_prompts_config()
    baseline = cfg.get("baseline") or {}
    system = baseline.get("system") or DEFAULT_BASELINE_SYSTEM
    user_template = baseline.get("user_template") or DEFAULT_BASELINE_USER
    user = user_template.format(
        evidence=format_evidence(chunks),
        question=question.strip(),
    )
    return f"{system.strip()}\n\n{user.strip()}"


def build_multi_agent_draft_prompt(
    question: str,
    chunks: list[RetrievedChunk] | list[dict[str, Any]],
    *,
    prompts_cfg: dict[str, Any] | None = None,
) -> str:
    cfg = prompts_cfg if prompts_cfg is not None else load_prompts_config()
    section = (cfg.get("multi_agent") or {}).get("generation") or {}
    system = section.get("system") or DEFAULT_MULTI_AGENT_DRAFT_SYSTEM
    user_template = section.get("user_template") or DEFAULT_MULTI_AGENT_DRAFT_USER
    user = user_template.format(
        evidence=format_evidence(chunks),
        question=question.strip(),
    )
    return f"{system.strip()}\n\n{user.strip()}"


def build_multi_agent_verification_prompt(
    question: str,
    answer: str,
    chunks: list[RetrievedChunk] | list[dict[str, Any]],
    *,
    prompts_cfg: dict[str, Any] | None = None,
) -> str:
    cfg = prompts_cfg if prompts_cfg is not None else load_prompts_config()
    section = (cfg.get("multi_agent") or {}).get("verification") or {}
    system = section.get("system") or DEFAULT_MULTI_AGENT_VERIFY_SYSTEM
    user_template = section.get("user_template") or DEFAULT_MULTI_AGENT_VERIFY_USER
    user = user_template.format(
        evidence=format_evidence(chunks),
        question=question.strip(),
        answer=answer.strip(),
    )
    return f"{system.strip()}\n\n{user.strip()}"
