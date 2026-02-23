"""Document ingestion router."""

import asyncio
import logging
import uuid
from fastapi import APIRouter, HTTPException
from models.schemas import IngestRequest, IngestResponse, DocumentStatus
from services.embedding_service import get_embedding_service
from services.qdrant_service import get_qdrant_service
from exceptions import IngestionError, InvalidRequestError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ingestion"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest) -> IngestResponse:
    """
    Ingest a document: chunk, embed, and store in Qdrant.

    Process:
    1. Split document into chunks (500 tokens with 50 token overlap)
    2. Generate embeddings for each chunk using OpenAI
    3. Store vectors with metadata in Qdrant
    """
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
            raise InvalidRequestError("Document content is empty or could not be processed")

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

    except (HTTPException, InvalidRequestError):
        raise
    except Exception as e:
        logger.exception("Document ingestion failed for title='%s'", request.title)
        raise IngestionError()


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and all its chunks from Qdrant."""
    try:
        qdrant_service = get_qdrant_service()
        await qdrant_service.delete_by_document_id_async(document_id)

        return {"message": f"Document {document_id} deleted successfully"}

    except Exception as e:
        logger.exception("Failed to delete document id='%s'", document_id)
        raise IngestionError("Failed to delete document")
