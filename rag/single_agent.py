from __future__ import annotations

import time

from models.ollama import generate
from rag.retriever import format_context, retrieve
from rag.schema import RAGResult


def answer(question: str) -> RAGResult:
    start = time.perf_counter()
    chunks, retrieval_score = retrieve(question)
    prompt = f"""
You are answering questions about enterprise documents.
Use the provided evidence only. If evidence is insufficient, say that the documents do not contain enough information.

Evidence:
{format_context(chunks)}

Question:
{question}

Answer:
""".strip()
    response = generate(prompt, temperature=0.1)
    return RAGResult(
        system_name="Single-Agent RAG",
        answer=response,
        confidence=None,
        decision="Answer",
        retrieved_chunks=chunks,
        response_time=time.perf_counter() - start,
        retrieval_score=retrieval_score,
    )
