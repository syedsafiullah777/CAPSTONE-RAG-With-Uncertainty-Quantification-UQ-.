from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import RESULTS_DIR, SAMPLED_QUESTIONS_PATH
from evaluation.dataset_loader import load_sampled_questions
from evaluation.evaluator import SYSTEMS, flatten_result, summarize_results
from evaluation.save_results import append_row


RESULTS_PATH = RESULTS_DIR / "experiment_results.csv"
SUMMARY_PATH = RESULTS_DIR / "summary.csv"


def run_experiment(sample_path: Path = SAMPLED_QUESTIONS_PATH, results_path: Path = RESULTS_PATH) -> pd.DataFrame:
    questions = load_sampled_questions(sample_path)
    if results_path.exists():
        results_path.unlink()

    for index, row in questions.iterrows():
        question = str(row["question"])
        ground_truth = str(row["ground_truth"])
        dataset = str(row.get("dataset", "unknown"))
        for _, system_fn in SYSTEMS.items():
            result = system_fn(question)
            append_row(results_path, flatten_result(result, question, ground_truth, dataset))
        print(f"Completed {index + 1}/{len(questions)}: {question[:80]}")

    results = pd.read_csv(results_path)
    summary = summarize_results(results)
    summary.to_csv(SUMMARY_PATH, index=False)
    return results


if __name__ == "__main__":
    run_experiment()
    print(f"Saved results to {RESULTS_PATH}")
    print(f"Saved summary to {SUMMARY_PATH}")
