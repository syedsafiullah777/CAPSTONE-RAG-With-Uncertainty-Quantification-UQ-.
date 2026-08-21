"""Download FinQA page PDFs from the Hugging Face dataset repo."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from huggingface_hub import hf_hub_download


@dataclass(frozen=True)
class CorpusDoc:
    split: str
    file_name: str
    role: str  # test | calibration | distractor
    company_symbol: str = ""
    company_name: str = ""
    report_year: str = ""
    context_id: str = ""
    question_id: str = ""

    @property
    def repo_path(self) -> str:
        return f"data/FinQA/{self.split}/{self.file_name}"

    @property
    def doc_key(self) -> str:
        return f"{self.split}::{self.file_name}"


def _read_csv_docs(path: Path, *, split: str, role: str) -> list[CorpusDoc]:
    docs: list[CorpusDoc] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            file_name = str(row.get("file_name") or "").strip()
            if not file_name:
                continue
            docs.append(
                CorpusDoc(
                    split=split,
                    file_name=file_name,
                    role=role,
                    company_symbol=str(row.get("company_symbol") or ""),
                    company_name=str(row.get("company_name") or ""),
                    report_year=str(row.get("report_year") or ""),
                    context_id=str(row.get("context_id") or ""),
                    question_id=str(row.get("id") or ""),
                )
            )
    return docs


def _dedupe_by_doc_key(docs: Iterable[CorpusDoc]) -> list[CorpusDoc]:
    seen: set[str] = set()
    out: list[CorpusDoc] = []
    for doc in docs:
        if doc.doc_key in seen:
            continue
        seen.add(doc.doc_key)
        out.append(doc)
    return out


def collect_corpus_targets(
    *,
    test_csv: Path,
    calibration_csv: Path,
    distractor_count: int = 50,
    distractor_seed: int = 42,
    dataset_id: str = "G4KMU/t2-ragbench",
    subset: str = "FinQA",
) -> list[CorpusDoc]:
    """Collect unique PDFs for test + calibration, plus optional train distractors."""
    core = _dedupe_by_doc_key(
        [
            *_read_csv_docs(test_csv, split="test", role="test"),
            *_read_csv_docs(calibration_csv, split="dev", role="calibration"),
        ]
    )
    core_files = {d.file_name for d in core}
    if distractor_count <= 0:
        return core

    from datasets import load_dataset
    import random

    ds = load_dataset(dataset_id, subset, split="train")
    candidates: list[CorpusDoc] = []
    seen_files: set[str] = set(core_files)
    for row in ds:
        file_name = str(row.get("file_name") or "").strip()
        if not file_name or file_name in seen_files:
            continue
        seen_files.add(file_name)
        candidates.append(
            CorpusDoc(
                split="train",
                file_name=file_name,
                role="distractor",
                company_symbol=str(row.get("company_symbol") or ""),
                company_name=str(row.get("company_name") or ""),
                report_year=str(row.get("report_year") or ""),
                context_id=str(row.get("context_id") or ""),
                question_id=str(row.get("id") or ""),
            )
        )
    rng = random.Random(distractor_seed)
    rng.shuffle(candidates)
    return core + candidates[:distractor_count]


def download_pdfs(
    docs: list[CorpusDoc],
    *,
    documents_dir: Path,
    repo_id: str = "G4KMU/t2-ragbench",
) -> dict:
    """Download page PDFs into ``documents_dir/{split}/{file_name}``."""
    documents_dir.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    skipped = 0
    failed: list[dict] = []
    local_paths: dict[str, str] = {}

    for doc in docs:
        dest = documents_dir / doc.split / doc.file_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            local_paths[doc.doc_key] = str(dest)
            continue
        try:
            cached = hf_hub_download(
                repo_id=repo_id,
                repo_type="dataset",
                filename=doc.repo_path,
            )
            dest.write_bytes(Path(cached).read_bytes())
            downloaded += 1
            local_paths[doc.doc_key] = str(dest)
        except Exception as exc:  # noqa: BLE001 — record and continue
            failed.append({"doc_key": doc.doc_key, "repo_path": doc.repo_path, "error": str(exc)})

    return {
        "requested": len(docs),
        "downloaded": downloaded,
        "skipped_existing": skipped,
        "failed": failed,
        "local_paths": local_paths,
    }
