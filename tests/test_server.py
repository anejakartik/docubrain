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


def _ingest_sample(client, sample_pdf_path) -> str:
    with open(sample_pdf_path, "rb") as f:
        response = client.post(
            "/ingest", files={"file": ("sample_contract.pdf", f, "application/pdf")}
        )
    return response.json()["doc_id"]


def test_ask_returns_a_bbox_citation_per_cited_page(client, sample_pdf_path):
    doc_id = _ingest_sample(client, sample_pdf_path)
    answer = client.post(
        "/ask",
        json={"question": "Is there a cap on liability?", "doc_id": doc_id, "top_k": 1},
    ).json()
    assert [c["page"] for c in answer["citations"]] == answer["cited_pages"]
    assert all(len(c["bbox"]) == 4 for c in answer["citations"])


def test_page_image_round_trip_with_highlight(client, sample_pdf_path):
    doc_id = _ingest_sample(client, sample_pdf_path)
    citation = client.post(
        "/ask",
        json={"question": "Is there a cap on liability?", "doc_id": doc_id, "top_k": 1},
    ).json()["citations"][0]
    highlight = ",".join(str(v) for v in citation["bbox"])
    response = client.get(
        f"/documents/{doc_id}/pages/{citation['page']}/image",
        params={"highlight": highlight},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG")


def test_page_image_unknown_doc_returns_404(client):
    assert client.get("/documents/nope/pages/1/image").status_code == 404


def test_page_image_out_of_range_page_returns_404(client, sample_pdf_path):
    doc_id = _ingest_sample(client, sample_pdf_path)
    assert client.get(f"/documents/{doc_id}/pages/0/image").status_code == 404
    assert client.get(f"/documents/{doc_id}/pages/99/image").status_code == 404


@pytest.mark.parametrize("highlight", ["1,2,3", "a,b,c,d"])
def test_page_image_rejects_malformed_highlight(client, sample_pdf_path, highlight):
    doc_id = _ingest_sample(client, sample_pdf_path)
    response = client.get(
        f"/documents/{doc_id}/pages/1/image", params={"highlight": highlight}
    )
    assert response.status_code == 400


def test_documents_listing_hides_server_paths(client, sample_pdf_path):
    _ingest_sample(client, sample_pdf_path)
    for meta in client.get("/documents").json().values():
        assert "source_path" not in meta


def test_ask_scoped_to_a_doc_outscored_by_another_still_answers(client, sample_pdf_path):
    # Regression: /ask used to take a global top-k and filter by doc_id
    # afterwards, so a second, identical upload lost every tie to the
    # first one and came back "No relevant content found".
    _ingest_sample(client, sample_pdf_path)
    second = _ingest_sample(client, sample_pdf_path)
    response = client.post(
        "/ask",
        json={"question": "Is there a cap on liability?", "doc_id": second, "top_k": 1},
    )
    assert response.status_code == 200
    assert response.json()["doc_id"] == second
