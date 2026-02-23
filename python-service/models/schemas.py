"""Pydantic schemas for request/response models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============== Ingest Schemas ==============

class IngestRequest(BaseModel):
    """Request schema for document ingestion."""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    user_id: Optional[str] = None


class IngestResponse(BaseModel):
    """Response schema for document ingestion."""
    document_id: str
    title: str
    chunk_count: int
    status: DocumentStatus
    message: str


# ============== Search Schemas ==============

class SearchFilter(BaseModel):
    """Filters for search queries."""
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class SearchRequest(BaseModel):
    """Request schema for vector search."""
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    filters: Optional[SearchFilter] = None
    user_id: Optional[str] = None


class SearchResult(BaseModel):
    """Individual search result."""
    id: str
    document_id: str
    title: str
    snippet: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response schema for vector search."""
    results: List[SearchResult]
    total_count: int
    query: str


# ============== Ask (RAG) Schemas ==============

class AskRequest(BaseModel):
    """Request schema for RAG-based question answering."""
    question: str = Field(..., min_length=1)
    collection_id: Optional[str] = None
    max_sources: int = Field(default=5, ge=1, le=10)
    user_id: Optional[str] = None


class Source(BaseModel):
    """Source document for an answer."""
    document_id: str
    title: str
    snippet: str
    relevance: float


class AskResponse(BaseModel):
    """Response schema for RAG-based answers."""
    answer: str
    sources: List[Source]
    confidence: float
    question: str


# ============== Document Management Schemas ==============

class DocumentInfo(BaseModel):
    """Information about an ingested document."""
    document_id: str
    title: str
    chunk_count: int
    created_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentListResponse(BaseModel):
    """Response schema for listing all documents."""
    documents: List[DocumentInfo]
    total_count: int
    page: int = 1
    page_size: int = 20


class DocumentChunk(BaseModel):
    """A single chunk from a document."""
    chunk_id: str
    chunk_index: int
    text: str
    created_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentDetailResponse(BaseModel):
    """Response with all chunks for a document."""
    document_id: str
    title: str
    chunks: List[DocumentChunk]
    total_chunks: int

# ============== Health Check ==============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    qdrant_connected: bool
    postgres_connected: bool
    version: str = "1.0.0"

