# Product — docubrain

> The "why" behind this repo. Read first if you're an AI agent contributing.

## Target user

**Persona:** Ops/knowledge lead at a small law firm, insurance broker, or clinic — thousands of PDFs (contracts, claims, intake forms), a handful of people who need answers out of them fast.

**Job they're trying to do:** Ask a plain-English question about a pile of PDFs and get an answer with a citation they can actually verify — not a hallucinated summary they have to double-check by hand.

**Current workflow:** Ctrl-F through individual PDFs, or paying an OCR/document-review shop by the hour. ChatGPT can't ingest the whole corpus, and pasting excerpts loses the page/section context that matters in a contract or claim.

## The pain

1. Generic RAG demos are built on blog-post text; real documents have layout — tables, clauses, scanned signatures — and flat-text chunking silently mangles that structure.
2. Answers without a verifiable citation are useless in a legal/compliance context — "trust me" isn't good enough when the answer feeds a real decision.
3. OCR/document-review services are priced for enterprise budgets, not a 5-person brokerage or clinic.

What it costs them: hours of manual search per week, and real risk when a missed clause or claim detail slips through.

## Existing alternatives — and why they fall short

| Alternative | What it does | Why it doesn't fit this persona |
|---|---|---|
| ChatGPT / Claude with pasted text | Q&A over whatever you paste | Can't ingest thousands of PDFs; no persistent corpus; no citation back to source |
| Enterprise OCR/document-review vendors | Full-service review pipelines | Priced and scoped for enterprise, not SMB budgets |
| Generic open-source RAG templates | Text-only chunk + embed + retrieve | Ignore page/layout structure; citations point to "a chunk," not a page a human can open and check |

## Our wedge

- Every answer traces back to a specific page in the source PDF — not just "chunk 47."
- Works without an API key out of the box (deterministic stub embedder + extractive answering) so the demo and test suite never depend on a live LLM budget — same "smoke judge" philosophy as evalstack.
- Self-hostable, MIT-licensed, free-tier deployable — not priced for enterprise.

## MVP scope (what we will ship first)

**Must-have:**
- PDF ingestion: extract text per page (PyMuPDF), chunk with page-number provenance kept on every chunk
- Pluggable embedding layer: deterministic `StubEmbedder` (no API key, for CI/demo) + `OpenAIEmbedder` (real, optional)
- Vector search over ingested chunks (cosine similarity), returning top-k chunks with page numbers
- `/ingest` and `/ask` API (FastAPI) + a `demo.py` that runs end-to-end with zero API keys
- Answer includes the cited page number(s) always — never a bare answer with no attribution

**Out of scope for MVP** (handled in [ROADMAP.md](./ROADMAP.md)):
- Multi-modal layout/image-region indexing (the original full C3 vision — Unstructured/Donut/CLIP) — v0.1 is text+page-number only, real layout-aware highlighting is the biggest post-MVP item
- Multi-tenant indexing, hand-written notes, chart/diagram understanding
- Web UI (v0.1 is API + CLI only)

## Success metric

- Demo answers a question against a real sample PDF corpus with a correct page citation, verified by hand
- Test suite passes with zero external API dependencies (StubEmbedder path)

## What success looks like in 6 months

- Live demo at docubrain.kartikaneja.com with a public sample corpus
- Real page-region highlighting (not just page number) shipped
- Cited in a hiring conversation alongside the rest of the trilogy/flagship set

## Non-goals

- Not competing with enterprise document-review suites (no workflow/case-management features)
- Not a general-purpose RAG framework — scoped specifically to "PDF in, cited answer out"
