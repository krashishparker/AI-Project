from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Resume Chat"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/resume_chat"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    UPLOAD_DIR: str = "uploads"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_LLM_MODEL: str = "llama3"
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "chroma_db"
    CHROMA_COLLECTION_NAME: str = "resume_embeddings"
    
    # RAG
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 3
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
