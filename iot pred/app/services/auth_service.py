"""Authentication service for user registration and login."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequest
from app.schemas.user_schema import UserCreate


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        """Initialize auth service with database session."""
        self.db = db
        self.user_repository = UserRepository(db)

    def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if email already exists
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ConflictException(f"Email {user_data.email} already registered")

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create user object
        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password=hashed_password,
            role=user_data.role,
        )

        # Save user
        return self.user_repository.create(user)

    def login(self, login_data: LoginRequest) -> dict:
        """Authenticate user and return access token."""
        # Find user by email
        user = self.user_repository.get_by_email(login_data.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        # Verify password
        if not verify_password(login_data.password, user.password):
            raise UnauthorizedException("Invalid email or password")

        # Create access token
        access_token = create_access_token({"sub": str(user.id)})

        return {"access_token": access_token, "token_type": "bearer"}
