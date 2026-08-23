# Phase 8 Colab retrieval failure — diagnostic report

| Field | Value |
| --- | --- |
| Phase | 8 — Single-Agent RAG baseline |
| Symptom | Colab smoke: all 3 questions returned `n_evidence=0`; Qwen3-8B generation succeeded |
| Date | 2026-08-23 |
| Status | **Root cause identified** (fix not implemented) |
| Scope | Diagnosis only — no architecture/dataset/frozen-set changes |

---

## Summary

**Root cause:** The Phase 6 Chroma vector index is **not present in the GitHub clone** used by Colab. Only the index *manifest* and *retrieval demo JSON* are committed. On Colab, `load_collection()` silently creates an **empty** Chroma collection; `retrieve()` queries it and returns zero hits without raising an error.

**Minimal fix:** Before running Phase 8 smoke on Colab, provide the built Phase 6 index at `V2/knowledge_base/index/` (including `chroma.sqlite3` and the Chroma UUID subfolder). Either sync from Google Drive/local backup, or rebuild on Colab with `scripts/build_index.py`.

---

## Observed failure (Colab)

| Item | Value |
| --- | --- |
| Workflow | GitHub clone → `/content/capstone-rag/V2` → Phase 8 smoke |
| LLM | Qwen3-8B via `llama_cpp` — **PASS** (generation works) |
| Retrieval | `n_evidence=0` for all 3 smoke questions |
| Errors in result | None (silent empty retrieval) |

---

## Working reference (local Mac)

| Item | Value |
| --- | --- |
| Smoke evidence | `results/config/phase8_single_agent_smoke.json` |
| Run ID | `phase8_20260822T164524Z_bd962134` |
| Result | **3/3 PASS** — `n_evidence=4` each, top scores 0.77–0.87 |
| Index path | `{V2_ROOT}/knowledge_base/index` (resolved correctly) |
| Index size | ~14 MB (`chroma.sqlite3` + Chroma segment folder) |
| PDF corpus | 230 PDFs (~57 MB) under `knowledge_base/documents/` |

---

## Checklist (requested items)

### Where the Phase 6 knowledge base is expected

| Path (relative to V2 root) | Purpose |
| --- | --- |
| `knowledge_base/documents/` | Source FinQA page PDFs (230 files) |
| `knowledge_base/index/` | Chroma persistent store |
| `knowledge_base/index/index_manifest.json` | Build metadata (1239 chunks) |
| `config/experiment.yaml` → `paths.kb_index` | `"knowledge_base/index"` |

Resolved at runtime via `get_path(cfg, "kb_index")` → `{V2_ROOT}/knowledge_base/index`.

### Whether the vector index exists (by environment)

| Environment | `chroma.sqlite3` | Chroma segment dir | Committed to GitHub |
| --- | --- | --- | --- |
| Local Mac | **Yes** (~12 MB) | **Yes** (`99ce927e-…/`) | **No** (gitignored) |
| GitHub clone / Colab | **No** | **No** | Only manifest + demo JSON |

```bash
# Verified locally (2026-08-23)
git ls-files V2/knowledge_base/
# → documents/.gitkeep, index/.gitkeep, index/index_manifest.json, index/retrieval_demo.json

git check-ignore -v V2/knowledge_base/index/chroma.sqlite3
# → V2/.gitignore:60:knowledge_base/index/**
```

### Whether source documents are available

| Environment | PDF count | In GitHub |
| --- | --- | --- |
| Local Mac | 230 | **No** (`knowledge_base/documents/**` gitignored) |
| Colab (GitHub clone) | 0 | Only `.gitkeep` |

PDFs are **not required for query-time retrieval** if the Chroma index is present (embeddings already stored). They **are** required to rebuild the index.

### Configured KB/index paths

From `config/experiment.yaml`:

```yaml
paths:
  kb_documents: "knowledge_base/documents"
  kb_index: "knowledge_base/index"
retrieval:
  collection_name: "finqa_source_pdfs"
  top_k: 4
embeddings:
  model: "BAAI/bge-small-en-v1.5"
```

`src/config/loader.py` resolves relative paths against `V2_ROOT` (derived from `src/config/loader.py` location). This works identically on Mac and Colab (`/content/capstone-rag/V2`). **Path resolution is not the bug.**

### Whether relative paths work from `/content/capstone-rag`

**Yes.** `V2_ROOT = Path(__file__).resolve().parents[2]` points to the cloned `V2/` folder regardless of mount point. Local smoke results confirm `persist_dir` is correctly set under V2 root.

### Embedding model availability

- Model: `BAAI/bge-small-en-v1.5` via `sentence-transformers` (`src/retrieval/embeddings.py`).
- On Colab, the model downloads from Hugging Face on first use.
- If embedding failed, `retrieve()` would raise and `run_single_agent()` would record an `error` field. Colab reported successful generation and no retrieval error → embedding likely ran; the collection was simply empty.

### Whether the index loads successfully

**Misleading “success”:** `load_collection()` in `src/retrieval/index.py` uses:

```python
return client.get_or_create_collection(name=collection_name, ...)
```

If `chroma.sqlite3` is missing, Chroma creates a new empty persistent store. No exception is raised. The committed `index_manifest.json` (1239 chunks) describes a **previous local build**, not the live Colab collection.

### Retriever initialization and top-k

- `run_single_agent()` → `retrieve(..., top_k=4, collection_name="finqa_source_pdfs")`.
- Configuration matches local smoke (top_k=4).
- `retrieve()` calls `collection.query(..., n_results=top_k)` and maps distances to scores.
- With an empty collection, Chroma returns empty `documents` / `ids` lists → `n_evidence=0`.

