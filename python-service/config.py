"""Configuration settings for the Python service."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Qdrant Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "documents"
    
    # OpenAI Configuration
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-ada-002"
    llm_model: str = "gpt-3.5-turbo"
    
    # PostgreSQL Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "vectorflow_sql_db"
    postgres_user: str = "vectorflow"
    postgres_password: str = "vectorflow123"
    
    # Chunking Configuration
    chunk_size: int = 500  # tokens
    chunk_overlap: int = 50  # tokens
    
    # Search Configuration
    default_search_limit: int = 5
    max_search_limit: int = 20
    
    # CORS Configuration
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

