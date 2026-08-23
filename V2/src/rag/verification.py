"""Evidence-grounded verification for Multi-Agent RAG (Phase 9)."""

from __future__ import annotations

from typing import Any

from src.models.types import LLMBackend
from src.rag.prompts import build_multi_agent_verification_prompt, format_evidence
from src.rag.text_utils import average, parse_unit_score, token_overlap
from src.retrieval.retriever import RetrievedChunk


def compute_verification_result(
    question: str,
    answer: str,
    chunks: list[RetrievedChunk],
    llm: LLMBackend,
    *,
    prompts_cfg: dict[str, Any] | None = None,
    verification_threshold: float = 0.5,
    temperature: float = 0.0,
    max_new_tokens: int = 32,
) -> dict[str, Any]:
    """Lexical overlap + LLM support score (no abstention logic here)."""
    evidence_text = format_evidence(chunks)
    lexical_score = token_overlap(answer, evidence_text)
    llm_score: float | None = None

    if answer.strip():
        prompt = build_multi_agent_verification_prompt(
            question,
            answer,
            chunks,
            prompts_cfg=prompts_cfg,
        )
        gen = llm.generate(
            prompt,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
        )
        llm_score = parse_unit_score(gen.text or "")

    if llm_score is not None:
        verification_score = average([lexical_score, llm_score])
    else:
        verification_score = lexical_score

    status = "VERIFIED" if verification_score >= verification_threshold else "WEAK_EVIDENCE"
    return {
        "verification_score": verification_score,
        "lexical_score": lexical_score,
        "llm_score": llm_score,
        "verification_threshold": verification_threshold,
        "status": status,
    }
