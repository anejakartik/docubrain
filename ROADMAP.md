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

### 2026-09-14 — live demo deployed
- [x] Deployed to Fly.io: https://docubrain-kartik.fly.dev — pre-seeded with the sample contract on boot so it's queryable with no setup
- Notes: custom domain (`docubrain.kartikaneja.com`) not wired up yet — no DNS/Cloudflare access from this environment; app runs fine on the `fly.dev` hostname in the meantime.

## Short-term — next 4 weeks

- [ ] **P0 / Custom domain** — point `docubrain.kartikaneja.com` at the Fly app *(needs Cloudflare/DNS access)*
- [ ] **P0 / Real layout-aware extraction** — swap flat `page.get_text()` for a layout-preserving extractor (Unstructured or PyMuPDF's block/dict mode) so tables and multi-column text don't get mangled *(est. 2-3 days · drives a "why generic RAG breaks on real documents" post)*
- [ ] **P1 / Page-region highlighting** — render the cited page as an image with the matching region boxed, not just a page number *(est. 2-3 days — the single biggest product upgrade)*
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
