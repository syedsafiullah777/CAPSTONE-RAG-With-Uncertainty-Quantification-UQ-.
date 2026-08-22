"""Reusable logging setup for V2 phases.

Records structured context fields when provided (run_id, phase, model, device,
architecture, question_id). Full benchmark logging is implemented in later phases.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any


_CONFIGURED = False
_DEFAULT_LOGGER_NAME = "v2"


class ContextFilter(logging.Filter):
    """Ensure optional context attributes always exist on log records."""

    DEFAULTS = {
        "run_id": "-",
        "phase": "-",
        "model": "-",
        "device": "-",
        "architecture": "-",
        "question_id": "-",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        for key, value in self.DEFAULTS.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return True


def setup_logging(
    *,
    level: str = "INFO",
    log_dir: Path | None = None,
    run_id: str | None = None,
    console: bool = True,
    file: bool = True,
) -> logging.Logger:
    """Configure the root V2 logger once and return it."""
    global _CONFIGURED
    logger = logging.getLogger(_DEFAULT_LOGGER_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    if _CONFIGURED:
        return logger

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | run_id=%(run_id)s | phase=%(phase)s | "
            "model=%(model)s | device=%(device)s | architecture=%(architecture)s | "
            "question_id=%(question_id)s | %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    context_filter = ContextFilter()

    if console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.addFilter(context_filter)
        logger.addHandler(stream_handler)

    if file and log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        suffix = run_id or "session"
        log_path = log_dir / f"{suffix}_{stamp}.log"
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        logger.addHandler(file_handler)

    _CONFIGURED = True
    return logger


def get_logger(
    name: str | None = None,
    **context: Any,
) -> logging.LoggerAdapter:
    """Return a logger adapter with optional structured context fields."""
    base = logging.getLogger(name or _DEFAULT_LOGGER_NAME)
    extras = {
        "run_id": context.get("run_id", "-"),
        "phase": context.get("phase", "-"),
        "model": context.get("model", "-"),
        "device": context.get("device", "-"),
        "architecture": context.get("architecture", "-"),
        "question_id": context.get("question_id", "-"),
    }
    return logging.LoggerAdapter(base, extras)
