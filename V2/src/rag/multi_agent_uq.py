"""Multi-Agent RAG + UQ / abstention (Phase 10): retrieve → draft → verify → confidence gate.

Extends Phase 9 with combined confidence (retrieval + verification) and ANSWER | ABSTAIN.
No self-consistency sampling (avoid V1 cost/constant-confidence issue).
"""

from __future__ import annotations

import time
from typing import Any

from src.config import ExperimentConfig, get_path, load_experiment_config, load_prompts_config
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.models.types import LLMBackend
from src.rag.multi_agent import _generate_with_retry
from src.rag.prompts import build_multi_agent_draft_prompt, build_multi_agent_verification_prompt
from src.rag.schema import ARCHITECTURE_MULTI_AGENT_UQ, RAGCaseResult
from src.rag.text_utils import clean_generated_answer
from src.rag.uncertainty import (
    apply_abstention_decision,
    compute_combined_confidence,
    compute_retrieval_score,
)
from src.rag.verification import compute_verification_result
from src.retrieval.retriever import retrieve
from src.utils import create_run_id


def _resolve_threshold(cfg: ExperimentConfig, threshold_override: float | None) -> float:
    if threshold_override is not None:
        return float(threshold_override)
    uq_cfg = cfg.section("uncertainty")
    locked = uq_cfg.get("confidence_threshold")
    if locked is not None:
        return float(locked)
    smoke = uq_cfg.get("smoke_threshold")
    if smoke is not None:
        return float(smoke)
    return 0.55


