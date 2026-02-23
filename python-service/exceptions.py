"""Custom exception types for structured error handling."""

import logging

logger = logging.getLogger(__name__)


class VectorFlowError(Exception):
    """Base exception for VectorFlow operations."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class IngestionError(VectorFlowError):
    """Raised when document ingestion fails."""

    def __init__(self, message: str = "Document ingestion failed"):
        super().__init__(message, status_code=500)


class SearchError(VectorFlowError):
    """Raised when vector search fails."""

    def __init__(self, message: str = "Search operation failed"):
        super().__init__(message, status_code=500)


class DocumentNotFoundError(VectorFlowError):
    """Raised when a requested document cannot be found."""

    def __init__(self, document_id: str):
        super().__init__(f"Document not found: {document_id}", status_code=404)


class LLMError(VectorFlowError):
    """Raised when the LLM/RAG pipeline fails."""

    def __init__(self, message: str = "Failed to generate answer"):
        super().__init__(message, status_code=500)


class EmbeddingError(VectorFlowError):
    """Raised when embedding generation fails."""

    def __init__(self, message: str = "Embedding generation failed"):
        super().__init__(message, status_code=500)


class InvalidRequestError(VectorFlowError):
    """Raised for invalid client input that passes schema validation."""

    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, status_code=400)
