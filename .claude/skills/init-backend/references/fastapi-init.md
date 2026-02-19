# FastAPI Project Initialization Reference

This document contains all templates and configurations for initializing a production-ready FastAPI + Postgres project.

## Directory Structure

```
project-name/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, middleware
│   ├── config.py            # Pydantic settings
│   ├── database.py          # SQLModel + asyncpg pool
│   ├── dependencies.py      # Dependency injection
│   ├── exceptions.py        # Custom exception handlers
│   ├── logging_config.py    # Logging configuration
│   └── routers/
│       ├── __init__.py
│       └── health.py        # Health check endpoint
├── .env.example
├── .gitignore
├── .python-version
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Dependencies (pyproject.toml)

```toml
[project]
name = "PROJECT_NAME"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlmodel>=0.0.22",
    "asyncpg>=0.30.0",
    "pydantic-settings>=2.6.0",
    "slowapi>=0.1.9",
]

[dependency-groups]
dev = [
    "ruff>=0.8.0",
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = []
```

## File Templates

### src/config.py

```python
"""Application configuration using Pydantic settings.

Loads configuration from environment variables with validation.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="PROJECT_NAME", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/PROJECT_NAME",
        description="PostgreSQL connection string",
    )
    db_pool_min_size: int = Field(default=2, description="Minimum pool size")
    db_pool_max_size: int = Field(default=10, description="Maximum pool size")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["*"],
        description="Comma-separated list of allowed origins for CORS",
    )
    
    # Rate Limiting
    rate_limit: str = Field(
        default="100/minute",
        description="Rate limit string (e.g., '100/minute')",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins from environment variable."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings: Application settings
    """
    return Settings()
```

### src/database.py

```python
"""Database connection and session management.

Provides asyncpg connection pool and SQLModel integration.
"""

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.config import get_settings

settings = get_settings()

# SQLAlchemy async engine for SQLModel
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    future=True,
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_pool() -> asyncpg.Pool:
    """Create asyncpg connection pool.
    
    Returns:
        asyncpg.Pool: Database connection pool
    """
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
        command_timeout=60,
    )
    return pool


async def init_db() -> None:
    """Initialize database tables.
    
    Creates all SQLModel tables. Run this during application startup
    or via a separate migration script.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### src/dependencies.py

```python
"""Dependency injection for FastAPI routes.

Provides reusable dependencies for database sessions, settings, etc.
"""

from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.database import async_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with async_session() as session:
        yield session


async def get_db_pool(request: Request) -> asyncpg.Pool:
    """Get asyncpg connection pool from app state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        asyncpg.Pool: Database connection pool
    """
    return request.app.state.db_pool


def get_settings_dependency() -> Settings:
    """Get application settings dependency.
    
    Returns:
        Settings: Application settings
    """
    return get_settings()
```

### src/exceptions.py

```python
"""Custom exception handlers for the FastAPI application.

Provides consistent error responses across the API.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with consistent JSON response.
    
    Args:
        request: FastAPI request
        exc: HTTP exception
        
    Returns:
        JSONResponse: Formatted error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with 500 response.
    
    Args:
        request: FastAPI request
        exc: General exception
        
    Returns:
        JSONResponse: Formatted error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "status_code": 500,
            }
        },
    )
```

### src/logging_config.py

```python
"""Logging configuration for the application.

Sets up structured logging with appropriate formats and levels.
"""

import logging
import sys

from src.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure application logging.
    
    Sets up console handler with appropriate format and level.
    """
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
```

### src/main.py

```python
"""FastAPI application entry point.

