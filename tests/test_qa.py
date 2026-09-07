import pytest

from docubrain.embeddings import StubEmbedder
from docubrain.ingest import ingest_pdf
from docubrain.models import Answer, Chunk
from docubrain.qa import ask
from docubrain.store import VectorStore


@pytest.fixture()
def populated_store(sample_pdf_path):
    document = ingest_pdf(sample_pdf_path)
    store = VectorStore(embedder=StubEmbedder())
    store.add_document(document)
    return store


def test_ask_returns_an_answer_with_a_citation(populated_store):
    answer = ask("Is there a cap on liability?", populated_store, top_k=1)
    assert isinstance(answer, Answer)
    assert answer.cited_pages == [4]


def test_ask_raises_on_empty_store():
    store = VectorStore(embedder=StubEmbedder())
    with pytest.raises(ValueError):
        ask("anything?", store)


def test_ask_can_filter_by_doc_id(sample_pdf_path):
    doc = ingest_pdf(sample_pdf_path, doc_id="contract-a")
    store = VectorStore(embedder=StubEmbedder())
    store.add_document(doc)

    answer = ask("payment terms", store, doc_id="contract-a", top_k=1)
    assert answer.doc_id == "contract-a"

    with pytest.raises(ValueError):
        ask("payment terms", store, doc_id="nonexistent-doc", top_k=1)


def test_ask_uses_a_custom_generator_when_provided(populated_store):
    def fake_generator(question: str, chunks: list[Chunk]) -> str:
        return f"Synthesized answer to '{question}' from {len(chunks)} chunk(s)."

    answer = ask(
        "When are invoices due?", populated_store, top_k=1, generator=fake_generator
    )
    assert answer.text.startswith("Synthesized answer to")


def test_answer_rejects_zero_cited_pages():
    with pytest.raises(ValueError):
        Answer(text="oops", cited_pages=[], doc_id="d", supporting_chunks=[])
