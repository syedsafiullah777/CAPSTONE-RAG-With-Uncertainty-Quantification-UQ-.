#!/usr/bin/env python3
"""Preflight: verify Chroma index matches index_manifest.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config
from src.retrieval.index import COLLECTION_NAME
from src.retrieval.preflight import IndexPreflightError, validate_index_preflight


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 6 Chroma index preflight")
    parser.add_argument("--persist-dir", default=None, help="Override kb_index path")
    parser.add_argument("--manifest", default=None, help="Override manifest path")
    args = parser.parse_args()

    config = load_experiment_config()
    retrieval_cfg = config.section("retrieval")
    persist_dir = Path(args.persist_dir) if args.persist_dir else get_path(config, "kb_index")
    manifest_path = Path(args.manifest) if args.manifest else None
    collection_name = str(retrieval_cfg.get("collection_name") or COLLECTION_NAME)

    try:
        report = validate_index_preflight(
            persist_dir,
            manifest_path=manifest_path,
            collection_name=collection_name,
        )
    except IndexPreflightError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        return 1

    print(json.dumps({"status": "PASS", **report}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
