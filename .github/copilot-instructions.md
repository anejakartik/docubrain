# Copilot instructions for docubrain

> Same intent as [../AGENTS.md](../AGENTS.md), Copilot-format.

## Product context

This repo is **docubrain** — PDF answers with a verifiable page citation, for SMBs (law firms, insurance brokers, clinics) drowning in PDFs. See [PRODUCT.md](../PRODUCT.md).

- **Target user:** Ops/knowledge lead with thousands of PDFs and no time to search them by hand
- **Their pain:** Generic RAG ignores document structure; answers without citations aren't trustworthy in a legal/compliance context
- **Our wedge:** Every answer traces back to an exact page; works with zero API keys out of the box

## Code style

- Python: type hints, pytest
- Small focused changes
- No speculative abstractions

## Repo layout

```
docubrain/
├── README.md, PRODUCT.md, ROADMAP.md, AGENTS.md, DEMO.md
├── docubrain/       # core library: models, ingest, embeddings, store, qa
├── server/          # FastAPI app (/ingest, /ask)
├── scripts/         # sample-data generation
├── sample_data/     # bundled sample PDF for demo + tests
├── tests/
└── demo.py          # zero-API-key end-to-end demo
```

## Hard constraints

- An `Answer` always has at least one cited page — enforced in `docubrain/models.py`, don't weaken it
- Chunks never cross a page boundary
- `demo.py` and the full test suite must run with zero API keys (StubEmbedder only)
- No heavyweight ML dependency in the base install
