from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if user exists
        existing_user = db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise ValueError("Email already registered")
        
        existing_username = db.query(User).filter(
            User.username == user_data.username
        ).first()
        
        if existing_username:
            raise ValueError("Username already taken")
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def login_user(db: Session, username: str, password: str) -> dict:
        """Login a user and return access token."""
        user = AuthService.authenticate_user(db, username, password)
        
        if not user:
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        access_token = create_access_token(data={"sub": user.username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
