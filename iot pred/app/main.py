# Main FastAPI application initialization and configuration

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="IoT Predictive Maintenance API",
    description="Enterprise Industrial IoT Predictive Maintenance Backend",
    version="1.0.0"
)

# Configure CORS - allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware - only allow trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"]
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if API is running and healthy"""
    return {
        "status": "healthy",
        "service": "IoT Predictive Maintenance Backend"
    }


# Root endpoint
@app.get("/")
async def root():
    """Welcome message"""
    return {"message": "Welcome to IoT Predictive Maintenance API"}


# Startup event
@app.on_event("startup")
async def startup():
    """Run when application starts"""
    logger.info("Application starting up...")
    # Database connection will be initialized here later
    # MQTT client will be started here later
    # WebSocket manager will be initialized here later


# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    """Run when application shuts down"""
    logger.info("Application shutting down...")
    # Close database connections here later
    # Disconnect MQTT client here later
    # Close WebSocket connections here later


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload during development
    )
