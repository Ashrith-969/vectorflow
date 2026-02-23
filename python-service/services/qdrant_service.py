"""Qdrant vector database service.

Uses AsyncQdrantClient for native async I/O -- no thread pool, no GIL
contention, unlimited concurrency bounded only by the network and Qdrant
server capacity.  Synchronous helpers are kept in a dedicated section at
the bottom for use in scripts / tests / CLI tools.
"""

import uuid
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Any, Optional, Tuple

from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
)
from config import get_settings


class QdrantService:
    """Service for interacting with Qdrant vector database.

    Primary interface is the set of ``*_async`` methods which use the native
    ``AsyncQdrantClient``.  A synchronous ``client`` is kept for startup
    housekeeping (_ensure_collection) and is available via the ``sync_*``
    section for scripts / tests that run outside an event loop.
    """

    VECTOR_SIZE = 1536  # OpenAI ada-002 embedding size

    def __init__(self):
        settings = get_settings()
        self.async_client = AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self._sync_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection_name = settings.qdrant_collection
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist (runs at startup, sync is fine)."""
        collections = self._sync_client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self._sync_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Created Qdrant collection: {self.collection_name}")

    # ------------------------------------------------------------------
    # Async API  (primary -- used by FastAPI routers)
    # ------------------------------------------------------------------

    async def upsert_chunks_async(
        self,
        document_id: str,
        title: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict[str, Any] = None,
    ) -> int:
        """Insert document chunks with their embeddings."""
        points = self._build_points(document_id, title, chunks, embeddings, metadata)

        await self.async_client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        return len(points)

    async def search_async(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        search_filter = self._build_search_filter(filters)

        results = await self.async_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=search_filter,
            with_payload=True,
        )
        return self._format_search_results(results)

    async def delete_by_document_id_async(self, document_id: str) -> bool:
        """Delete all chunks for a document."""
        await self.async_client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )
        return True

    async def get_collection_info_async(self) -> Dict[str, Any]:
        """Get collection statistics."""
        info = await self.async_client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status.value,
        }

    async def list_all_documents_async(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Paginated list of unique documents.

        Scrolls only enough batches to fill the requested page instead of
        loading the entire collection into memory.
        """
        documents: Dict[str, Dict[str, Any]] = {}
        offset = None
        skip = (page - 1) * page_size

        while True:
            results, offset = await self.async_client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=offset,
                with_payload=["document_id", "title", "created_at", "metadata"],
                with_vectors=False,
            )

            if not results:
                break

            for point in results:
                doc_id = point.payload.get("document_id", "")
                if not doc_id:
                    continue
                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "title": point.payload.get("title", ""),
                        "created_at": point.payload.get("created_at", ""),
                        "metadata": point.payload.get("metadata", {}),
                        "chunk_count": 0,
                    }
                documents[doc_id]["chunk_count"] += 1

            if offset is None:
                break

            collected = len(documents)
            if collected >= skip + page_size:
                break

        all_docs = list(documents.values())
        total_count = len(all_docs)
        return all_docs[skip : skip + page_size], total_count

    async def get_document_chunks_async(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document."""
        results, _ = await self.async_client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
            limit=100,
            with_payload=True,
            with_vectors=False,
        )

        chunks = [
            {
                "chunk_id": str(point.id),
                "chunk_index": point.payload.get("chunk_index", 0),
                "text": point.payload.get("text", ""),
                "title": point.payload.get("title", ""),
                "created_at": point.payload.get("created_at", ""),
                "metadata": point.payload.get("metadata", {}),
            }
            for point in results
        ]
        chunks.sort(key=lambda x: x["chunk_index"])
        return chunks

    async def health_check_async(self) -> bool:
        """Check if Qdrant is reachable."""
        try:
            await self.async_client.get_collections()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Shared helpers  (pure logic, no I/O)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_points(
        document_id: str,
        title: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict[str, Any] = None,
    ) -> List[PointStruct]:
        """Build Qdrant PointStruct list from chunks and embeddings."""
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            payload = {
                "text": chunk,
                "document_id": document_id,
                "title": title,
                "chunk_index": i,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }
            points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
        return points

    @staticmethod
    def _build_search_filter(filters: Optional[Dict[str, Any]]) -> Optional[Filter]:
        """Translate a user-facing filter dict into a Qdrant Filter."""
        if not filters:
            return None

        conditions = []
        if filters.get("category"):
            conditions.append(
                FieldCondition(
                    key="metadata.category",
                    match=MatchValue(value=filters["category"]),
                )
            )
        if filters.get("tags"):
            conditions.append(
                FieldCondition(
                    key="metadata.tags",
                    match=MatchAny(any=filters["tags"]),
                )
            )
        return Filter(must=conditions) if conditions else None

    @staticmethod
    def _format_search_results(results) -> List[Dict[str, Any]]:
        """Convert Qdrant ScoredPoint objects to plain dicts."""
        return [
            {
                "id": str(r.id),
                "score": r.score,
                "document_id": r.payload.get("document_id", ""),
                "title": r.payload.get("title", ""),
                "text": r.payload.get("text", ""),
                "chunk_index": r.payload.get("chunk_index", 0),
                "metadata": r.payload.get("metadata", {}),
            }
            for r in results
        ]

    # ------------------------------------------------------------------
    # Synchronous API  (for scripts, tests, CLI -- NOT used by routers)
    # ------------------------------------------------------------------

    def upsert_chunks(
        self,
        document_id: str,
        title: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict[str, Any] = None,
    ) -> int:
        """Synchronous version of upsert_chunks_async."""
        points = self._build_points(document_id, title, chunks, embeddings, metadata)
        self._sync_client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Synchronous version of search_async."""
        search_filter = self._build_search_filter(filters)
        results = self._sync_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=search_filter,
            with_payload=True,
        )
        return self._format_search_results(results)

    def delete_by_document_id(self, document_id: str) -> bool:
        """Synchronous version of delete_by_document_id_async."""
        self._sync_client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )
        return True

    def get_collection_info(self) -> Dict[str, Any]:
        """Synchronous version of get_collection_info_async."""
        info = self._sync_client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status.value,
        }

    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Synchronous version of get_document_chunks_async."""
        results, _ = self._sync_client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
            limit=100,
            with_payload=True,
            with_vectors=False,
        )
        chunks = [
            {
                "chunk_id": str(point.id),
                "chunk_index": point.payload.get("chunk_index", 0),
                "text": point.payload.get("text", ""),
                "title": point.payload.get("title", ""),
                "created_at": point.payload.get("created_at", ""),
                "metadata": point.payload.get("metadata", {}),
            }
            for point in results
        ]
        chunks.sort(key=lambda x: x["chunk_index"])
        return chunks

    def health_check(self) -> bool:
        """Synchronous version of health_check_async."""
        try:
            self._sync_client.get_collections()
            return True
        except Exception:
            return False


@lru_cache()
def get_qdrant_service() -> QdrantService:
    """Get or create Qdrant service singleton (thread-safe via lru_cache)."""
    return QdrantService()
