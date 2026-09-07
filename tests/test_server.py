import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    # Reimport so each test gets a fresh in-memory store instead of
    # leaking state between tests via the module-level `_store`.
    import server.main as main_module

    importlib.reload(main_module)
    return TestClient(main_module.app)


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "chunks_indexed": 0}


def test_ingest_rejects_non_pdf(client):
    response = client.post(
        "/ingest", files={"file": ("notes.txt", b"hello", "text/plain")}
    )
    assert response.status_code == 400


def test_ask_before_any_ingest_returns_404(client):
    response = client.post("/ask", json={"question": "anything?"})
    assert response.status_code == 404


def test_ingest_then_ask_round_trip(client, sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        ingest_response = client.post(
            "/ingest", files={"file": ("sample_contract.pdf", f, "application/pdf")}
        )
    assert ingest_response.status_code == 200
    body = ingest_response.json()
    assert body["page_count"] == 4
    doc_id = body["doc_id"]

    ask_response = client.post(
        "/ask",
        json={"question": "Is there a cap on liability?", "doc_id": doc_id, "top_k": 1},
    )
    assert ask_response.status_code == 200
    answer = ask_response.json()
    assert answer["cited_pages"] == [4]
    assert answer["doc_id"] == doc_id


def test_ask_with_unknown_doc_id_returns_404(client, sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        client.post(
            "/ingest", files={"file": ("sample_contract.pdf", f, "application/pdf")}
        )
    response = client.post(
        "/ask", json={"question": "anything?", "doc_id": "does-not-exist"}
    )
    assert response.status_code == 404
