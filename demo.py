"""One-command demo: ingest a sample PDF, ask questions, print cited answers.

No API key required — uses StubEmbedder end to end, same pattern as
routerai's demo.py and evalstack's non-LLM smoke judges.
"""

from __future__ import annotations

import os
import subprocess
import sys

from docubrain import StubEmbedder, VectorStore, ask, ingest_pdf

SAMPLE_PDF = "sample_data/sample_contract.pdf"

QUESTIONS = [
    "How much notice is required to terminate the agreement?",
    "When are invoices due?",
    "How long does the confidentiality obligation last?",
    "Is there a cap on liability?",
]


def _ensure_sample_pdf() -> None:
    if not os.path.exists(SAMPLE_PDF):
        subprocess.run(
            [sys.executable, "scripts/make_sample_pdf.py"], check=True
        )


def main() -> None:
    _ensure_sample_pdf()

    print(f"Ingesting {SAMPLE_PDF} ...")
    document = ingest_pdf(SAMPLE_PDF)
    print(f"  -> {document.page_count} pages, {len(document.chunks)} chunks\n")

    store = VectorStore(embedder=StubEmbedder())
    store.add_document(document)

    for question in QUESTIONS:
        answer = ask(question, store, top_k=1)
        pages = ", ".join(f"p.{p}" for p in answer.cited_pages)
        print(f"Q: {question}")
        print(f"A: {answer.text[:160].strip()}...")
        print(f"   cited: {pages}\n")


if __name__ == "__main__":
    main()
