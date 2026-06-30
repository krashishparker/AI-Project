from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.schemas.resume import ResumeUploadResponse, ResumeResponse, ChatRequest, ChatResponse
from app.services.resume_service import ResumeService
from app.services.chat_service import ChatService
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter, get_rate_limit
import os
import uuid
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/resume", tags=["Resume"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_rate_limit())
async def upload_resume(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a resume file (PDF or DOCX)."""
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Upload resume
    try:
        resume = await ResumeService.upload_resume(
            db=db,
            user_id=current_user.id,
            filename=file.filename,
            file_path=file_path,
            file_type=file.content_type,
            file_size=file_size
        )
        return resume
    except Exception as e:
        # Clean up file if upload fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        )


@router.get("/", response_model=List[ResumeResponse])
async def get_resumes(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all resumes for the current user."""
    resumes = ResumeService.get_user_resumes(db, current_user.id, skip, limit)
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID."""
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume."""
    success = ResumeService.delete_resume(db, resume_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return None


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(get_rate_limit())
async def chat_with_resume(
    chat_request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI about a resume."""
    
    # Verify resume belongs to user
    resume = ResumeService.get_resume(db, chat_request.resume_id, current_user.id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.processing_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume is still being processed. Please wait."
        )
    
    chat_service = ChatService()
    response = await chat_service.chat(
        db=db,
        user_id=current_user.id,
        resume_id=chat_request.resume_id,
        question=chat_request.question
    )
    
    return response


@router.get("/{resume_id}/chat-history")
async def get_chat_history(
    resume_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a resume."""
    
    # Verify resume belongs to user
    resume = ResumeService.get_resume(db, resume_id, current_user.id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    chat_service = ChatService()
    history = chat_service.get_chat_history(db, current_user.id, resume_id, skip, limit)
    
    return {"history": history}
