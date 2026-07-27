"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT token and return the current authenticated user."""
    token = credentials.credentials

    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token does not contain user information")

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedException("Invalid user ID in token")

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return user


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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information.

    Requires a valid JWT access token in the Authorization header.
    """
    return current_user
