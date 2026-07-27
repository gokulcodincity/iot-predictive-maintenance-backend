from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Project information
    PROJECT_NAME: str = "Enterprise IoT Predictive Maintenance Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Industrial IoT platform for predictive maintenance with AI predictions"

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/iot_predictive_maintenance"

    # JWT settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Debug mode
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