def run_multi_agent_uq(
    question: str,
    *,
    question_id: str = "adhoc",
    reference_answer: str | None = None,
    config: ExperimentConfig | None = None,
    backend: LLMBackend | None = None,
    backend_name: str | None = None,
    run_id: str | None = None,
    fingerprint: dict[str, Any] | None = None,
    threshold: float | None = None,
) -> RAGCaseResult:
    """Run retrieve → draft → verify → combined confidence → abstention gate."""
    cfg = config or load_experiment_config()
    model_cfg = dict(cfg.section("model"))
    retrieval_cfg = cfg.section("retrieval")
    embeddings_cfg = cfg.section("embeddings")
    execution_cfg = cfg.section("execution")
    rag_cfg = cfg.section("rag")
    uq_cfg = cfg.section("uncertainty")
    multi_cfg = dict(rag_cfg.get("architectures", {}).get("multi_agent") or {})
    prompts_cfg = load_prompts_config()
    uq_prompts = dict(prompts_cfg.get("uncertainty") or {})

    if backend_name:
        model_cfg["backend"] = backend_name

    from src.config import project_root

    rid = run_id or create_run_id("phase10")
    architecture = ARCHITECTURE_MULTI_AGENT_UQ
    case_key = f"{architecture}:{question_id}"

    top_k = int(retrieval_cfg.get("top_k") or 4)
    persist_dir = get_path(cfg, "kb_index")
    embed_model = str(embeddings_cfg.get("model") or "BAAI/bge-small-en-v1.5")
    collection = str(retrieval_cfg.get("collection_name") or "finqa_source_pdfs")
    verify_threshold = float(multi_cfg.get("verification_threshold") or 0.5)
    confidence_threshold = _resolve_threshold(cfg, threshold)
    uq_method = str(uq_cfg.get("method") or "mean_retrieval_verification")
    abstention_message = str(
        uq_prompts.get("abstention_message")
        or uq_cfg.get("abstention_message")
        or "I cannot answer reliably because supporting evidence is insufficient."
    )
    temperature = float(model_cfg.get("temperature") or 0.1)
    max_new_tokens = int(model_cfg.get("max_new_tokens") or 512)
    top_p = model_cfg.get("top_p")

    fp = fingerprint or collect_fingerprint(
        model_config=model_cfg,
        project_root=str(project_root()),
    )

    llm = backend or create_backend(model_cfg)
    start = time.perf_counter()
    error: str | None = None
    draft_answer = ""
    final_answer = ""
    chunks_dicts: list[dict[str, Any]] = []
    scores: list[float] = []
    draft_prompt_chars = 0
    verify_prompt_chars = 0
    verification_result: dict[str, Any] | None = None
    uncertainty_result: dict[str, Any] | None = None
    decision = "ANSWER"
    confidence: float | None = None
    model_name = str(model_cfg.get("name") or "Qwen3-8B")
    quant: Any = model_cfg.get("quantisation")
    backend_used: Any = getattr(llm, "name", model_cfg.get("backend"))

    try:
        chunks = retrieve(
            question,
            persist_dir=persist_dir,
            top_k=top_k,
            embedding_model=embed_model,
            collection_name=collection,
        )
        chunks_dicts = [c.to_dict() for c in chunks]
        scores = [float(c.score) for c in chunks]

        draft_prompt = build_multi_agent_draft_prompt(question, chunks, prompts_cfg=prompts_cfg)
        draft_prompt_chars = len(draft_prompt)
        draft_gen = _generate_with_retry(
            llm,
            draft_prompt,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
        )
        draft_answer = clean_generated_answer(draft_gen.text or "")
        model_name = draft_gen.model
        quant = draft_gen.quantisation
        backend_used = draft_gen.backend

        if not draft_answer:
            error = "Draft generation returned empty text after retry"
        else:
            verify_prompt = build_multi_agent_verification_prompt(
                question,
                draft_answer,
                chunks,
                prompts_cfg=prompts_cfg,
            )
            verify_prompt_chars = len(verify_prompt)
            verification_result = compute_verification_result(
                question,
                draft_answer,
                chunks,
                llm,
                prompts_cfg=prompts_cfg,
                verification_threshold=verify_threshold,
            )
            retrieval_score = compute_retrieval_score(scores)
            verify_score = float(verification_result["verification_score"])
            uncertainty_result = compute_combined_confidence(
                retrieval_score,
                verify_score,
                method=uq_method,
            )
            confidence = float(uncertainty_result["confidence"])
            final_answer, decision = apply_abstention_decision(
                draft_answer=draft_answer,
                confidence=confidence,
                threshold=confidence_threshold,
                abstention_message=abstention_message,
            )
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"

    latency = time.perf_counter() - start
    gpu_info = (fp or {}).get("gpu") or {}
    gpu_name = gpu_info.get("name") if gpu_info.get("available") else None

    return RAGCaseResult(
        run_id=rid,
        question_id=str(question_id),
        architecture=architecture,
        question=question,
        retrieved_evidence=chunks_dicts,
        retrieval_scores=scores,
        answer=final_answer if not error else "",
        reference_answer=reference_answer,
        verification_result=verification_result,
        confidence=confidence,
        threshold=confidence_threshold,
        decision=decision,
        latency_seconds=latency,
        model=model_name,
        model_version=None,
        quantisation=str(quant) if quant is not None else None,
        device=(fp or {}).get("device"),
        gpu=gpu_name,
        configuration={
            "top_k": top_k,
            "embedding_model": embed_model,
            "collection_name": collection,
            "persist_dir": str(persist_dir),
            "hf_repo_id": model_cfg.get("hf_repo_id"),
            "gguf_filename": model_cfg.get("gguf_filename"),
            "temperature": temperature,
            "max_new_tokens": max_new_tokens,
            "verification_threshold": verify_threshold,
            "draft_prompt_chars": draft_prompt_chars,
            "verify_prompt_chars": verify_prompt_chars,
            "draft_answer": draft_answer or None,
            "uncertainty_result": uncertainty_result,
            "uq_method": uq_method,
            "threshold_source": (
                "override"
                if threshold is not None
                else ("locked" if uq_cfg.get("confidence_threshold") is not None else "smoke")
            ),
        },
        random_seed=execution_cfg.get("random_seed"),
        error=error,
        retrieval_top_k=top_k,
        backend=str(backend_used) if backend_used else None,
        prompt_chars=draft_prompt_chars,
        case_key=case_key,
    )
