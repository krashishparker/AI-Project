from typing import List, Dict, Any
from app.rag.vectorstore import VectorStoreService
from app.rag.llm import LLMService
from app.models.resume import ResumeChunk


class RAGPipeline:
    """RAG (Retrieval Augmented Generation) pipeline for resume chat."""
    
    def __init__(self):
        self.vectorstore = VectorStoreService()
        self.llm_service = LLMService()
    
    def process_resume(self, resume_id: int, chunks: List[ResumeChunk], metadata: Dict[str, Any] = None):
        """Process resume: create embeddings and store in vector database."""
        chunk_texts = [chunk.chunk_text for chunk in chunks]
        
        # Add to vector store
        self.vectorstore.add_documents(
            resume_id=resume_id,
            chunks=chunk_texts,
            metadata=metadata
        )
    
    def query(self, question: str, resume_id: int) -> Dict[str, Any]:
        """Query the RAG pipeline."""
        # Retrieve relevant chunks
        relevant_docs = self.vectorstore.similarity_search(
            query=question,
            resume_id=resume_id
        )
        
        if not relevant_docs:
            return {
                "answer": "The uploaded resume does not contain this information.",
                "context_chunks": []
            }
        
        # Combine context from relevant chunks
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Generate response using LLM
        answer = self.llm_service.generate_response(context, question)
        
        # Prepare context chunks for response
        context_chunks = [
            {
                "text": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in relevant_docs
        ]
        
        return {
            "answer": answer,
            "context_chunks": context_chunks
        }
    
    def delete_resume(self, resume_id: int):
        """Delete a resume from the vector store."""
        self.vectorstore.delete_resume_documents(resume_id)
