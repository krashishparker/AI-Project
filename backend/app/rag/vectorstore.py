from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.rag.embeddings import EmbeddingService
import os


class VectorStoreService:
    """Service for managing ChromaDB vector store."""
    
    def __init__(self):
        self.embeddings = EmbeddingService()
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        
        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize vector store
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings.embeddings,
            persist_directory=self.persist_directory
        )
    
    def add_documents(self, resume_id: int, chunks: List[str], metadata: Dict[str, Any] = None):
        """Add document chunks to vector store."""
        documents = []
        
        for idx, chunk in enumerate(chunks):
            doc_metadata = {
                "resume_id": resume_id,
                "chunk_index": idx,
                "chunk_size": len(chunk)
            }
            
            if metadata:
                doc_metadata.update(metadata)
            
            doc = Document(page_content=chunk, metadata=doc_metadata)
            documents.append(doc)
        
        # Add documents to vector store
        self.vectorstore.add_documents(documents)
        
        # Persist to disk
        self.vectorstore.persist()
    
    def similarity_search(
        self,
        query: str,
        resume_id: int,
        k: int = None,
        filter_dict: Dict[str, Any] = None
    ) -> List[Document]:
        """Search for similar documents."""
        if k is None:
            k = settings.TOP_K_RESULTS
        
        # Filter by resume_id
        if filter_dict is None:
            filter_dict = {"resume_id": resume_id}
        else:
            filter_dict["resume_id"] = resume_id
        
        results = self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        return results
    
    def delete_resume_documents(self, resume_id: int):
        """Delete all documents for a specific resume."""
        # Get all documents for the resume
        results = self.vectorstore.get(
            where={"resume_id": resume_id}
        )
        
        if results and results.get("ids"):
            # Delete by IDs
            self.vectorstore.delete(ids=results["ids"])
            self.vectorstore.persist()
    
    def get_resume_document_count(self, resume_id: int) -> int:
        """Get the number of documents for a resume."""
        results = self.vectorstore.get(
            where={"resume_id": resume_id}
        )
        
        if results and results.get("ids"):
            return len(results["ids"])
        return 0
