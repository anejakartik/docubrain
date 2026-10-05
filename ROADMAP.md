# Roadmap — docubrain

> Updated weekly. Add a dated entry per shipped feature. Feeds the content engine — each `[x]` is a potential LinkedIn post.

## Shipping log (newest on top)

### 2026-09-07 — v0.1: page-cited Q&A, zero API keys required
- [x] PDF ingestion with per-page text extraction + page-bounded chunking
- [x] Pluggable `Embedder` protocol — `StubEmbedder` (deterministic, no API key) + `OpenAIEmbedder`
- [x] In-memory `VectorStore` with cosine similarity search
- [x] `ask()` — always returns a cited `Answer`, enforced at the data-model level
- [x] FastAPI service (`/ingest`, `/ask`, `/documents`, `/healthz`)
- [x] `demo.py` — end-to-end, zero API keys, bundled sample contract
- [x] 24 passing tests, all against the zero-API-key path
- Notes: the first version of `StubEmbedder` (raw word+bigram hashing) scored badly on the demo's own sample questions — 1 of 4 answers cited the wrong page. Fixed by adding stopword filtering and a crude 6-char prefix "stem" so morphological variants (confidential/confidentiality/confidence) collapse together. Worth remembering for any future hash-based smoke embedder: raw bag-of-words hashing is noisier than it looks on short documents.

<!-- copy the block above for each new week -->

---

### 2026-09-14 — live demo deployed, custom domain live
- [x] Deployed to Fly.io: `docubrain-kartik.fly.dev` — pre-seeded with the sample contract on boot so it's queryable with no setup
- [x] Interactive demo landing page at `/` (ask questions against the sample contract or upload your own PDF) with a link out to `/docs` for the raw API
- [x] Custom domain live: **https://docubrain.kartikaneja.com** — `vercel.json` pure rewrite-proxy (no build step, same pattern as tracelens) + CNAME at the registrar, done by Kartik
- Notes: this closes out the ROADMAP's original P0 deploy item end-to-end.

### 2026-10-05 — page-region highlighting
- [x] Every chunk now carries a `bbox` (PDF point coords) located at ingest time via `page.search_for()`, with a line-by-line fallback; `None` when there's no text layer
- [x] `/ask` returns `citations: [{page, bbox}]` alongside `cited_pages`; new `GET /documents/{doc_id}/pages/{n}/image?highlight=x0,y0,x1,y1` renders the cited page as a PNG with the region boxed
- [x] Demo UI shows the highlighted page thumbnail under every answer
- Notes: found + fixed two bugs along the way — the sample PDF generator used `insert_text()`, which silently truncated every section mid-sentence (no wrapping), and PyMuPDF wraps negative page indexes, so page 0 would have rendered the *last* page instead of 404ing. Uploaded PDFs now persist to disk (keyed by doc_id) since rendering needs the original bytes.

## Short-term — next 4 weeks

- [ ] **P0 / Real layout-aware extraction** — swap flat `page.get_text()` for a layout-preserving extractor (Unstructured or PyMuPDF's block/dict mode) so tables and multi-column text don't get mangled *(est. 2-3 days · drives a "why generic RAG breaks on real documents" post)*
- [x] **P1 / Page-region highlighting** — shipped 2026-10-05 (see above)
- [ ] **P1 / Generative answers via a real LLM** — wire up an `OpenAIGenerator` alongside `OpenAIEmbedder`, keep extractive mode as the always-available fallback

## 3-month

- [ ] Multi-document corpora with per-document and cross-document search
- [ ] Persistent vector store (Qdrant) replacing the in-memory `VectorStore`
- [ ] Minimal web UI (upload + chat) instead of API-only
- [ ] Retrieval eval suite reusing evalstack — measure "did we cite the right page" as a real regression-gated metric, not just spot-checked by hand

## 6-month

- [ ] Multi-tenant indexing (per-workspace isolation)
- [ ] Hand-written note / scanned-signature OCR support
- [ ] Chart/diagram understanding
- [ ] Slack/email integration for asking questions without opening the UI
