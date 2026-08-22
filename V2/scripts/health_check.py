"""Phase 1 health check — verify V2 config loads without touching V1."""

from __future__ import annotations

import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import load_experiment_config, project_root
from src.utils import create_run_id, get_logger, setup_logging


def main() -> int:
    root = project_root()
    config = load_experiment_config()
    run_id = create_run_id("phase1")
    setup_logging(level="INFO", console=True, file=False)
    log = get_logger(run_id=run_id, phase="phase1")
    log.info(
        "health_check ok root=%s project=%s dataset=%s",
        root,
        config.get("project", "name"),
        config.get("dataset", "subset"),
    )
    print(f"OK | V2_ROOT={root} | run_id={run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
