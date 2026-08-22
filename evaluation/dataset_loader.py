from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

from config import RAGBENCH_SAMPLE_PLAN, RANDOM_SEED, SAMPLED_QUESTIONS_PATH


QUESTION_COLUMNS = ("question", "query", "user_input")
ANSWER_COLUMNS = ("response", "answer", "ground_truth", "reference")
CONTEXT_COLUMNS = ("documents", "contexts", "context", "passages")


def _first_available(row: dict, candidates: tuple[str, ...], default: str = "") -> str:
    for column in candidates:
        if column in row and row[column] is not None:
            return str(row[column])
    return default


def normalize_ragbench_row(row: dict, subset: str) -> dict:
    return {
        "dataset": subset,
        "question": _first_available(row, QUESTION_COLUMNS),
        "ground_truth": _first_available(row, ANSWER_COLUMNS),
        "context": _first_available(row, CONTEXT_COLUMNS),
    }


def load_ragbench_subset(subset: str, split: str = "test") -> pd.DataFrame:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc

    dataset = load_dataset("rungalileo/ragbench", subset, split=split)
    rows = [normalize_ragbench_row(dict(row), subset) for row in dataset]
    return pd.DataFrame(rows)


def create_sampled_questions(
    sample_plan: dict[str, int] | None = None,
    output_path: Path = SAMPLED_QUESTIONS_PATH,
    seed: int = RANDOM_SEED,
    split: str = "test",
) -> pd.DataFrame:
    sample_plan = sample_plan or RAGBENCH_SAMPLE_PLAN
    rng = random.Random(seed)
    frames = []

    for subset, count in sample_plan.items():
        df = load_ragbench_subset(subset, split=split)
        df = df.dropna(subset=["question", "ground_truth"])
        sample_count = min(count, len(df))
        selected_indices = rng.sample(list(df.index), sample_count)
        frames.append(df.loc[selected_indices])

    sampled = pd.concat(frames, ignore_index=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sampled.to_csv(output_path, index=False)
    return sampled


def load_sampled_questions(path: Path = SAMPLED_QUESTIONS_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} was not found. Run: python -m evaluation.dataset_loader"
        )
    return pd.read_csv(path)


if __name__ == "__main__":
    df = create_sampled_questions()
    print(f"Saved {len(df)} sampled questions to {SAMPLED_QUESTIONS_PATH}")
