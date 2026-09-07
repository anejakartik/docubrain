"""docubrain — PDF intelligence with page-cited answers."""

from docubrain.models import Chunk, Document, Answer
from docubrain.ingest import ingest_pdf
from docubrain.embeddings import StubEmbedder, OpenAIEmbedder
from docubrain.store import VectorStore
from docubrain.qa import ask

__all__ = [
    "Chunk",
    "Document",
    "Answer",
    "ingest_pdf",
    "StubEmbedder",
    "OpenAIEmbedder",
    "VectorStore",
    "ask",
]
