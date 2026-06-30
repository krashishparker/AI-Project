from langchain_community.embeddings import OllamaEmbeddings
from app.core.config import settings


class EmbeddingService:
    """Service for generating embeddings using Ollama."""
    
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_EMBEDDING_MODEL
        )
    
    def embed_documents(self, texts: list) -> list:
        """Generate embeddings for a list of documents."""
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> list:
        """Generate embedding for a single query."""
        return self.embeddings.embed_query(text)
