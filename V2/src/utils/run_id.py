"""Run identification helpers for reproducible experiment tracking."""

from __future__ import annotations

from datetime import datetime, timezone
import re
import uuid


def create_run_id(prefix: str = "run") -> str:
    """Create a unique run ID: ``{prefix}_{UTC-timestamp}_{short-uuid}``."""
    safe_prefix = re.sub(r"[^a-zA-Z0-9_-]+", "-", prefix).strip("-") or "run"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short = uuid.uuid4().hex[:8]
    return f"{safe_prefix}_{stamp}_{short}"
