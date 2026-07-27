from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.assets import router as assets_router

app = FastAPI(
    title="Enterprise IoT Predictive Maintenance Backend",
    version="1.0.0",
    description="Industrial IoT platform for predictive maintenance with AI predictions"
)

# API Tags for future routers
tags_metadata = [
    {"name": "Authentication", "description": "User login, registration, token management"},
    {"name": "Assets", "description": "Industrial asset management"},
    {"name": "Telemetry", "description": "Sensor telemetry data ingestion and retrieval"},
    {"name": "Prediction", "description": "AI-based predictions for equipment health"},
    {"name": "Alert", "description": "Alert management and notifications"},
    {"name": "Maintenance", "description": "Maintenance records and scheduling"},
    {"name": "Dashboard", "description": "Dashboard data aggregation"},
]

app.openapi_tags = tags_metadata

# Register routers
app.include_router(auth_router)
app.include_router(assets_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Enterprise IoT Predictive Maintenance Backend is running",
        "status": "success",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
