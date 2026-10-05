"""docubrain — PDF intelligence with page-cited answers."""

from docubrain.models import Chunk, Document, Answer
from docubrain.ingest import ingest_pdf
from docubrain.embeddings import StubEmbedder, OpenAIEmbedder
from docubrain.store import VectorStore
from docubrain.qa import ask
from docubrain.render import render_page_png

__all__ = [
    "Chunk",
    "Document",
    "Answer",
    "ingest_pdf",
    "StubEmbedder",
    "OpenAIEmbedder",
    "VectorStore",
    "ask",
    "render_page_png",
]
