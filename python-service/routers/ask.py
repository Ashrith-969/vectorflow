"""RAG-based question answering router."""

import logging
from fastapi import APIRouter
from models.schemas import AskRequest, AskResponse, Source
from services.llm_service import get_llm_service
from exceptions import LLMError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ask"])


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    """
    Answer a question using RAG (Retrieval-Augmented Generation).

    Process:
    1. Generate embedding for the question
    2. Search Qdrant for relevant document chunks
    3. Construct context from retrieved chunks
    4. Send context + question to LLM
    5. Return answer with source citations
    """
    try:
        llm_service = get_llm_service()

        result = await llm_service.ask_async(
            question=request.question,
            max_sources=request.max_sources
        )

        sources = [
            Source(
                document_id=s["document_id"],
                title=s["title"],
                snippet=s["snippet"],
                relevance=s["relevance"]
            )
            for s in result["sources"]
        ]

        return AskResponse(
            answer=result["answer"],
            sources=sources,
            confidence=result["confidence"],
            question=request.question
        )

    except Exception as e:
        logger.exception("RAG pipeline failed for question='%s'", request.question)
        raise LLMError()
