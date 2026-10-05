"""FastAPI app exposing /ingest and /ask.

Single-process, in-memory store — fine for the demo/free-tier deploy.
Swapping in a persistent/multi-tenant store is a ROADMAP item.
"""

import os
import tempfile
import uuid
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from docubrain import Chunk, StubEmbedder, VectorStore, ask, ingest_pdf, render_page_png

app = FastAPI(title="docubrain", version="0.1.0")

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# One process-wide store for the demo deploy. A real multi-tenant deploy
# would key this by API key / workspace — out of scope for v0.1.
_store = VectorStore(embedder=StubEmbedder())
_documents: dict[str, dict] = {}

_SAMPLE_PDF = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "sample_data", "sample_contract.pdf"
)

# Uploaded PDFs used to live only in a self-deleting NamedTemporaryFile,
# gone by the time anything tried to read them again — fine when all any
# later request needed was the already-extracted text, but page-image
# rendering needs the original file bytes. Persisted here instead, keyed
# by doc_id.
_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "docubrain_uploads")
os.makedirs(_UPLOAD_DIR, exist_ok=True)


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
        "source_path": _SAMPLE_PDF,
    }


class AskRequest(BaseModel):
    question: str
    doc_id: Optional[str] = None
    top_k: int = 3


class Citation(BaseModel):
    page: int
    bbox: Optional[tuple[float, float, float, float]] = None


class AskResponse(BaseModel):
    text: str
    cited_pages: list[int]
    doc_id: str
    citations: list[Citation] = []


@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    return FileResponse(os.path.join(_STATIC_DIR, "index.html"))


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    if file.content_type not in ("application/pdf", "application/x-pdf"):
        raise HTTPException(400, "Only PDF uploads are supported.")

    doc_id = uuid.uuid4().hex[:12]
    dest_path = os.path.join(_UPLOAD_DIR, f"{doc_id}.pdf")
    with open(dest_path, "wb") as f:
        f.write(await file.read())
    document = ingest_pdf(dest_path, doc_id=doc_id)

    _store.add_document(document)
    _documents[document.doc_id] = {
        "filename": file.filename,
        "page_count": document.page_count,
        "chunk_count": len(document.chunks),
        "source_path": dest_path,
    }
    return {
        "doc_id": document.doc_id,
        "filename": file.filename,
        "page_count": document.page_count,
        "chunk_count": len(document.chunks),
    }


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

    # One citation per cited page, carrying that page's first matching
    # chunk's bbox so the frontend can request a highlighted page image —
    # cited_pages can come from multiple supporting_chunks (generator mode),
    # so dedupe to the first chunk seen per page.
    chunk_by_page: dict[int, Chunk] = {}
    for chunk in answer.supporting_chunks:
        if chunk.page in answer.cited_pages:
            chunk_by_page.setdefault(chunk.page, chunk)
    citations = [
        Citation(page=page, bbox=chunk_by_page[page].bbox) for page in answer.cited_pages
    ]

    return AskResponse(
        text=answer.text,
        cited_pages=answer.cited_pages,
        doc_id=answer.doc_id,
        citations=citations,
    )


@app.get("/documents/{doc_id}/pages/{page_number}/image")
async def page_image(doc_id: str, page_number: int, highlight: Optional[str] = None) -> Response:
    """Render a cited page as a PNG, with the matching region boxed if
    `highlight=x0,y0,x1,y1` (PDF point coordinates, from an /ask citation's
    bbox) is given — lets a reader verify a citation at a glance."""
    if doc_id not in _documents:
        raise HTTPException(404, f"Unknown doc_id: {doc_id}")

    bbox = None
    if highlight is not None:
        parts = highlight.split(",")
        if len(parts) != 4:
            raise HTTPException(400, "highlight must be 'x0,y0,x1,y1'")
        try:
            bbox = (float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]))
        except ValueError as exc:
            raise HTTPException(400, "highlight must be 'x0,y0,x1,y1'") from exc

    try:
        png_bytes = render_page_png(
            _documents[doc_id]["source_path"], page_number, bbox
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return Response(content=png_bytes, media_type="image/png")


@app.get("/documents")
async def list_documents() -> dict:
    # source_path is a server-local filesystem path — internal only.
    return {
        doc_id: {k: v for k, v in meta.items() if k != "source_path"}
        for doc_id, meta in _documents.items()
    }


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "chunks_indexed": len(_store)}
