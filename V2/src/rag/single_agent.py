"""Single-Agent RAG baseline (Phase 8).

Retrieve from the Phase 6 source-PDF knowledge base, then generate with the
configured Qwen3-8B backend. No multi-agent verification or abstention.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from src.config import ExperimentConfig, get_path, load_experiment_config, load_prompts_config
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.models.types import LLMBackend
from src.rag.prompts import build_baseline_prompt
from src.rag.schema import ARCHITECTURE_SINGLE_AGENT, RAGCaseResult
from src.rag.text_utils import clean_generated_answer
from src.retrieval.retriever import retrieve
from src.utils import create_run_id


def run_single_agent(
    question: str,
    *,
    question_id: str = "adhoc",
    reference_answer: str | None = None,
    config: ExperimentConfig | None = None,
    backend: LLMBackend | None = None,
    backend_name: str | None = None,
    run_id: str | None = None,
    fingerprint: dict[str, Any] | None = None,
) -> RAGCaseResult:
    """Run retrieve → prompt → generate for one question."""
    cfg = config or load_experiment_config()
    model_cfg = dict(cfg.section("model"))
    retrieval_cfg = cfg.section("retrieval")
    embeddings_cfg = cfg.section("embeddings")
    execution_cfg = cfg.section("execution")

    if backend_name:
        model_cfg["backend"] = backend_name

    from src.config import project_root

    rid = run_id or create_run_id("phase8")
    architecture = ARCHITECTURE_SINGLE_AGENT
    case_key = f"{architecture}:{question_id}"

    top_k = int(retrieval_cfg.get("top_k") or 4)
    persist_dir = get_path(cfg, "kb_index")
    embed_model = str(embeddings_cfg.get("model") or "BAAI/bge-small-en-v1.5")
    collection = str(retrieval_cfg.get("collection_name") or "finqa_source_pdfs")

    fp = fingerprint or collect_fingerprint(
        model_config=model_cfg,
        project_root=str(project_root()),
    )

    llm = backend or create_backend(model_cfg)
    start = time.perf_counter()
    error: str | None = None
    answer = ""
    chunks_dicts: list[dict[str, Any]] = []
    scores: list[float] = []
    prompt_chars = 0

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
        prompts_cfg = load_prompts_config()
        prompt = build_baseline_prompt(question, chunks, prompts_cfg=prompts_cfg)
        prompt_chars = len(prompt)
        gen = llm.generate(
            prompt,
            temperature=float(model_cfg.get("temperature") or 0.1),
            max_new_tokens=int(model_cfg.get("max_new_tokens") or 512),
            top_p=model_cfg.get("top_p"),
        )
        answer = clean_generated_answer(gen.text or "")
        # One retry if the backend returns empty text (seen with some local Ollama/Qwen3 runs).
        if not answer:
            gen = llm.generate(
                prompt,
                temperature=float(model_cfg.get("temperature") or 0.1),
                max_new_tokens=int(model_cfg.get("max_new_tokens") or 512),
                top_p=model_cfg.get("top_p"),
            )
            answer = clean_generated_answer(gen.text or "")
        model_name = gen.model
        quant = gen.quantisation
        backend_used = gen.backend
        if not answer:
            error = "Generation returned empty text after retry"
    except Exception as exc:  # noqa: BLE001 — capture into result record
        error = f"{type(exc).__name__}: {exc}"
        model_name = str(model_cfg.get("name") or "Qwen3-8B")
        quant = model_cfg.get("quantisation")
        backend_used = getattr(llm, "name", model_cfg.get("backend"))

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
        answer=answer,
        reference_answer=reference_answer,
        verification_result=None,
        confidence=None,
        threshold=None,
        decision="ANSWER",
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
            "temperature": model_cfg.get("temperature"),
            "max_new_tokens": model_cfg.get("max_new_tokens"),
        },
        random_seed=execution_cfg.get("random_seed"),
        error=error,
        retrieval_top_k=top_k,
        backend=str(backend_used) if backend_used else None,
        prompt_chars=prompt_chars,
        case_key=case_key,
    )
