"""PDF ingestion: extract text per page and chunk it with page provenance kept.

v0.1 is text-only (no layout/image-region indexing yet — see ROADMAP.md).
Every chunk produced here carries the exact page it came from; nothing
downstream is allowed to lose that attribution.
"""

from __future__ import annotations

import uuid

import fitz  # PyMuPDF

from docubrain.models import Chunk, Document

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150


def _chunk_page_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split one page's text into overlapping windows.

    Chunking never crosses a page boundary — that's what keeps every
    chunk's page citation exact instead of "somewhere around page N".
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    step = max(chunk_size - overlap, 1)
    windows = []
    start = 0
    while start < len(text):
        windows.append(text[start : start + chunk_size])
        start += step
    return windows


def ingest_pdf(
    path: str,
    *,
    doc_id: str | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> Document:
    """Extract text page-by-page from a PDF and chunk it with page provenance.

    Raises FileNotFoundError / fitz errors as-is — callers (the API layer)
    are responsible for turning those into a 4xx response.
    """
    doc_id = doc_id or uuid.uuid4().hex[:12]
    pdf = fitz.open(path)
    try:
        chunks: list[Chunk] = []
        for page_index in range(pdf.page_count):
            page = pdf.load_page(page_index)
            page_number = page_index + 1  # 1-indexed for citations
            page_text = page.get_text()
            for i, window in enumerate(
                _chunk_page_text(page_text, chunk_size, chunk_overlap)
            ):
                chunks.append(
                    Chunk(
                        doc_id=doc_id,
                        chunk_id=f"{doc_id}-p{page_number}-{i}",
                        page=page_number,
                        text=window,
                    )
                )
        return Document(
            doc_id=doc_id,
            source_path=path,
            page_count=pdf.page_count,
            chunks=chunks,
        )
    finally:
        pdf.close()
