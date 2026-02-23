"""Vector search router."""

import logging
from fastapi import APIRouter, HTTPException, Query
from models.schemas import (
    SearchRequest, SearchResponse, SearchResult,
    DocumentListResponse, DocumentInfo, DocumentDetailResponse, DocumentChunk
)
from services.embedding_service import get_embedding_service
from services.qdrant_service import get_qdrant_service
from exceptions import SearchError, DocumentNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest) -> SearchResponse:
    """
    Perform vector similarity search.

    Process:
    1. Generate embedding for the search query
    2. Search Qdrant for similar vectors
    3. Apply metadata filters if provided
    4. Return ranked results with snippets
    """
    try:
        embedding_service = get_embedding_service()
        qdrant_service = get_qdrant_service()

        query_embedding = await embedding_service.generate_embedding_async(request.query)

        filters = None
        if request.filters:
            filters = {
                "category": request.filters.category,
                "tags": request.filters.tags
            }

        results = await qdrant_service.search_async(
            query_embedding=query_embedding,
            limit=request.limit,
            filters=filters,
            user_id=request.user_id
        )

        search_results = []
        for result in results:
            text = result.get("text", "")
            snippet = text[:200] + "..." if len(text) > 200 else text

            search_results.append(SearchResult(
                id=result["id"],
                document_id=result["document_id"],
                title=result["title"],
                snippet=snippet,
                score=result["score"],
                metadata=result.get("metadata", {})
            ))

        return SearchResponse(
            results=search_results,
            total_count=len(search_results),
            query=request.query
        )

    except Exception as e:
        logger.exception("Search failed for query='%s'", request.query)
        raise SearchError()


@router.get("/collection/info")
async def get_collection_info():
    """Get information about the vector collection."""
    try:
        qdrant_service = get_qdrant_service()
        info = await qdrant_service.get_collection_info_async()
        return info
    except Exception as e:
        logger.exception("Failed to get collection info")
        raise SearchError("Failed to retrieve collection info")


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
):
    """
    Get a paginated list of all ingested documents.

    Returns document info including title, chunk count, and metadata.
    Documents are grouped by document_id.
    """
    try:
        qdrant_service = get_qdrant_service()
        docs, total_count = await qdrant_service.list_all_documents_async(
            page=page,
            page_size=page_size,
        )

        document_infos = [
            DocumentInfo(
                document_id=doc["document_id"],
                title=doc["title"],
                chunk_count=doc["chunk_count"],
                created_at=doc["created_at"],
                metadata=doc["metadata"]
            )
            for doc in docs
        ]

        return DocumentListResponse(
            documents=document_infos,
            total_count=total_count,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.exception("Failed to list documents")
        raise SearchError("Failed to list documents")


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document_by_id(document_id: str):
    """
    Get all chunks for a specific document by document_id.

    Returns the full content of all chunks belonging to the document.
    """
    try:
        qdrant_service = get_qdrant_service()
        chunks = await qdrant_service.get_document_chunks_async(document_id)

        if not chunks:
            raise DocumentNotFoundError(document_id)

        title = chunks[0].get("title", "") if chunks else ""

        chunk_models = [
            DocumentChunk(
                chunk_id=chunk["chunk_id"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                created_at=chunk["created_at"],
                metadata=chunk["metadata"]
            )
            for chunk in chunks
        ]

        return DocumentDetailResponse(
            document_id=document_id,
            title=title,
            chunks=chunk_models,
            total_chunks=len(chunk_models)
        )

    except (HTTPException, DocumentNotFoundError):
        raise
    except Exception as e:
        logger.exception("Failed to get document id='%s'", document_id)
        raise SearchError("Failed to retrieve document")
