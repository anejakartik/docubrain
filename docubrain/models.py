"""Core data types shared across ingestion, storage, and Q&A."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    """A page-attributed slice of extracted PDF text.

    `page` is 1-indexed to match how a human would refer to a page
    when opening the PDF — never expose 0-indexed page numbers in
    an answer's citation.
    """

    doc_id: str
    chunk_id: str
    page: int
    text: str


@dataclass
class Document:
    """A single ingested PDF: its chunks plus basic metadata."""

    doc_id: str
    source_path: str
    page_count: int
    chunks: list[Chunk] = field(default_factory=list)


@dataclass
class Answer:
    """The result of `ask()` — always carries at least one page citation."""

    text: str
    cited_pages: list[int]
    doc_id: str
    supporting_chunks: list[Chunk]

    def __post_init__(self) -> None:
        if not self.cited_pages:
            raise ValueError(
                "An Answer must cite at least one page — "
                "docubrain never returns an uncited answer."
            )
