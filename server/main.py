"""FastAPI app exposing /ingest and /ask.

Single-process, in-memory store — fine for the demo/free-tier deploy.
Swapping in a persistent/multi-tenant store is a ROADMAP item.
"""

import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from docubrain import StubEmbedder, VectorStore, ask, ingest_pdf

app = FastAPI(title="docubrain", version="0.1.0")

# One process-wide store for the demo deploy. A real multi-tenant deploy
# would key this by API key / workspace — out of scope for v0.1.
_store = VectorStore(embedder=StubEmbedder())
_documents: dict[str, dict] = {}

_SAMPLE_PDF = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "sample_data", "sample_contract.pdf"
)


@app.on_event("startup")
async def _seed_sample_document() -> None:
    """Pre-load the bundled sample contract so the public demo is queryable
    without requiring a visitor to upload their own PDF first."""
    if not os.path.exists(_SAMPLE_PDF):
        return
    document = ingest_pdf(_SAMPLE_PDF)
    _store.add_document(document)
    _documents[document.doc_id] = {
        "filename": "sample_contract.pdf",
        "page_count": document.page_count,
        "chunk_count": len(document.chunks),
    }


class AskRequest(BaseModel):
    question: str
    doc_id: Optional[str] = None
    top_k: int = 3


class AskResponse(BaseModel):
    text: str
    cited_pages: list[int]
    doc_id: str


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    if file.content_type not in ("application/pdf", "application/x-pdf"):
        raise HTTPException(400, "Only PDF uploads are supported.")

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp.flush()
        document = ingest_pdf(tmp.name)

    _store.add_document(document)
    _documents[document.doc_id] = {
        "filename": file.filename,
        "page_count": document.page_count,
        "chunk_count": len(document.chunks),
    }
    return {"doc_id": document.doc_id, **_documents[document.doc_id]}


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    if request.doc_id is not None and request.doc_id not in _documents:
        raise HTTPException(404, f"Unknown doc_id: {request.doc_id}")
    try:
        answer = ask(
            request.question, _store, doc_id=request.doc_id, top_k=request.top_k
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return AskResponse(
        text=answer.text, cited_pages=answer.cited_pages, doc_id=answer.doc_id
    )


@app.get("/documents")
async def list_documents() -> dict:
    return _documents


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "chunks_indexed": len(_store)}
