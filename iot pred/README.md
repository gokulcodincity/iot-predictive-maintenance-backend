# IoT Predictive Maintenance Intelligence Platform - Backend

## Overview

This is the backend service for an Enterprise Industrial IoT Predictive Maintenance Intelligence Platform. The system receives industrial telemetry from PLC/Edge devices through MQTT, performs AI-based predictions, generates maintenance recommendations, and provides REST and WebSocket APIs for dashboards.

## Tech Stack

- **Framework:** FastAPI (Python 3.12+)
- **Database:** PostgreSQL + SQLAlchemy ORM
- **Database Migrations:** Alembic
- **Authentication:** JWT + RBAC
- **Real-time Messaging:** MQTT (Paho MQTT)
- **WebSocket:** FastAPI WebSocket
- **ML Integration:** Model abstraction layer (independent training)
- **Containerization:** Docker & Docker Compose
- **Testing:** Pytest
- **Code Quality:** Black, isort, flake8

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 13+
- MQTT Broker (Mosquitto)
- Docker & Docker Compose (optional)

### Setup

1. Clone repository
```bash
git clone <repo-url>
cd iot-predictive-maintenance-backend
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements-dev.txt
```

4. Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database
```bash
python scripts/init_db.py
python scripts/seed_db.py
```

6. Run development server
```bash
python -m uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

## Project Structure

```
app/
├── api/                 # API route handlers (v1, v2)
├── schemas/             # Pydantic request/response models
├── core/                # Configuration, security, exceptions
├── models/              # SQLAlchemy ORM models
├── repositories/        # Data access layer
├── services/            # Business logic layer
├── dependencies/        # Dependency injection
├── middleware/          # HTTP middleware
├── mqtt/                # MQTT consumer module
├── websocket/           # WebSocket module
├── ml/                  # ML model abstraction
├── utils/               # Utility functions
└── db/                  # Database configuration

tests/                   # Test suite
migrations/              # Alembic database migrations
scripts/                 # Utility scripts
docker/                  # Docker configuration
config/                  # Environment configuration
docs/                    # Documentation
```

## API Endpoints

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for full API specification.

### Main Endpoints
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/assets` - List assets
- `POST /api/v1/telemetry` - Store telemetry data
- `GET /api/v1/predictions` - Get predictions
- `GET /api/v1/alerts` - Get alerts
- `WS /ws` - WebSocket connection

## Development

### Running Tests
```bash
pytest                          # Run all tests
pytest tests/unit/              # Run unit tests
pytest tests/integration/       # Run integration tests
pytest --cov=app                # With coverage report
```

### Code Quality
```bash
black app/                      # Format code
isort app/                      # Sort imports
flake8 app/                     # Lint code
```

### Database Migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Docker

### Development
```bash
docker-compose up
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [MQTT Topics](docs/MQTT_TOPICS.md)
- [ML Model Integration](docs/ML_MODEL_INTEGRATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

TODO: Add license
