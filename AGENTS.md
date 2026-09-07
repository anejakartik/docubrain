# AGENTS.md — instructions for AI coding agents

## Before you touch code

1. Read [PRODUCT.md](./PRODUCT.md) — who this is for + the wedge
2. Read the top of [ROADMAP.md](./ROADMAP.md) — what's prioritized
3. Check open issues + PRs to avoid duplication

## Coding conventions

- Python: type hints, pytest. Keep `docubrain/` dependency-light — it should not require an LLM API key to import or to run its own test suite.
- Small focused PRs
- Match existing patterns; no speculative abstractions

## Repo-specific guardrails

- **An `Answer` must always cite at least one page.** This is enforced in `docubrain/models.py`'s `Answer.__post_init__` — do not weaken or remove that check. There is no acceptable code path that returns an answer with zero citations.
- **Chunking must never cross a page boundary.** A chunk's `page` field has to be exact, not "somewhere around page N."
- **The zero-API-key path must keep working.** `demo.py`, and the full test suite, must run end-to-end using only `StubEmbedder` — no network calls, no API key required. `OpenAIEmbedder` / a real generator are opt-in additions, never a hard dependency for the base functionality.
- Do not add a heavyweight ML dependency (torch, transformers, etc.) to the base install just to improve `StubEmbedder` — if you want stronger embeddings, that belongs behind the same pluggable `Embedder` protocol as an optional backend, same as `OpenAIEmbedder`.

## Commits & PRs

- Imperative-mood commit messages focused on *why*
- PR description: problem (1–2 lines) + change (2–3 lines) + test plan
- Squash on merge

## Deployment

See [DEMO.md](./DEMO.md) once a live deploy exists — v0.1 is local/API-only, no live demo URL yet (see ROADMAP.md).
