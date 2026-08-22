from __future__ import annotations

from pathlib import Path

from config import COLLECTION_NAME, PDF_DIR, TOP_K, VECTORSTORE_DIR
from rag.chunking import extract_pdf_pages, extract_text_document, split_pages
from rag.embeddings import get_embedding_model
from rag.schema import RetrievedChunk
from rag.text_utils import similarity_from_distance


def _get_chroma_class():
    try:
        from langchain_chroma import Chroma
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc
    return Chroma


def build_knowledge_base(document_dir: Path = PDF_DIR, persist_dir: Path = VECTORSTORE_DIR) -> dict:
    Chroma = _get_chroma_class()
    document_dir.mkdir(parents=True, exist_ok=True)
    persist_dir.mkdir(parents=True, exist_ok=True)

    document_paths = sorted(document_dir.glob("*.pdf")) + sorted(document_dir.glob("*.txt"))
    if not document_paths:
        return {"documents": 0, "chunks": 0, "message": f"No PDF or text documents found in {document_dir}"}

    pages = []
    for document_path in document_paths:
        if document_path.suffix.lower() == ".pdf":
            pages.extend(extract_pdf_pages(document_path))
        elif document_path.suffix.lower() == ".txt":
            pages.extend(extract_text_document(document_path))

    texts, metadatas = split_pages(pages)
    embeddings = get_embedding_model()
    Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=COLLECTION_NAME,
        persist_directory=str(persist_dir),
    )
    return {
        "documents": len(document_paths),
        "chunks": len(texts),
        "message": f"Knowledge base built from {len(document_paths)} document(s) and {len(texts)} chunk(s).",
    }


def get_vectorstore(persist_dir: Path = VECTORSTORE_DIR):
    Chroma = _get_chroma_class()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(persist_dir),
    )


def retrieve(question: str, top_k: int = TOP_K) -> tuple[list[RetrievedChunk], float]:
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(question, k=top_k)
    chunks = []
    scores = []
    for document, distance in results:
        score = similarity_from_distance(distance)
        scores.append(score)
        chunks.append(
            RetrievedChunk(
                source=document.metadata.get("source", "Unknown"),
                page=document.metadata.get("page", "Unknown"),
                text=document.page_content,
                score=score,
            )
        )
    retrieval_score = sum(scores) / len(scores) if scores else 0.0
    return chunks, retrieval_score


def format_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "No evidence retrieved."
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        score = 0.0 if chunk.score is None else chunk.score
        blocks.append(f"[Chunk {index}] {chunk.source}, page {chunk.page}, score={score:.2f}\n{chunk.text}")
    return "\n\n".join(blocks)