Configures the FastAPI app with middleware, exception handlers,
lifespan events, and includes all routers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.config import get_settings
from src.database import create_db_pool
from src.exceptions import general_exception_handler, http_exception_handler
from src.logging_config import setup_logging
from src.routers import health

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown events.
    
    Handles database connection pool initialization on startup and
    proper cleanup on shutdown.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Control back to the application
    """
    # Startup: Initialize database connection pool
    app.state.db_pool = await create_db_pool()
    logger.info("Connected to PostgreSQL database pool")
    
    yield
    
    # Shutdown: Close database connection pool
    await app.state.db_pool.close()
    logger.info("Closed database connection pool")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add rate limiter state
app.state.limiter = limiter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    """Root endpoint.
    
    Returns:
        dict: Welcome message
    """
    return {"message": f"Welcome to {settings.app_name}"}
```

### src/routers/health.py

```python
"""Health check endpoint for monitoring and load balancers."""

from fastapi import APIRouter, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.dependencies import get_db_pool

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/health")
@limiter.exempt
async def health_check(db_pool=Depends(get_db_pool)):
    """Health check endpoint.
    
    Verifies database connectivity and returns service status.
    
    Args:
        db_pool: Database connection pool
        
    Returns:
        dict: Health status
    """
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }
```

### src/routers/__init__.py

```python
"""Router package for API endpoints."""
```

### src/__init__.py

```python
"""PROJECT_NAME API application."""

__version__ = "0.1.0"
```

## Configuration Files

### .python-version

```
3.13.1
```

### .env.example

```env
# Application
APP_NAME=PROJECT_NAME
DEBUG=false

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/PROJECT_NAME
DB_POOL_MIN_SIZE=2
DB_POOL_MAX_SIZE=10

# CORS - comma-separated list of allowed origins
# Use "*" for development, specific origins for production
ALLOWED_ORIGINS=*

# Rate Limiting
RATE_LIMIT=100/minute
```

### docker-compose.yml

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: PROJECT_NAME_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: PROJECT_NAME
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
.eggs/

# Virtual Environment
.venv/
venv/
ENV/
env/

# Environment Variables
.env
.env.local

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Ruff
.ruff_cache/

# Logs
*.log
```

### README.md

```markdown
# PROJECT_NAME

A production-ready FastAPI application with PostgreSQL database.

## Features

- ⚡ **FastAPI** - Modern, fast web framework
- 🗄️ **PostgreSQL** - Robust relational database
- 🔄 **SQLModel** - SQL databases with Python type annotations
- ⚙️ **Pydantic Settings** - Configuration management
- 🚀 **Async Support** - Full async/await with asyncpg
- 🛡️ **Rate Limiting** - Built-in API rate limiting
- 🌐 **CORS** - Configurable cross-origin resource sharing
- 📝 **Logging** - Structured application logging
- 🐳 **Docker Compose** - Easy PostgreSQL setup

## Prerequisites

- Python 3.13.1
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer
- Docker and Docker Compose (for PostgreSQL)

## Getting Started

### 1. Clone and Setup

```bash
cd PROJECT_NAME

# Create virtual environment
uv venv --python 3.13.1

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# At minimum, verify DATABASE_URL matches your setup
```

### 3. Start Database

```bash
# Start PostgreSQL with Docker Compose
docker compose up -d

# Check database is running
docker compose ps
```

### 4. Run Application

```bash
# Development server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## Project Structure

```
PROJECT_NAME/
├── src/
│   ├── main.py              # FastAPI app, middleware, lifespan
│   ├── config.py            # Pydantic settings
│   ├── database.py          # Database connection and pool
│   ├── dependencies.py      # Dependency injection
│   ├── exceptions.py        # Exception handlers
│   ├── logging_config.py    # Logging configuration
│   └── routers/
│       ├── health.py        # Health check endpoint
│       └── ...              # Add your routers here
├── .env.example             # Environment variables template
├── .python-version          # Python version for pyenv/uv
├── docker-compose.yml       # PostgreSQL service
├── pyproject.toml           # Project dependencies
└── README.md
```

## Available Endpoints

### Health Check
```bash
GET /health
```

Returns database connectivity status.

### Root
```bash
GET /
```

Welcome message.

## Development

### Adding Dependencies

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --group dev package-name
```

### Code Quality

```bash
# Run ruff linter
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Database Management

```bash
# Stop database
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v

# View logs
docker compose logs -f postgres
```

## Configuration

Key environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | `PROJECT_NAME` |
| `DEBUG` | Debug mode | `false` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/PROJECT_NAME` |
| `DB_POOL_MIN_SIZE` | Min connection pool size | `2` |
| `DB_POOL_MAX_SIZE` | Max connection pool size | `10` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `*` |
| `RATE_LIMIT` | API rate limit | `100/minute` |

## Production Deployment

Before deploying to production:

1. **Set `DEBUG=false`** in environment variables
2. **Configure `ALLOWED_ORIGINS`** with specific domains (not `*`)
3. **Use strong database credentials** (not default postgres/postgres)
4. **Set up proper secret management** for sensitive values
5. **Configure rate limits** based on your needs
6. **Set up database backups**
7. **Configure logging** to appropriate level and destination

## License

[Your License Here]
```

## Implementation Notes

### Variable Substitution

When creating files, replace these placeholders:
- `PROJECT_NAME` → User's project name (use the snake_case version for Python)

### Order of Operations

1. Create directory structure
2. Create all Python files in `src/`
3. Create configuration files (.env.example, .gitignore, etc.)
4. Create pyproject.toml
5. Create docker-compose.yml
6. Create README.md last (so user sees it at the end)

### After Creation

Remind the user to:
1. Navigate to project directory
2. Create and activate virtual environment
3. Install dependencies with `uv sync`
4. Start Docker Compose
5. Copy .env.example to .env
6. Run the application

### Common Issues

- Missing asyncpg import in dependencies.py - make sure to add at top
- Rate limiter needs to be initialized before using in routes
- Health check should be exempt from rate limiting