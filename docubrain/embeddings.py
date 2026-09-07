"""Pluggable embedding backends.

Same philosophy as evalstack's non-LLM smoke judges: the default path
(`StubEmbedder`) needs no API key, so demo.py and the test suite never
depend on a live LLM budget. `OpenAIEmbedder` is the real backend for
production use.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

# Minimal stopword list — just enough that common function words don't
# drown out the content words that actually distinguish one page from
# another. Not linguistically complete; StubEmbedder is a smoke-test
# embedder, not a real model (see class docstring).
_STOPWORDS = frozenset(
    """
    a an the this that these those is are was were be been being
    to of in on for with as at by from up down out if or and but not
    it its it's their they he she his her him you your we our i
    do does did has have had will would shall should can could may
    might must into over under about between within without
    """.split()
)


class Embedder(Protocol):
    """Anything that turns text into a fixed-length vector."""

    dimensions: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class StubEmbedder:
    """Deterministic, dependency-free embedder for demo/CI use.

    Hashes overlapping word shingles into a fixed-size vector. It is not
    a real semantic embedding — but it's stable and locally consistent
    enough that near-duplicate/overlapping text scores higher similarity
    than unrelated text, which is all the demo and test suite need.
    """

    dimensions = 256

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        raw_words = re.findall(r"[a-z0-9']+", text.lower())
        # Crude prefix "stemming" (6 chars) so morphological variants —
        # confidential/confidentiality/confidence, terminate/termination —
        # collapse to the same token instead of being unrelated hashes.
        # Not a real stemmer; good enough for a dependency-free smoke embedder.
        words = [
            (w[:6] if len(w) > 6 else w) for w in raw_words if w not in _STOPWORDS
        ]
        shingles = words + [f"{a}_{b}" for a, b in zip(words, words[1:])]
        if not shingles:
            return vec
        for shingle in shingles:
            digest = hashlib.sha256(shingle.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vec[bucket] += sign
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class OpenAIEmbedder:
    """Real embedding backend via the OpenAI API. Requires OPENAI_API_KEY."""

    dimensions = 1536  # text-embedding-3-small

    def __init__(self, model: str = "text-embedding-3-small", client=None) -> None:
        self.model = model
        if client is not None:
            self._client = client
        else:
            from openai import OpenAI  # imported lazily — optional dependency

            self._client = OpenAI()

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]
