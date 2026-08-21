"""Extract text from FinQA page PDFs."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def clean_text(text: str) -> str:
    return " ".join(str(text).replace("\x00", " ").split())


def extract_pdf_pages(pdf_path: Path) -> list[dict[str, Any]]:
    """Return one page dict per PDF page with text + base metadata."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError("Install PyMuPDF: pip install pymupdf") from exc

    pages: list[dict[str, Any]] = []
    document = fitz.open(pdf_path)
    try:
        for page_index, page in enumerate(document, start=1):
            text = clean_text(page.get_text("text"))
            if not text:
                continue
            pages.append(
                {
                    "text": text,
                    "page": page_index,
                    "local_path": str(pdf_path),
                }
            )
    finally:
        document.close()
    return pages
