import pytest

from docubrain.embeddings import StubEmbedder
from docubrain.ingest import ingest_pdf
from docubrain.store import VectorStore


def test_empty_store_search_returns_no_results():
    store = VectorStore(embedder=StubEmbedder())
    assert store.search("anything") == []
    assert len(store) == 0


def test_add_document_populates_the_store(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    store = VectorStore(embedder=StubEmbedder())
    store.add_document(document)
    assert len(store) == len(document.chunks)


def test_search_returns_at_most_top_k_results(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    store = VectorStore(embedder=StubEmbedder())
    store.add_document(document)

    results = store.search("payment terms", top_k=2)
    assert len(results) <= 2
    for chunk, score in results:
        assert -1.0 <= score <= 1.0


def test_search_finds_the_right_page_for_a_targeted_question(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    store = VectorStore(embedder=StubEmbedder())
    store.add_document(document)

    results = store.search("When are invoices due for payment?", top_k=1)
    assert len(results) == 1
    top_chunk, _ = results[0]
    assert "Payment Terms" in top_chunk.text


def test_adding_a_document_with_no_chunks_is_a_noop():
    from docubrain.models import Document

    store = VectorStore(embedder=StubEmbedder())
    store.add_document(Document(doc_id="empty", source_path="x", page_count=0))
    assert len(store) == 0
