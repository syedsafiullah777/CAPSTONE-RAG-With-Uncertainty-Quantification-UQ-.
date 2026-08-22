from __future__ import annotations

from pathlib import Path

import pandas as pd


def append_row(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([row])
    df.to_csv(path, mode="a", index=False, header=not path.exists())


def save_summary(path: Path, rows: list[dict]) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return df
