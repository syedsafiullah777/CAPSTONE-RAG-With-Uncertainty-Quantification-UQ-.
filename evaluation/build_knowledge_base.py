from __future__ import annotations

import shutil

from config import PDF_DIR, SAMPLED_QUESTIONS_PATH, VECTORSTORE_DIR
from evaluation.dataset_loader import load_sampled_questions
from rag.retriever import build_knowledge_base
from rag.text_utils import clean_text


def export_ragbench_contexts_to_documents(clear_existing: bool = False) -> int:
    if clear_existing and PDF_DIR.exists():
        shutil.rmtree(PDF_DIR)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    sampled = load_sampled_questions(SAMPLED_QUESTIONS_PATH)
    exported = 0
    for index, row in sampled.iterrows():
        context = clean_text(str(row.get("context", "")))
        if not context or context.lower() == "nan":
            continue
        dataset = str(row.get("dataset", "ragbench"))
        output = PDF_DIR / f"{dataset}_{index:04d}.txt"
        output.write_text(context, encoding="utf-8")
        exported += 1
    return exported


def build_from_sampled_ragbench(clear_existing_documents: bool = False) -> dict:
    if VECTORSTORE_DIR.exists():
        shutil.rmtree(VECTORSTORE_DIR)
    exported = export_ragbench_contexts_to_documents(clear_existing=clear_existing_documents)
    result = build_knowledge_base()
    result["exported_context_documents"] = exported
    return result


if __name__ == "__main__":
    output = build_from_sampled_ragbench(clear_existing_documents=True)
    print(output["message"])
    print(f"Exported {output['exported_context_documents']} RAGBench context document(s).")
