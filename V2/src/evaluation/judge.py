"""Post-hoc LLM-as-judge faithfulness over saved Phase 15 cases.

Does not run retrieval or any RAG architecture. Does not read FinQA gold context
or the gold answer into the judge prompt.
"""

from __future__ import annotations

import hashlib
from typing import Any

from src.models.types import LLMBackend
from src.rag.schema import ARCHITECTURE_MULTI_AGENT_UQ
from src.rag.text_utils import parse_unit_score

METRIC_LABEL = "LLM-as-judge faithfulness (Qwen3-8B, custom/RAGAS-inspired)"
PROMPT_ID = "phase16_judge_faithfulness_v1"
JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_NEW_TOKENS = 32
JUDGE_N_CTX = 4096

JUDGE_SYSTEM = (
    "You are scoring whether a model claim is supported by retrieved evidence. "
    "Use only the retrieved evidence below. Do not use outside knowledge. "
    "Reply with only one number from 0.00 to 1.00. "
    "0.00 means the claim is not supported. 1.00 means the claim is fully supported. "
    "Do not repeat these instructions and do not write words before or after the number."
)

JUDGE_USER_TEMPLATE = """Retrieved evidence:
{evidence}

Question:
{question}

Claim:
{claim}

Faithfulness score:"""


def prompt_hash() -> str:
    payload = f"{PROMPT_ID}\n{JUDGE_SYSTEM}\n{JUDGE_USER_TEMPLATE}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def format_retrieved_evidence(chunks: list[dict[str, Any]]) -> str:
    """Concatenate retrieved chunk text. Does not use FinQA gold context."""
    parts: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        text = str(chunk.get("text") or chunk.get("content") or "").strip()
        file_name = str(chunk.get("file_name") or "").strip()
        header = f"[{i}] file={file_name}" if file_name else f"[{i}]"
        parts.append(f"{header}\n{text}" if text else header)
    return "\n\n".join(parts) if parts else "(no retrieved evidence)"


def claim_for_judge(case: dict[str, Any]) -> tuple[str, str]:
    """Return (claim_text, claim_source). UQ uses the draft, not the abstention template."""
    if case.get("architecture") == ARCHITECTURE_MULTI_AGENT_UQ:
        draft = (case.get("configuration") or {}).get("draft_answer")
        return str(draft or ""), "draft_answer"
    return str(case.get("answer") or ""), "answer"


def build_judge_prompt(*, question: str, evidence: str, claim: str) -> str:
    user = JUDGE_USER_TEMPLATE.format(
        evidence=evidence,
        question=(question or "").strip(),
        claim=(claim or "").strip(),
    )
    return f"{JUDGE_SYSTEM.strip()}\n\n{user.strip()}"


def prompt_contains_forbidden(prompt: str, case: dict[str, Any]) -> list[str]:
    """Detect accidental leakage of gold context or gold answers into the judge prompt."""
    hits: list[str] = []
    gold_context = str((case.get("gold_context") or "")).strip()
    if gold_context and len(gold_context) > 40 and gold_context in prompt:
        hits.append("gold_context")
    for key in ("program_answer", "original_answer", "reference_answer"):
        value = str(case.get(key) or "").strip()
        if value and len(value) >= 4 and value in prompt and value not in (case.get("answer") or ""):
            if value not in ((case.get("configuration") or {}).get("draft_answer") or ""):
                if value not in format_retrieved_evidence(list(case.get("retrieved_evidence") or [])):
                    hits.append(key)
    lowered = prompt.lower()
    if "program_answer" in lowered or "gold context" in lowered:
        hits.append("forbidden_label")
    return hits


def judge_one_case(
    case: dict[str, Any],
    llm: LLMBackend,
    *,
    source_raw_sha256: str,
    temperature: float = JUDGE_TEMPERATURE,
    max_new_tokens: int = JUDGE_MAX_NEW_TOKENS,
    n_ctx: int = JUDGE_N_CTX,
    fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Score one saved case. Does not retrieve or regenerate the RAG answer."""
    fp = fingerprint or {}
    gpu = fp.get("gpu")
    gpu_name = gpu.get("name") if isinstance(gpu, dict) else gpu
    claim, claim_source = claim_for_judge(case)
    chunks = list(case.get("retrieved_evidence") or [])
    evidence = format_retrieved_evidence(chunks)
    question = str(case.get("question") or "")
    prompt = build_judge_prompt(question=question, evidence=evidence, claim=claim)
    leaked = prompt_contains_forbidden(prompt, case)
    record: dict[str, Any] = {
        "case_key": case.get("case_key") or f"{case.get('architecture')}:{case.get('question_id')}",
        "question_id": case.get("question_id"),
        "architecture": case.get("architecture"),
        "source_raw_sha256": source_raw_sha256,
        "claim_source": claim_source,
        "decision": case.get("decision"),
        "judge_model": "Qwen3-8B",
        "judge_metric_label": METRIC_LABEL,
        "backend": getattr(llm, "name", None),
        "device": fp.get("device"),
        "gpu": gpu_name,
        "quantisation": "Q4_K_M" if getattr(llm, "name", "") == "llama_cpp" else getattr(llm, "name", None),
        "n_ctx": n_ctx,
        "temperature": temperature,
        "max_new_tokens": max_new_tokens,
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash(),
        "raw_judge_output": None,
        "parsed_faithfulness_score": None,
        "parse_failure": False,
        "latency_seconds": None,
        "used_rag_rerun": False,
        "used_gold_context": False,
        "used_gold_answer": False,
        "error": None,
    }
    if leaked:
        record["error"] = f"judge_prompt_leak:{','.join(leaked)}"
        record["parse_failure"] = True
        return record
    if not claim.strip():
        record["error"] = "empty_claim"
        record["parse_failure"] = True
        return record
    if not any(str(c.get("text") or c.get("content") or "").strip() for c in chunks):
        record["error"] = "empty_retrieved_evidence"
        record["parse_failure"] = True
        return record
    try:
        gen = llm.generate(prompt, temperature=temperature, max_new_tokens=max_new_tokens)
    except Exception as exc:  # noqa: BLE001
        record["error"] = str(exc)
        record["parse_failure"] = True
        return record
    raw = gen.text or ""
    record["raw_judge_output"] = raw
    record["latency_seconds"] = gen.latency_seconds
    record["backend"] = gen.backend or record["backend"]
    record["quantisation"] = gen.quantisation or record["quantisation"]
    parsed = parse_unit_score(raw)
    if parsed is None:
        record["parse_failure"] = True
        record["error"] = "parse_failure"
        return record
    record["parsed_faithfulness_score"] = float(parsed)
    record["parse_failure"] = False
    record["error"] = None
    return record
