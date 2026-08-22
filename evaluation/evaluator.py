from __future__ import annotations

import pandas as pd

from evaluation.metrics import result_metrics
from rag.multi_agent import answer_verified, answer_with_uncertainty
from rag.schema import RAGResult
from rag.single_agent import answer as single_agent_answer


SYSTEMS = {
    "single_agent": single_agent_answer,
    "multi_agent": answer_verified,
    "multi_agent_uq": answer_with_uncertainty,
}


def flatten_result(result: RAGResult, question: str, ground_truth: str, dataset: str) -> dict:
    metrics = result_metrics(result, question, ground_truth)
    return {
        "dataset": dataset,
        "question": question,
        "ground_truth": ground_truth,
        "system": result.system_name,
        "answer": result.answer,
        "confidence": result.confidence,
        "decision": result.decision,
        "response_time": result.response_time,
        "retrieval_score": result.retrieval_score,
        "verification_score": result.verification_score,
        "consistency_score": result.consistency_score,
        "sources": "; ".join(f"{c.source}:p{c.page}" for c in result.retrieved_chunks),
        **metrics,
    }


def summarize_results(results: pd.DataFrame) -> pd.DataFrame:
    summary = (
        results.groupby("system")
        .agg(
            average_accuracy=("accuracy", "mean"),
            accuracy_std=("accuracy", "std"),
            hallucination_rate=("hallucinated", "mean"),
            faithfulness=("faithfulness", "mean"),
            mean_confidence=("confidence", "mean"),
            average_response_time=("response_time", "mean"),
            retrieval_precision=("retrieval_precision", "mean"),
            abstention_rate=("abstained", "mean"),
        )
        .reset_index()
    )
    return summary
