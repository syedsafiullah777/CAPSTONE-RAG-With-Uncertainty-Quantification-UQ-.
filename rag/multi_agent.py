from __future__ import annotations

import time

from config import ANSWER_THRESHOLD, WARNING_THRESHOLD
from models.ollama import generate
from rag.retriever import format_context, retrieve
from rag.schema import RAGResult
from rag.uncertainty import combined_confidence, self_consistency_score, verification_score


def _draft_answer(question: str, chunks) -> str:
    prompt = f"""
You are an enterprise knowledge assistant.
Answer using only the evidence. Cite the most relevant source and page.
If the evidence is insufficient, say so clearly.

Evidence:
{format_context(chunks)}

Question:
{question}

Answer:
""".strip()
    return generate(prompt, temperature=0.1)


def answer_verified(question: str) -> RAGResult:
    start = time.perf_counter()
    chunks, retrieval_score = retrieve(question)
    response = _draft_answer(question, chunks)
    verification = verification_score(response, chunks)
    decision = "Verified" if verification >= 0.5 else "Weak evidence"
    return RAGResult(
        system_name="Multi-Agent RAG",
        answer=response,
        confidence=verification,
        decision=decision,
        retrieved_chunks=chunks,
        response_time=time.perf_counter() - start,
        retrieval_score=retrieval_score,
        verification_score=verification,
        hallucination_risk="Lower" if verification >= 0.5 else "High",
    )


def answer_with_uncertainty(question: str) -> RAGResult:
    start = time.perf_counter()
    chunks, retrieval_score = retrieve(question)
    response = _draft_answer(question, chunks)
    verification = verification_score(response, chunks)
    consistency = self_consistency_score(question, chunks)
    confidence = combined_confidence(retrieval_score, verification, consistency)

    if confidence >= ANSWER_THRESHOLD:
        decision = "Answer"
        final_answer = response
    elif confidence >= WARNING_THRESHOLD:
        decision = "Answer with warning"
        final_answer = "Warning: confidence is moderate, so check the cited policy. " + response
    else:
        decision = "Abstain"
        final_answer = "I cannot answer reliably because insufficient supporting evidence was found."

    return RAGResult(
        system_name="Multi-Agent RAG + UQ",
        answer=final_answer,
        confidence=confidence,
        decision=decision,
        retrieved_chunks=chunks,
        response_time=time.perf_counter() - start,
        retrieval_score=retrieval_score,
        verification_score=verification,
        consistency_score=consistency,
        hallucination_risk="Controlled by abstention" if decision == "Abstain" else "Managed",
    )
