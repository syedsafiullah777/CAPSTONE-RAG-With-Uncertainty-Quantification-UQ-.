#!/usr/bin/env python3
"""Run pytest and save verbose output for phase validation evidence."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture pytest output for phase evidence")
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument(
        "--out",
        default=None,
        help="Output path (default: project_record/evidence/artifacts/phaseN_pytest_<timestamp>.txt)",
    )
    args = parser.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    default_out = V2_ROOT / "project_record" / "evidence" / "artifacts" / f"phase{args.phase}_pytest_{ts}.txt"
    out_path = Path(args.out) if args.out else default_out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
    proc = subprocess.run(
        cmd,
        cwd=V2_ROOT,
        capture_output=True,
        text=True,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(V2_ROOT)},
    )
    header = (
        f"# Phase {args.phase} pytest capture\n"
        f"# recorded_at_utc: {datetime.now(timezone.utc).isoformat()}\n"
        f"# command: PYTHONPATH=. pytest -v --tb=short\n"
        f"# exit_code: {proc.returncode}\n\n"
    )
    out_path.write_text(header + proc.stdout + proc.stderr, encoding="utf-8")
    print(str(out_path))
    print(f"exit_code={proc.returncode}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
