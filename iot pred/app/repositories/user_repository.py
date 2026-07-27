"""User repository for database operations."""

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def get_by_email(self, email: str):
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User):
        """Create a new user."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int):
        """Get user by id."""
        return self.db.query(User).filter(User.id == user_id).first()
