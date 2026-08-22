"""Prompt construction for V2 RAG architectures."""

from __future__ import annotations

from typing import Any

from src.config import load_prompts_config
from src.retrieval.retriever import RetrievedChunk


DEFAULT_BASELINE_SYSTEM = (
    "You are answering questions about financial documents. "
    "Use only the provided evidence. If the evidence is insufficient, say so clearly. "
    "Give a concise final answer."
)

DEFAULT_BASELINE_USER = """Evidence:
{evidence}

Question:
{question}

Answer:"""


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
