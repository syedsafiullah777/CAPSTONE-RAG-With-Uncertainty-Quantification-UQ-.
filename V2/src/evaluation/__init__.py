"""Evaluation helpers (numeric match + Phase 16 CPU metrics).

``run_evaluation`` lives in ``src.evaluation.runner`` and is imported by the
CLI only, to avoid a circular import with ``src.calibration.lock``.
"""

from src.evaluation.metrics import score_case
from src.evaluation.numeric import numeric_match

__all__ = ["numeric_match", "score_case"]
