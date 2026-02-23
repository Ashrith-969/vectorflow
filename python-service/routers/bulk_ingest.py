"""Bulk document ingestion router with async support."""

import logging
import uuid
import asyncio
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.schemas import IngestRequest, IngestResponse, DocumentStatus
from services.embedding_service import get_embedding_service
from services.qdrant_service import get_qdrant_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["bulk-ingestion"])


class BulkIngestRequest(BaseModel):
    """Request schema for bulk document ingestion."""
    documents: List[IngestRequest]


class BulkIngestResponse(BaseModel):
    """Response schema for bulk ingestion."""
    total: int
    successful: int
    failed: int
    results: List[IngestResponse]


async def ingest_single_document_async(request: IngestRequest) -> IngestResponse:
    """Ingest a single document asynchronously."""
    try:
        document_id = str(uuid.uuid4())

        embedding_service = get_embedding_service()
        qdrant_service = get_qdrant_service()

        chunks_with_counts = await asyncio.to_thread(
            embedding_service.chunk_text,
            request.content,
            request.title,
        )

        if not chunks_with_counts:
            return IngestResponse(
                document_id=document_id,
                title=request.title,
                chunk_count=0,
                status=DocumentStatus.FAILED,
                message="Document content is empty or could not be processed"
            )

        chunk_texts = [chunk for chunk, _ in chunks_with_counts]
        embeddings = await embedding_service.generate_embeddings_async(chunk_texts)

        chunk_count = await qdrant_service.upsert_chunks_async(
            document_id=document_id,
            title=request.title,
            chunks=chunk_texts,
            embeddings=embeddings,
            metadata=request.metadata
        )

        return IngestResponse(
            document_id=document_id,
            title=request.title,
            chunk_count=chunk_count,
            status=DocumentStatus.COMPLETED,
            message=f"Successfully ingested document with {chunk_count} chunks"
        )

    except Exception as e:
        logger.exception("Bulk ingest failed for title='%s'", request.title)
        return IngestResponse(
            document_id=str(uuid.uuid4()),
            title=request.title,
            chunk_count=0,
            status=DocumentStatus.FAILED,
            message="Document ingestion failed"
        )


@router.post("/bulk-ingest", response_model=BulkIngestResponse)
async def bulk_ingest_documents(request: BulkIngestRequest) -> BulkIngestResponse:
    """
    Ingest multiple documents in parallel asynchronously.

    Process:
    1. Receive list of documents
    2. Process all documents in parallel
    3. Return summary of results

    This endpoint uses true async processing with asyncio.gather()
    to ingest multiple documents concurrently, dramatically improving
    performance for bulk ingestion workloads.
    """
    if not request.documents:
        raise HTTPException(
            status_code=400,
            detail="No documents provided for ingestion"
        )

    results = await asyncio.gather(
        *[ingest_single_document_async(doc) for doc in request.documents],
        return_exceptions=False
    )

    successful = sum(1 for r in results if r.status == DocumentStatus.COMPLETED)
    failed = sum(1 for r in results if r.status == DocumentStatus.FAILED)

    return BulkIngestResponse(
        total=len(results),
        successful=successful,
        failed=failed,
        results=results
    )
