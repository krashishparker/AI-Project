from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Resume(Base):
    """Resume model for storing resume metadata."""
    
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Parsed content
    parsed_text = Column(Text)
    parsed_data = Column(JSON)  # Stores structured data (name, email, skills, etc.)
    
    # Processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="resumes")
    chunks = relationship("ResumeChunk", back_populates="resume", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="resume", cascade="all, delete-orphan")


class ResumeChunk(Base):
    """Resume chunk model for storing text chunks."""
    
    __tablename__ = "resume_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    metadata = Column(JSON)  # Additional metadata about the chunk
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    resume = relationship("Resume", back_populates="chunks")


class ChatHistory(Base):
    """Chat history model for storing conversations."""
    
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    context_chunks = Column(JSON)  # Store retrieved chunks for reference
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    resume = relationship("Resume", back_populates="chat_history")
    user = relationship("User", backref="chat_history")
