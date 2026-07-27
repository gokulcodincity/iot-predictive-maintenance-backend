"""Custom exception classes for the application."""

from fastapi import HTTPException


class ResourceNotFoundException(HTTPException):
    """Exception raised when a resource is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, detail=message)


class UnauthorizedException(HTTPException):
    """Exception raised when user is not authorized."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=401, detail=message)


class BadRequestException(HTTPException):
    """Exception raised for bad/invalid requests."""
    def __init__(self, message: str = "Bad request"):
        super().__init__(status_code=400, detail=message)


class ConflictException(HTTPException):
    """Exception raised when there is a conflict."""
    def __init__(self, message: str = "Conflict"):
        super().__init__(status_code=409, detail=message)
