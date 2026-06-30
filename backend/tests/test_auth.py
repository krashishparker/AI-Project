import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data


def test_register_duplicate_email():
    """Test registration with duplicate email."""
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "testpass123"
        }
    )
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser3",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400


def test_login():
    """Test user login."""
    # First register
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "loginpass123"
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        json={
            "username": "loginuser",
            "password": "loginpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user with token."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "current@example.com",
            "username": "currentuser",
            "password": "currentpass123"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "currentuser",
            "password": "currentpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"


def test_get_current_user_no_token():
    """Test getting current user without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
