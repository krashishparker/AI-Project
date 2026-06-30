from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    parsed_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    processing_status: str
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeDetailResponse(ResumeResponse):
    chunks: List[Dict[str, Any]] = []


class ChatRequest(BaseModel):
    resume_id: int
    question: str


class ChatResponse(BaseModel):
    answer: str
    context_chunks: List[Dict[str, Any]] = []
