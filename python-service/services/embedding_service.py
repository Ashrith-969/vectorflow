"""Embedding service using OpenAI API.

Primary interface is the ``*_async`` methods which use AsyncOpenAI.
Synchronous methods are kept in a dedicated section at the bottom for
scripts / tests / CLI tools.  ``chunk_text`` and ``count_tokens`` are
CPU-only helpers and work in both contexts.
"""

import tiktoken
from functools import lru_cache
from openai import OpenAI, AsyncOpenAI
from typing import List, Tuple
from config import get_settings


class EmbeddingService:
    """Service for generating embeddings and chunking text."""

    def __init__(self):
        settings = get_settings()
        self.async_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._sync_client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

    # ------------------------------------------------------------------
    # Async API  (primary -- used by FastAPI routers)
    # ------------------------------------------------------------------

    async def generate_embedding_async(self, text: str) -> List[float]:
        """Generate embedding for a single text asynchronously."""
        response = await self.async_client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def generate_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch asynchronously."""
        response = await self.async_client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    # ------------------------------------------------------------------
    # CPU-only helpers  (no I/O -- safe on any thread / event loop)
    # ------------------------------------------------------------------

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text."""
        return len(self.tokenizer.encode(text))

    def chunk_text(self, text: str, title: str = "") -> List[Tuple[str, int]]:
        """Split text into chunks with overlap.

        Returns list of (chunk_text, token_count) tuples.
        CPU-bound via tiktoken; callers in async context should wrap this
        in ``asyncio.to_thread()`` for large documents.
        """
        tokens = self.tokenizer.encode(text)

        if len(tokens) <= self.chunk_size:
            return [(text, len(tokens))]

        chunks = []
        start = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            if title:
                chunk_text = f"[Document: {title}]\n{chunk_text}"

            chunks.append((chunk_text, len(chunk_tokens)))
            start = end - self.chunk_overlap

        return chunks

    # ------------------------------------------------------------------
    # Synchronous API  (for scripts, tests, CLI -- NOT used by routers)
    # ------------------------------------------------------------------

    def generate_embedding(self, text: str) -> List[float]:
        """Synchronous version of generate_embedding_async."""
        response = self._sync_client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Synchronous version of generate_embeddings_async."""
        response = self._sync_client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service singleton (thread-safe via lru_cache)."""
    return EmbeddingService()
