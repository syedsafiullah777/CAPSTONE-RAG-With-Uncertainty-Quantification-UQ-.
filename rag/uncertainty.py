from __future__ import annotations

from models.ollama import generate
from rag.retriever import format_context
from rag.schema import RetrievedChunk
from rag.text_utils import average, token_overlap


def verification_score(answer: str, chunks: list[RetrievedChunk]) -> float:
    evidence_text = " ".join(chunk.text for chunk in chunks)
    lexical_score = token_overlap(answer, evidence_text)

    prompt = f"""
Score how well the answer is supported by the evidence on a scale from 0 to 1.
Return only one decimal number.

Evidence:
{format_context(chunks)}

Answer:
{answer}
""".strip()
    try:
        raw = generate(prompt, temperature=0.0)
        number = "".join(ch for ch in raw if ch.isdigit() or ch == ".")
        llm_score = float(number[:4])
        return max(0.0, min(1.0, average([lexical_score, llm_score])))
    except Exception:
        return lexical_score


def self_consistency_score(question: str, chunks: list[RetrievedChunk]) -> float:
    samples = []
    for temperature in (0.1, 0.4, 0.7):
        prompt = f"""
Answer the question using only the evidence.

Evidence:
{format_context(chunks)}

Question:
{question}
""".strip()
        try:
            samples.append(generate(prompt, temperature=temperature))
        except Exception:
            break

    if len(samples) < 2:
        return 0.5
    first = samples[0]
    return average(token_overlap(first, sample) for sample in samples[1:])


def combined_confidence(retrieval: float, verification: float, consistency: float) -> float:
    return average([retrieval, verification, consistency])