### Why `retrieve()` returns zero evidence

1. Colab clone has no Chroma DB files.
2. `get_or_create_collection` creates empty `finqa_source_pdfs`.
3. Query embedding is computed, but there are no stored vectors.
4. Empty result returned; pipeline continues to LLM with empty evidence prompt.

### Phase 6 artefacts excluded from GitHub / local-only dependency

**Confirmed.** By design in `V2/.gitignore`:

```
knowledge_base/documents/**
knowledge_base/index/**
!knowledge_base/index/index_manifest.json
!knowledge_base/index/retrieval_demo.json
```

Large artefacts (~71 MB total locally) live only on the dev machine. They were never pushed to GitHub. Colab notebook (`notebooks/colab_phase7_smoke.ipynb`) clones GitHub only and has **no step** to copy or build the knowledge base before RAG smoke.

Google Drive layout for KB backup: **NEEDS VERIFICATION** — `storage.google_drive.root` is defined but no verified KB copy on Drive was found in repo evidence.

---

## Local vs Colab path comparison

| Step | Local (working) | Colab (failing) |
| --- | --- | --- |
| V2 root | Mac path | `/content/capstone-rag/V2` |
| `kb_index` resolve | `{V2}/knowledge_base/index` | Same relative resolution |
| Chroma files | Present (14 MB) | **Absent** |
| Collection count | 1239 chunks | 0 (new empty collection) |
| `retrieve()` | 4 hits | 0 hits |
| LLM backend | `ollama_dev` | `llama_cpp` (GPU) |
| Smoke outcome | PASS | FAIL (`n_evidence=0`) |

The only material difference is **missing Phase 6 index artefacts on Colab**, not RAG code or path logic.

---

## Root cause

**The Phase 6 Chroma index (and PDF corpus) are gitignored and not included in the GitHub → Colab workflow.** Colab therefore runs retrieval against an empty auto-created Chroma collection. The committed `index_manifest.json` incorrectly implies a populated index is present.

Contributing code behaviour: `get_or_create_collection` fails open (empty index) instead of failing closed when manifest claims chunks > 0 but collection is empty.

---

## Minimal fix (do not implement until approved)

Choose **one** provisioning path before Phase 8 Colab smoke:

### Option A — Sync pre-built index (fastest; preferred for smoke)

1. One-time: copy local `V2/knowledge_base/index/` (entire directory including `chroma.sqlite3` and UUID subfolder) to persistent storage, e.g. `Google Drive/MSc-RAG/artifacts/knowledge_base/index/` (**path NEEDS VERIFICATION**).
2. In Colab, after clone: mount Drive and copy/sync that folder into `/content/capstone-rag/V2/knowledge_base/index/`.
3. Optional guardrail: verify `collection.count() >= index_manifest.json["chunks"]` before smoke.

PDFs not required for retrieval-only smoke if index is intact.

### Option B — Rebuild on Colab (reproducible; slower)

After clone, on GPU Colab runtime with network:

```bash
cd /content/capstone-rag/V2
pip install -r requirements.txt  # if not already
PYTHONPATH=. python scripts/build_index.py --distractors 50
```

Downloads 230 PDFs from Hugging Face, embeds with BGE, rebuilds Chroma (~tens of minutes). Produces a fresh index matching manifest schema.

### Recommended guardrail (either option)

Add a preflight check in smoke/benchmark entrypoints: if `index_manifest.json` reports `chunks > 0` but Chroma `collection.count() == 0`, raise a clear error naming the missing artefact and sync/rebuild instructions. This prevents silent `n_evidence=0` runs.

---

## What was ruled out

| Hypothesis | Verdict |
| --- | --- |
| Wrong `kb_index` path on Colab | Ruled out — same relative resolution |
| top_k misconfiguration | Ruled out — top_k=4 matches local |
| Embedding model missing | Unlikely — would raise exception |
| LLM/backend issue | Ruled out — generation succeeded |
| Frozen 140 / calibration sets | Not involved in retrieval index load |
| V1 interference | Not involved |

---

## Evidence paths

| File | Role |
| --- | --- |
| `V2/.gitignore` | Excludes index + documents from git |
| `V2/knowledge_base/index/index_manifest.json` | Declares 1239 chunks (metadata only on Colab) |
| `V2/src/retrieval/index.py` | `get_or_create_collection` silent empty create |
| `V2/src/retrieval/retriever.py` | Query returns [] on empty collection |
| `V2/results/config/phase8_single_agent_smoke.json` | Local PASS reference |
| `V2/notebooks/colab_runtime.md` | GitHub-only clone; no KB provisioning |
| `V2/docs/phase6_knowledge_base.md` | Rebuild command documented |

---

## Fix implemented (2026-08-23) — not yet verified on Colab

**Option B** implemented in V2:

| Component | Path |
| --- | --- |
| Preflight module | `src/retrieval/preflight.py` |
| Preflight CLI | `scripts/validate_kb_index.py` |
| Colab notebook | `notebooks/colab_phase8_smoke.ipynb` |
| Smoke integration | `scripts/smoke_single_agent.py` (preflight before cases) |
| Build integration | `scripts/build_index.py` (post-build preflight) |

Colab workflow: clone → install → `build_index.py --distractors 50` → preflight → Phase 8 smoke.

**Colab T4 verification:** **PASS** (2026-08-23T12:42:22Z) — run_id `phase8_20260823T124009Z_70a29b9f`; evidence in `phase8_smoke_test.json`, `phase8_single_agent_smoke.json`, `phase8_runtime_fingerprint.json`.

---

## Master record reference

Update Phase 8 Colab validation status separately after fix is applied and smoke re-run. This file records diagnosis only.
