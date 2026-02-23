"""LLM service for RAG-based question answering.

Primary interface is the set of ``*_async`` methods which use AsyncOpenAI
and the native async Qdrant/embedding services.  Synchronous methods are
kept in a dedicated section at the bottom for scripts / tests / CLI tools.
"""

import math
from functools import lru_cache
from typing import List, Dict, Any, Tuple

from openai import OpenAI, AsyncOpenAI
from config import get_settings
from services.embedding_service import get_embedding_service
from services.qdrant_service import get_qdrant_service


class LLMService:
    """Service for LLM-powered question answering with RAG."""

    SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context.

Rules:
1. Only answer based on the provided context
2. If the context doesn't contain enough information, say so
3. Be concise and direct in your answers
4. Cite the source documents when relevant
5. If you're uncertain, express your uncertainty

Context will be provided in the following format:
[Source: Document Title]
Content...
"""

    def __init__(self):
        settings = get_settings()
        self.async_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._sync_client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.embedding_service = get_embedding_service()
        self.qdrant_service = get_qdrant_service()

    # ------------------------------------------------------------------
    # Async API  (primary -- used by FastAPI routers)
    # ------------------------------------------------------------------

    async def retrieve_context_async(
        self,
        question: str,
        max_sources: int = 5,
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """Non-blocking retrieval: embed the question then search Qdrant."""
        query_embedding = await self.embedding_service.generate_embedding_async(question)
        results = await self.qdrant_service.search_async(
            query_embedding=query_embedding,
            limit=max_sources,
        )
        return results, query_embedding

    async def generate_answer_async(
        self,
        question: str,
        context: str,
    ) -> Tuple[str, float]:
        """Non-blocking answer generation using AsyncOpenAI."""
        messages = self._build_messages(question, context)

        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=500,
            logprobs=True,
            top_logprobs=1,
        )

        answer = response.choices[0].message.content
        confidence = self._calculate_confidence_from_logprobs(response, answer)
        return answer, confidence

    async def ask_async(
        self,
        question: str,
        max_sources: int = 5,
    ) -> Dict[str, Any]:
        """Full async RAG pipeline: retrieve context, generate answer."""
        results, _ = await self.retrieve_context_async(question, max_sources)

        if not results:
            return {
                "answer": "I couldn't find any relevant information to answer your question. "
                          "Please try rephrasing or ensure relevant documents have been ingested.",
                "sources": [],
                "confidence": 0.0,
            }

        context = self.format_context(results)
        answer, confidence = await self.generate_answer_async(question, context)
        return {
            "answer": answer,
            "sources": self._build_sources(results),
            "confidence": confidence,
        }

    # ------------------------------------------------------------------
    # Shared helpers  (pure logic, no I/O)
    # ------------------------------------------------------------------

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results into context for the LLM."""
        context_parts = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "Unknown")
            text = result.get("text", "")
            context_parts.append(f"[Source {i}: {title}]\n{text}\n")
        return "\n".join(context_parts)

    def _build_messages(self, question: str, context: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]

    def _calculate_confidence_from_logprobs(self, response, answer: str) -> float:
        """Derive a confidence score from the mean token log-probability.

        Falls back to a heuristic if logprobs are unavailable.
        """
        logprobs_content = None
        choice = response.choices[0]
        if choice.logprobs and choice.logprobs.content:
            logprobs_content = choice.logprobs.content

        if logprobs_content:
            log_probs = [t.logprob for t in logprobs_content]
            mean_logprob = sum(log_probs) / len(log_probs)
            confidence = math.exp(mean_logprob)
        else:
            confidence = self._heuristic_confidence(answer)

        return round(max(0.0, min(1.0, confidence)), 2)

    @staticmethod
    def _heuristic_confidence(answer: str) -> float:
        """Fallback heuristic when logprobs are unavailable."""
        uncertainty_phrases = [
            "i don't know",
            "i'm not sure",
            "unclear",
            "cannot determine",
            "no information",
            "not enough context",
        ]
        answer_lower = answer.lower()
        confidence = 0.85
        for phrase in uncertainty_phrases:
            if phrase in answer_lower:
                confidence -= 0.15
        return max(0.1, min(1.0, confidence))

    @staticmethod
    def _build_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        for result in results:
            text = result.get("text", "")
            snippet = text[:150] + "..." if len(text) > 150 else text
            sources.append({
                "document_id": result.get("document_id", ""),
                "title": result.get("title", "Unknown"),
                "snippet": snippet,
                "relevance": result.get("score", 0.0),
            })
        return sources

    # ------------------------------------------------------------------
    # Synchronous API  (for scripts, tests, CLI -- NOT used by routers)
    # ------------------------------------------------------------------

    def retrieve_context(
        self,
        question: str,
        max_sources: int = 5,
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """Synchronous version of retrieve_context_async."""
        query_embedding = self.embedding_service.generate_embedding(question)
        results = self.qdrant_service.search(
            query_embedding=query_embedding,
            limit=max_sources,
        )
        return results, query_embedding

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> Tuple[str, float]:
        """Synchronous version of generate_answer_async."""
        messages = self._build_messages(question, context)

        response = self._sync_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=500,
            logprobs=True,
            top_logprobs=1,
        )

        answer = response.choices[0].message.content
        confidence = self._calculate_confidence_from_logprobs(response, answer)
        return answer, confidence

    def ask(
        self,
        question: str,
        max_sources: int = 5,
    ) -> Dict[str, Any]:
        """Synchronous version of ask_async."""
        results, _ = self.retrieve_context(question, max_sources)

        if not results:
            return {
                "answer": "I couldn't find any relevant information to answer your question. "
                          "Please try rephrasing or ensure relevant documents have been ingested.",
                "sources": [],
                "confidence": 0.0,
            }

        context = self.format_context(results)
        answer, confidence = self.generate_answer(question, context)
        return {
            "answer": answer,
            "sources": self._build_sources(results),
            "confidence": confidence,
        }


@lru_cache()
def get_llm_service() -> LLMService:
    """Get or create LLM service singleton (thread-safe via lru_cache)."""
    return LLMService()
