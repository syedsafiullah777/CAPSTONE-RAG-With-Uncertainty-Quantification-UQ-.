"""Validation evidence helpers (project management — not RAG)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

ValidationStatus = Literal["PASS", "FAIL", "NEEDS_VERIFICATION"]


@dataclass
class ValidationRecord:
    phase: int
    test_name: str
    command: str
    expected: str
    actual: str
    status: ValidationStatus
    recorded_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    notebook: str | None = None
    environment: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    output_path: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def summarize_environment(fingerprint: dict[str, Any] | None) -> dict[str, Any]:
    if not fingerprint:
        return {}
    return {
        "device": fingerprint.get("device"),
        "platform": fingerprint.get("platform"),
        "gpu": fingerprint.get("gpu"),
        "torch": fingerprint.get("torch"),
        "model_config": fingerprint.get("model_config"),
        "git_commit": fingerprint.get("git_commit"),
        "captured_at_utc": fingerprint.get("captured_at_utc"),
    }
