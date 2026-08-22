from __future__ import annotations

from pathlib import Path

from config import CHUNK_OVERLAP, CHUNK_SIZE
from rag.text_utils import clean_text


def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc

    pages = []
    document = fitz.open(pdf_path)
    for page_index, page in enumerate(document, start=1):
        text = clean_text(page.get_text("text"))
        if text:
            pages.append(
                {
                    "text": text,
                    "metadata": {"source": pdf_path.name, "page": page_index, "path": str(pdf_path)},
                }
            )
    return pages


def extract_text_document(path: Path) -> list[dict]:
    text = clean_text(path.read_text(encoding="utf-8", errors="ignore"))
    if not text:
        return []
    return [{"text": text, "metadata": {"source": path.name, "page": 1, "path": str(path)}}]


def split_pages(pages: list[dict]) -> tuple[list[str], list[dict]]:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc

    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    texts = []
    metadatas = []
    for page in pages:
        for chunk in splitter.split_text(page["text"]):
            texts.append(chunk)
            metadatas.append(page["metadata"])
    return texts, metadatas
