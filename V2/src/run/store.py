"""Append-only raw results + checkpoint/resume for evaluation jobs.

Case key: ``{architecture}:{question_id}``.
Never silently overwrites completed raw cases. Resume skips completed keys.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.rag.schema import RAGCaseResult

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_PENDING = "PENDING"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def case_is_successful(result: RAGCaseResult) -> bool:
    """Pipeline success: no error, evidence present, non-empty answer (incl. ABSTAIN)."""
    if result.error:
        return False
    if not result.retrieved_evidence:
        return False
    if not (result.answer or "").strip():
        return False
    return True


class CaseStore:
    """Per-run raw JSONL + checkpoint. Duplicate-safe and resumable."""

    def __init__(
        self,
        run_dir: Path,
        *,
        checkpoint_copy: Path | None = None,
        raw_filename: str = "cases.jsonl",
    ) -> None:
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.raw_path = self.run_dir / raw_filename
        self.checkpoint_path = self.run_dir / "checkpoint.json"
        self.checkpoint_copy = Path(checkpoint_copy) if checkpoint_copy else None
        self._completed: set[str] = set()
        self._failed: dict[str, str] = {}
        self._records: dict[str, dict[str, Any]] = {}
        self._meta: dict[str, Any] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        if self.raw_path.is_file():
            with self.raw_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    text = line.strip()
                    if not text:
                        continue
                    try:
                        payload = json.loads(text)
                    except json.JSONDecodeError:
                        # Interrupted mid-write — ignore the incomplete last line.
                        continue
                    key = str(payload.get("case_key") or "")
                    if not key:
                        continue
                    self._records[key] = payload
                    status = str(payload.get("case_status") or "")
                    if status == STATUS_COMPLETED or (
                        status != STATUS_FAILED and not payload.get("error")
                    ):
                        if payload.get("error"):
                            self._failed[key] = str(payload["error"])
                            self._completed.discard(key)
                        else:
                            self._completed.add(key)
                            self._failed.pop(key, None)
                    else:
                        self._failed[key] = str(payload.get("error") or status or "failed")
                        self._completed.discard(key)
        if self.checkpoint_path.is_file():
            try:
                self._meta = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._meta = {}

    @property
    def completed_keys(self) -> set[str]:
        return set(self._completed)

    @property
    def failed_keys(self) -> dict[str, str]:
        return dict(self._failed)

    def has_completed(self, case_key: str) -> bool:
        return case_key in self._completed

    def should_run(self, case_key: str, *, retry_failed: bool) -> bool:
        if case_key in self._completed:
            return False
        if case_key in self._failed:
            return bool(retry_failed)
        return True

    def append_result(self, result: RAGCaseResult, *, extra: dict[str, Any] | None = None) -> bool:
        """Write one case. Returns False if the case was already completed (duplicate)."""
        key = result.case_id
        if key in self._completed:
            return False
        ok = case_is_successful(result)
        payload = result.to_dict()
        payload["case_key"] = key
        payload["case_status"] = STATUS_COMPLETED if ok else STATUS_FAILED
        if extra:
            payload.update(extra)
        return self.append_payload(key, payload, ok=ok, error=result.error)

    def append_payload(
        self,
        key: str,
        payload: dict[str, Any],
        *,
        ok: bool,
        error: str | None = None,
    ) -> bool:
        """Write one dict record. Returns False if the case was already completed."""
        if key in self._completed:
            return False
        record = dict(payload)
        record["case_key"] = key
        record["case_status"] = STATUS_COMPLETED if ok else STATUS_FAILED
        if error:
            record["error"] = error
        with self.raw_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")
        self._records[key] = record
        if ok:
            self._completed.add(key)
            self._failed.pop(key, None)
        else:
            self._failed[key] = str(error or record.get("error") or "failed")
            self._completed.discard(key)
        return True

    def progress(self, planned_keys: list[str]) -> dict[str, Any]:
        pending = [key for key in planned_keys if key not in self._completed and key not in self._failed]
        return {
            "n_planned": len(planned_keys),
            "n_completed": sum(1 for key in planned_keys if key in self._completed),
            "n_failed": sum(1 for key in planned_keys if key in self._failed),
            "n_pending": len(pending),
            "completed": [key for key in planned_keys if key in self._completed],
            "failed": {key: self._failed[key] for key in planned_keys if key in self._failed},
            "pending": pending,
        }

    def write_checkpoint(self, meta: dict[str, Any], planned_keys: list[str]) -> dict[str, Any]:
        progress = self.progress(planned_keys)
        payload = {
            **self._meta,
            **meta,
            **progress,
            "raw_path": str(self.raw_path),
            "updated_at_utc": utc_now(),
        }
        self._meta = payload
        text = json.dumps(payload, indent=2) + "\n"
        tmp = self.checkpoint_path.with_suffix(".json.tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(self.checkpoint_path)
        if self.checkpoint_copy is not None:
            self.checkpoint_copy.parent.mkdir(parents=True, exist_ok=True)
            self.checkpoint_copy.write_text(text, encoding="utf-8")
        return payload


def latest_run_dir(raw_root: Path) -> Path | None:
    if not raw_root.is_dir():
        return None
    dirs = [path for path in raw_root.iterdir() if path.is_dir() and (path / "checkpoint.json").is_file()]
    if not dirs:
        return None
    return max(dirs, key=lambda path: path.stat().st_mtime)
