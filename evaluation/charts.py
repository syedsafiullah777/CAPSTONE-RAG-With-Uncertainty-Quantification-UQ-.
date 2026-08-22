from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import CHARTS_DIR, RESULTS_DIR


SUMMARY_PATH = RESULTS_DIR / "summary.csv"


def _bar_chart(df: pd.DataFrame, column: str, title: str, filename: str) -> Path:
    import matplotlib.pyplot as plt

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    output = CHARTS_DIR / filename
    plt.figure(figsize=(8, 5))
    plt.bar(df["system"], df[column])
    plt.title(title)
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(output, dpi=180)
    plt.close()
    return output


def generate_charts(summary_path: Path = SUMMARY_PATH) -> list[Path]:
    if not summary_path.exists():
        raise FileNotFoundError(f"{summary_path} was not found. Run the experiment first.")
    df = pd.read_csv(summary_path)
    return [
        _bar_chart(df, "average_accuracy", "Average Accuracy", "accuracy.png"),
        _bar_chart(df, "hallucination_rate", "Hallucination Rate", "hallucination.png"),
        _bar_chart(df, "mean_confidence", "Mean Confidence", "confidence.png"),
        _bar_chart(df, "average_response_time", "Average Response Time", "response_time.png"),
    ]


if __name__ == "__main__":
    paths = generate_charts()
    for path in paths:
        print(path)
