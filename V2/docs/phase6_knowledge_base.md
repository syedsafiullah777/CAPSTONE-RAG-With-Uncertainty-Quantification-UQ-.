# Phase 6 — Knowledge base (source PDFs)

**Status:** complete  

## What was built

Persistent Chroma index over FinQA **source page PDFs** for:

- frozen test 140 file set
- frozen calibration 40 file set
- 50 additional train distractors  

Gold `context` fields were **not** ingested as retrieval documents.

## Artefacts

- PDFs: `V2/knowledge_base/documents/{split}/pdf/...`
- Index: `V2/knowledge_base/index/` (Chroma persist)
- Manifest: `V2/knowledge_base/index/index_manifest.json`
- Retrieval demo: `V2/knowledge_base/index/retrieval_demo.json`
- Snapshot: `V2/results/config/phase6_index_manifest.json`

## Verified build stats

| Item | Value |
| --- | --- |
| Docs requested / indexed | 230 / 230 |
| Download failures | 0 |
| Chunks | 1239 |
| Embedding model | `BAAI/bge-small-en-v1.5` |
| Chunk size / overlap | 900 / 150 |
| Vector store | Chroma (cosine) |
| Roles | test + calibration + distractor |

## Reproduce

```bash
cd V2
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python scripts/build_index.py --distractors 50
```

## Out of scope

- Qwen3-8B inference (Phase 7)
- RAG architectures (Phases 8–10)
- Threshold locking
- Full 420 benchmark
