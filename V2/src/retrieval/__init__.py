"""Knowledge-base retrieval package (Phase 6).

Indexes FinQA source PDFs — never the gold ``context`` field as retrieval output.
"""

from src.retrieval.chunking import chunk_pages
from src.retrieval.extract import extract_pdf_pages
from src.retrieval.index import build_knowledge_base, load_collection
from src.retrieval.pdf_fetch import collect_corpus_targets, download_pdfs
from src.retrieval.retriever import RetrievedChunk, retrieve

__all__ = [
    "RetrievedChunk",
    "build_knowledge_base",
    "chunk_pages",
    "collect_corpus_targets",
    "download_pdfs",
    "extract_pdf_pages",
    "load_collection",
    "retrieve",
]
