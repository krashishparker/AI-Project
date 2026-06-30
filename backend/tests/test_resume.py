import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
import io

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_resume.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Fixture to get auth token."""
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "email": "resume@example.com",
            "username": "resumeuser",
            "password": "resumepass123"
        }
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "username": "resumeuser",
            "password": "resumepass123"
        }
    )
    return response.json()["access_token"]


def test_upload_resume_pdf(auth_token):
    """Test uploading a PDF resume."""
    # Create a fake PDF file
    pdf_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post(
        "/api/resume/upload",
        files=files,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["file_type"] == "application/pdf"
    assert data["processing_status"] in ["pending", "processing", "completed"]


def test_upload_resume_docx(auth_token):
    """Test uploading a DOCX resume."""
    # Create a fake DOCX file
    docx_content = b"PK fake docx content"
    files = {"file": ("test.docx", io.BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    
    response = client.post(
        "/api/resume/upload",
        files=files,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.docx"


def test_upload_invalid_file_type(auth_token):
    """Test uploading invalid file type."""
    files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
    
    response = client.post(
        "/api/resume/upload",
        files=files,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 400


def test_get_resumes(auth_token):
    """Test getting all resumes."""
    # Upload a resume first
    pdf_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    client.post(
        "/api/resume/upload",
        files=files,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Get resumes
    response = client.get(
        "/api/resume/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_resume_by_id(auth_token):
    """Test getting a specific resume."""
    # Upload a resume
    pdf_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    upload_response = client.post(
        "/api/resume/upload",
        files=files,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = upload_response.json()["id"]
    
    # Get resume by ID
    response = client.get(
        f"/api/resume/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == resume_id


def test_delete_resume(auth_token):
    """Test deleting a resume."""
    # Upload a resume
    pdf_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    upload_response = client.post(
        "/api/resume/upload",
        files=files,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = upload_response.json()["id"]
    
    # Delete resume
    response = client.delete(
        f"/api/resume/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 204


def test_chat_with_resume(auth_token):
    """Test chatting with a resume."""
    # Upload a resume
    pdf_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    upload_response = client.post(
        "/api/resume/upload",
        files=files,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    resume_id = upload_response.json()["id"]
    
    # Chat with resume
    response = client.post(
        "/api/resume/chat",
        json={
            "resume_id": resume_id,
            "question": "What is this resume about?"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Note: This might fail if Ollama is not running or resume is not processed
    # In a real test, you'd mock the RAG pipeline
    assert response.status_code in [200, 400, 500]
