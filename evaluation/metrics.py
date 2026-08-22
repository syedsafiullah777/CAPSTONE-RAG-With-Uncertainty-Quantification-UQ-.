from __future__ import annotations

from rag.schema import RAGResult
from rag.text_utils import token_overlap


def answer_correctness(answer: str, ground_truth: str) -> float:
    return token_overlap(ground_truth, answer)


def faithfulness(answer: str, evidence: str) -> float:
    return token_overlap(answer, evidence)


def retrieval_precision(question: str, evidence: str) -> float:
    return token_overlap(question, evidence)


def hallucinated(result: RAGResult, ground_truth: str) -> bool:
    if result.decision == "Abstain":
        return False
    return answer_correctness(result.answer, ground_truth) < 0.35 and (result.verification_score or 0.0) < 0.5


def result_metrics(result: RAGResult, question: str, ground_truth: str) -> dict:
    evidence_text = " ".join(chunk.text for chunk in result.retrieved_chunks)
    return {
        "accuracy": answer_correctness(result.answer, ground_truth),
        "faithfulness": faithfulness(result.answer, evidence_text),
        "retrieval_precision": retrieval_precision(question, evidence_text),
        "hallucinated": hallucinated(result, ground_truth),
        "abstained": result.decision == "Abstain",
    }
