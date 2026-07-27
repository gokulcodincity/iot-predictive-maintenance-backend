"""Authentication API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)
    return auth_service.register(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    auth_service = AuthService(db)
    return auth_service.login(login_data)
