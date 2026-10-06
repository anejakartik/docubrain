"""Question answering over an ingested corpus.

Every path here returns an `Answer` with at least one cited page — see
`models.Answer.__post_init__`. There is no code path that returns a bare
answer with no citation; that guarantee is the whole point of the product.

Default mode is extractive (no LLM call, no API key): the most relevant
chunk is returned verbatim with its page number. An optional `generator`
callable can be passed in to produce a synthesized answer instead, for
callers with an LLM budget — the citation guarantee holds either way.
"""

from __future__ import annotations

from typing import Callable, Optional

from docubrain.models import Answer, Chunk
from docubrain.store import VectorStore

Generator = Callable[[str, list[Chunk]], str]


def ask(
    question: str,
    store: VectorStore,
    *,
    doc_id: str | None = None,
    top_k: int = 3,
    generator: Optional[Generator] = None,
) -> Answer:
    """Answer `question` against everything ingested into `store`.

    Raises ValueError if the store has no matching chunks — callers should
    treat that as "nothing ingested yet" / "no relevant content found",
    never fabricate a citation to cover for an empty result.
    """
    results = store.search(question, top_k=top_k, doc_id=doc_id)
    if not results:
        raise ValueError("No relevant content found for this question.")

    supporting_chunks = [c for c, _ in results]

    if generator is not None:
        text = generator(question, supporting_chunks)
        cited_pages = sorted({c.page for c in supporting_chunks})
    else:
        # Extractive mode returns exactly one chunk's text verbatim, so the
        # citation must point at that chunk's page only — citing every
        # retrieved chunk here would cite pages whose text never appears in
        # the answer, breaking the "cited or it doesn't exist" guarantee.
        best_chunk = supporting_chunks[0]
        text = best_chunk.text.strip()
        cited_pages = [best_chunk.page]

    return Answer(
        text=text,
        cited_pages=cited_pages,
        doc_id=supporting_chunks[0].doc_id,
        supporting_chunks=supporting_chunks,
    )
