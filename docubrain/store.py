"""In-memory vector store with brute-force cosine similarity search.

Fine at demo/small-corpus scale (thousands of chunks). Swapping in a real
vector DB (Qdrant is the planned production backend) is a storage-layer
change only — nothing above this module should need to know which one
is in use. See ROADMAP.md.
"""

from __future__ import annotations

import numpy as np

from docubrain.embeddings import Embedder
from docubrain.models import Chunk, Document


class VectorStore:
    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._chunks: list[Chunk] = []
        self._vectors: np.ndarray | None = None

    def add_document(self, document: Document) -> None:
        if not document.chunks:
            return
        new_vectors = np.array(
            self._embedder.embed([c.text for c in document.chunks]), dtype=np.float32
        )
        self._chunks.extend(document.chunks)
        self._vectors = (
            new_vectors
            if self._vectors is None
            else np.vstack([self._vectors, new_vectors])
        )

    def __len__(self) -> int:
        return len(self._chunks)

    def search(
        self, query: str, top_k: int = 5, *, doc_id: str | None = None
    ) -> list[tuple[Chunk, float]]:
        """Top-`top_k` chunks by cosine similarity, optionally restricted to
        one document. The restriction happens before ranking, not after —
        filtering a global top-k afterwards drops the requested document
        entirely whenever another document's chunks outscore it."""
        if self._vectors is None or len(self._chunks) == 0:
            return []
        query_vec = np.array(self._embedder.embed([query])[0], dtype=np.float32)
        query_norm = np.linalg.norm(query_vec) or 1.0
        corpus_norms = np.linalg.norm(self._vectors, axis=1)
        corpus_norms[corpus_norms == 0] = 1.0
        scores = (self._vectors @ query_vec) / (corpus_norms * query_norm)

        candidates = np.arange(len(self._chunks))
        if doc_id is not None:
            candidates = np.array(
                [i for i, c in enumerate(self._chunks) if c.doc_id == doc_id], dtype=int
            )
            if candidates.size == 0:
                return []
        ranked = candidates[np.argsort(-scores[candidates])][:top_k]
        return [(self._chunks[i], float(scores[i])) for i in ranked]
