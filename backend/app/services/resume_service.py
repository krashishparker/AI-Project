from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.resume import Resume, ResumeChunk
from app.schemas.resume import ResumeUploadResponse, ResumeResponse
from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
import os
from app.core.config import settings


class ResumeService:
    """Service for resume operations."""
    
    @staticmethod
    async def upload_resume(
        db: Session,
        user_id: int,
        filename: str,
        file_path: str,
        file_type: str,
        file_size: int
    ) -> ResumeUploadResponse:
        """Upload and process a resume."""
        # Create resume record
        resume = Resume(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            processing_status="pending"
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Process resume asynchronously
        await ResumeService._process_resume(db, resume)
        
        return ResumeUploadResponse.model_validate(resume)
    
    @staticmethod
    async def _process_resume(db: Session, resume: Resume):
        """Process resume: parse, chunk, and create embeddings."""
        try:
            resume.processing_status = "processing"
            db.commit()
            
            # Parse resume based on file type
            if resume.file_type == "application/pdf":
                parser = PDFParser
            elif resume.file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                parser = DOCXParser
            else:
                raise Exception("Unsupported file type")
            
            # Extract text
            text = parser.extract_text(resume.file_path)
            resume.parsed_text = text
            
            # Parse structured data
            parsed_data = parser.parse_resume(text)
            resume.parsed_data = parsed_data
            
            # Create chunks
            chunks = ResumeService._create_chunks(text)
            
            # Save chunks to database
            for idx, chunk in enumerate(chunks):
                resume_chunk = ResumeChunk(
                    resume_id=resume.id,
                    chunk_index=idx,
                    chunk_text=chunk,
                    metadata={"chunk_size": len(chunk)}
                )
                db.add(resume_chunk)
            
            resume.processing_status = "completed"
            db.commit()
            
        except Exception as e:
            resume.processing_status = "failed"
            resume.error_message = str(e)
            db.commit()
    
    @staticmethod
    def _create_chunks(text: str) -> list:
        """Create text chunks for embedding."""
        chunk_size = settings.CHUNK_SIZE
        chunk_overlap = settings.CHUNK_OVERLAP
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
            
            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunk))
                # Keep overlap
                overlap_words = current_chunk[-chunk_overlap:]
                current_chunk = overlap_words
                current_size = sum(len(w) + 1 for w in overlap_words)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    @staticmethod
    def get_resume(db: Session, resume_id: int, user_id: int) -> Optional[ResumeResponse]:
        """Get a resume by ID."""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return None
        
        return ResumeResponse.model_validate(resume)
    
    @staticmethod
    def get_user_resumes(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        """Get all resumes for a user."""
        resumes = db.query(Resume).filter(
            Resume.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        return [ResumeResponse.model_validate(r) for r in resumes]
    
    @staticmethod
    def delete_resume(db: Session, resume_id: int, user_id: int) -> bool:
        """Delete a resume."""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        
        if not resume:
            return False
        
        # Delete file from disk
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
        
        db.delete(resume)
        db.commit()
        return True
    
    @staticmethod
    def get_resume_chunks(db: Session, resume_id: int) -> list:
        """Get all chunks for a resume."""
        chunks = db.query(ResumeChunk).filter(
            ResumeChunk.resume_id == resume_id
        ).order_by(ResumeChunk.chunk_index).all()
        
        return [{"id": c.id, "index": c.chunk_index, "text": c.chunk_text} for c in chunks]
