from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.resume import ChatHistory
from app.schemas.resume import ChatResponse
from app.rag.rag_pipeline import RAGPipeline
from app.core.redis_client import RedisCache


class ChatService:
    """Service for chat operations with RAG."""
    
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
    
    async def chat(
        self,
        db: Session,
        user_id: int,
        resume_id: int,
        question: str
    ) -> ChatResponse:
        """Process a chat question using RAG."""
        
        # Check cache first
        cache_key = f"chat:{resume_id}:{hash(question)}"
        cached_response = await RedisCache.get(cache_key)
        if cached_response:
            return ChatResponse(**cached_response)
        
        # Query RAG pipeline
        result = self.rag_pipeline.query(question, resume_id)
        
        # Save chat history
        chat_history = ChatHistory(
            resume_id=resume_id,
            user_id=user_id,
            question=question,
            answer=result["answer"],
            context_chunks=result["context_chunks"]
        )
        db.add(chat_history)
        db.commit()
        
        # Cache response
        await RedisCache.set(cache_key, result, expire=3600)
        
        return ChatResponse(
            answer=result["answer"],
            context_chunks=result["context_chunks"]
        )
    
    def get_chat_history(
        self,
        db: Session,
        user_id: int,
        resume_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> list:
        """Get chat history for a resume."""
        history = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.resume_id == resume_id
        ).order_by(ChatHistory.created_at.desc()).offset(skip).limit(limit).all()
        
        return [
            {
                "id": h.id,
                "question": h.question,
                "answer": h.answer,
                "created_at": h.created_at.isoformat()
            }
            for h in history
        ]
