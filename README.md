# docubrain — PDF answers you can actually verify

> Drop PDFs in, ask a question, get an answer with the exact page it came from — every answer is cited, or it isn't returned at all.

**Status:** MVP (v0.1, text-only) · last shipped 2026-09-07
**Built by:** [Kartik Aneja](https://kartikaneja.com) — AI/ML Platform Engineer

---

## Why this exists

See [PRODUCT.md](./PRODUCT.md) for the full user/problem/solution writeup. TL;DR:

- **Who:** Ops/knowledge lead at a small law firm, insurance broker, or clinic with thousands of PDFs and no time to search them by hand.
- **Pain:** ChatGPT can't ingest the whole corpus, generic RAG demos ignore document structure, and an answer without a page citation isn't trustworthy in a legal/compliance context.
- **Why now:** RAG is everywhere, but almost none of it is built to point back at a specific page a human can open and check.

## What works today (MVP, v0.1)

- PDF ingestion with per-page text extraction (PyMuPDF) — chunking never crosses a page boundary
- Pluggable embeddings: a dependency-free `StubEmbedder` (no API key, deterministic) and an `OpenAIEmbedder` for production use
- Cosine-similarity search over ingested chunks
- `ask()` always returns an `Answer` with at least one cited page — there is no code path that returns an uncited answer (enforced at the data-model level, not just by convention)
- Page-region highlighting: every citation carries the bounding box of its source text, and `/documents/{id}/pages/{n}/image?highlight=…` renders the page with that region boxed — the answer points at *where* on the page, not just which page
- FastAPI service (`/ingest`, `/ask`, `/documents`, page images, `/healthz`)
- `demo.py` — runs end-to-end against a bundled sample contract with zero API keys
- 40 passing tests, all of them running against the zero-API-key path

## Try it

**Live demo:** https://docubrain.kartikaneja.com — pre-seeded with a sample contract, ask it a question right in the browser or via the API:

```bash
curl -X POST https://docubrain.kartikaneja.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Is there a cap on liability?"}'
```

Local in under a minute:

```bash
git clone https://github.com/anejakartik/docubrain.git
cd docubrain
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 demo.py
```

Or run the API:

```bash
uvicorn server.main:app --reload
# then: curl -F file=@sample_data/sample_contract.pdf http://localhost:8000/ingest
```

## Architecture

See [docs/architecture.md](./docs/architecture.md). Stack: Python + PyMuPDF + FastAPI, pluggable embedding/generation backends, in-memory vector search for v0.1 (Qdrant planned for the persistent/production backend).

## What's next

See [ROADMAP.md](./ROADMAP.md) — the biggest post-MVP item is layout-aware extraction (tables and multi-column text), so highlighting stays accurate on real-world documents, not just clean ones.

## Contributing

This is a personal portfolio project but PRs welcome. See [AGENTS.md](./AGENTS.md) if you're an AI coding agent working on this repo.

## License

MIT. See [LICENSE](./LICENSE).
