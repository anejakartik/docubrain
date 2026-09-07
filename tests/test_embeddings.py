import numpy as np

from docubrain.embeddings import StubEmbedder


def _cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(a @ b / ((np.linalg.norm(a) * np.linalg.norm(b)) or 1.0))


def test_stub_embedder_is_deterministic():
    embedder = StubEmbedder()
    v1 = embedder.embed(["the quick brown fox"])[0]
    v2 = embedder.embed(["the quick brown fox"])[0]
    assert v1 == v2


def test_stub_embedder_returns_unit_length_vectors():
    embedder = StubEmbedder()
    vectors = embedder.embed(["hello world", "a completely different sentence"])
    for v in vectors:
        norm = sum(x * x for x in v) ** 0.5
        assert abs(norm - 1.0) < 1e-6


def test_stub_embedder_scores_similar_text_higher_than_unrelated_text():
    embedder = StubEmbedder()
    query = "How long does the confidentiality obligation last?"
    related = (
        "Each party agrees to hold confidential information in strict "
        "confidence for a period of five years."
    )
    unrelated = "Invoices are due net 45 from the invoice date."

    q_vec, related_vec, unrelated_vec = embedder.embed([query, related, unrelated])
    assert _cosine(q_vec, related_vec) > _cosine(q_vec, unrelated_vec)


def test_stub_embedder_handles_empty_string():
    embedder = StubEmbedder()
    vec = embedder.embed([""])[0]
    assert vec == [0.0] * StubEmbedder.dimensions
