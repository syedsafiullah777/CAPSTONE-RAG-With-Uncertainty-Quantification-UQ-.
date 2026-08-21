#!/usr/bin/env python3
"""Phase 6: download FinQA source PDFs and build the Chroma knowledge base."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from src.config import get_path, load_experiment_config
from src.retrieval.index import build_knowledge_base
from src.retrieval.pdf_fetch import collect_corpus_targets, download_pdfs
from src.retrieval.retriever import retrieve
from src.utils import create_run_id, get_logger, setup_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Build FinQA source-PDF knowledge base")
    parser.add_argument("--distractors", type=int, default=50, help="Extra train PDFs as distractors")
    parser.add_argument("--skip-download", action="store_true", help="Use already-downloaded PDFs only")
    parser.add_argument("--no-reset", action="store_true", help="Do not delete existing collection")
    parser.add_argument("--demo-query", type=str, default="", help="Optional retrieval smoke query")
    args = parser.parse_args()

    config = load_experiment_config()
    run_id = create_run_id("phase6")
    setup_logging(
        level="INFO",
        log_dir=get_path(config, "results_logs"),
        run_id=run_id,
        console=True,
        file=True,
    )
    log = get_logger(run_id=run_id, phase="phase6")

    test_csv = get_path(config, "data_final") / "selected_140_questions.csv"
    cal_csv = get_path(config, "data_calibration") / "calibration_questions.csv"
    docs_dir = get_path(config, "kb_documents")
    index_dir = get_path(config, "kb_index")
    repo_id = str(config.get("dataset", "huggingface_id", default="G4KMU/t2-ragbench"))
    subset = str(config.get("dataset", "subset", default="FinQA"))
    emb = str(config.get("embeddings", "model", default="BAAI/bge-small-en-v1.5"))
    chunk_size = int(config.get("retrieval", "chunk_size", default=900))
    chunk_overlap = int(config.get("retrieval", "chunk_overlap", default=150))
    top_k = int(config.get("retrieval", "top_k", default=4))
    seed = int(config.get("execution", "random_seed", default=42))

    log.info("Collecting corpus targets distractors=%s", args.distractors)
    docs = collect_corpus_targets(
        test_csv=test_csv,
        calibration_csv=cal_csv,
        distractor_count=args.distractors,
        distractor_seed=seed,
        dataset_id=repo_id,
        subset=subset,
    )
    log.info("Corpus docs=%s", len(docs))

    if args.skip_download:
        local_paths = {}
        for doc in docs:
            path = docs_dir / doc.split / doc.file_name
            if path.exists():
                local_paths[doc.doc_key] = str(path)
        download_stats = {
            "requested": len(docs),
            "downloaded": 0,
            "skipped_existing": len(local_paths),
            "failed": [],
            "local_paths": local_paths,
        }
    else:
        log.info("Downloading PDFs into %s", docs_dir)
        download_stats = download_pdfs(docs, documents_dir=docs_dir, repo_id=repo_id)
    log.info(
        "Download done downloaded=%s skipped=%s failed=%s",
        download_stats["downloaded"],
        download_stats["skipped_existing"],
        len(download_stats["failed"]),
    )

    log.info("Building index at %s", index_dir)
    manifest = build_knowledge_base(
        docs,
        download_stats["local_paths"],
        persist_dir=index_dir,
        documents_dir=docs_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_model=emb,
        reset=not args.no_reset,
    )
    manifest["download"] = {
        "requested": download_stats["requested"],
        "downloaded": download_stats["downloaded"],
        "skipped_existing": download_stats["skipped_existing"],
        "failed_count": len(download_stats["failed"]),
        "failed": download_stats["failed"][:20],
    }
    (index_dir / "index_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    snap = get_path(config, "results_config") / "phase6_index_manifest.json"
    snap.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    log.info("Index built chunks=%s docs_indexed=%s", manifest["chunks"], manifest["docs_indexed"])

    demo_query = args.demo_query.strip()
    demo_out = None
    if not demo_query:
        # Use first frozen test question as a live retrieval smoke test.
        import csv

        with test_csv.open(encoding="utf-8", newline="") as handle:
            first = next(csv.DictReader(handle))
            demo_query = str(first["question"])
            demo_out = {
                "question_id": first["id"],
                "gold_file_name": first["file_name"],
            }

    hits = retrieve(
        demo_query,
        persist_dir=index_dir,
        top_k=top_k,
        embedding_model=emb,
    )
    demo = {
        "query": demo_query,
        "top_k": top_k,
        "hits": [h.to_dict() for h in hits],
        **(demo_out or {}),
    }
    demo_path = index_dir / "retrieval_demo.json"
    demo_path.write_text(json.dumps(demo, indent=2) + "\n", encoding="utf-8")
    log.info("Retrieval demo saved %s hits=%s", demo_path, len(hits))

    print(
        json.dumps(
            {
                "status": "built",
                "docs_indexed": manifest["docs_indexed"],
                "chunks": manifest["chunks"],
                "download_failed": manifest["download"]["failed_count"],
                "index_manifest": str(index_dir / "index_manifest.json"),
                "retrieval_demo": str(demo_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
