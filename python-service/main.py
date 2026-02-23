"""VectorFlow Python Service - Main Application."""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config import get_settings
from exceptions import VectorFlowError
from models.schemas import HealthResponse
from routers import ingest, search, ask, bulk_ingest

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("VectorFlow Python Service starting...")
    settings = get_settings()
    print(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
    print(f"Embedding model: {settings.embedding_model}")
    yield
    # Shutdown
    print("VectorFlow Python Service shutting down...")


app = FastAPI(
    title="VectorFlow Python Service",
    description="Document ingestion, embedding generation, and vector search service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(ask.router)
app.include_router(bulk_ingest.router)


@app.exception_handler(VectorFlowError)
async def vectorflow_error_handler(request: Request, exc: VectorFlowError):
    """Return structured error responses for known exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "service": "VectorFlow Python Service",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    from services.qdrant_service import get_qdrant_service
    
    qdrant_connected = False
    postgres_connected = False
    
    try:
        qdrant_service = get_qdrant_service()
        qdrant_connected = await qdrant_service.health_check_async()
    except Exception:
        pass
    
    # For now, assume postgres is connected if we got this far
    # In production, you'd check the actual connection
    postgres_connected = True
    
    status = "healthy" if qdrant_connected else "degraded"
    
    return HealthResponse(
        status=status,
        qdrant_connected=qdrant_connected,
        postgres_connected=postgres_connected
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
