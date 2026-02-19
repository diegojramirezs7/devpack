# Django Project Initialization Reference

This document contains all templates and configurations for initializing a production-ready Django + Django REST Framework + Postgres project.

## Directory Structure

```
project-name/
├── PROJECT_NAME/                # Django project directory
│   ├── __init__.py
│   ├── settings.py              # Django settings
│   ├── urls.py                  # URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── APP_NAME/                    # Django app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py                  # App URLs
│   ├── views.py                 # API views
│   └── migrations/
│       └── __init__.py
├── static/                      # Static files (collectstatic target)
├── media/                       # User-uploaded media
├── manage.py
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
    "django>=5.1.0",
    "djangorestframework>=3.15.0",
    "django-cors-headers>=4.6.0",
    "django-ratelimit>=4.1.0",
    "dj-database-url>=2.3.0",
    "psycopg[binary]>=3.2.0",
    "python-dotenv>=1.0.0",
]

[dependency-groups]
dev = [
    "ruff>=0.8.0",
    "pytest>=8.3.0",
    "pytest-django>=4.9.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "DJ"]
ignore = []

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "PROJECT_NAME.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
```

## File Templates

### manage.py

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PROJECT_NAME.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

### PROJECT_NAME/settings.py

```python
"""Django settings for PROJECT_NAME project."""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-CHANGE-THIS-IN-PRODUCTION'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    # Local apps
    'APP_NAME',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'PROJECT_NAME.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'PROJECT_NAME.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:postgres@localhost:5432/PROJECT_NAME',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
if '*' in CORS_ALLOWED_ORIGINS:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_CREDENTIALS = True

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.getenv('ANON_RATE_LIMIT', '100/hour'),
        'user': os.getenv('USER_RATE_LIMIT', '1000/hour'),
    },
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'APP_NAME': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
```

### PROJECT_NAME/urls.py

```python
"""URL configuration for PROJECT_NAME project."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('APP_NAME.urls')),
]
```

### PROJECT_NAME/__init__.py

```python
"""PROJECT_NAME Django project."""
```

### PROJECT_NAME/asgi.py

```python
"""ASGI config for PROJECT_NAME project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PROJECT_NAME.settings')

application = get_asgi_application()
```

### PROJECT_NAME/wsgi.py

```python
"""WSGI config for PROJECT_NAME project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PROJECT_NAME.settings')

application = get_wsgi_application()
```

### APP_NAME/apps.py

```python
"""App configuration for APP_NAME."""

from django.apps import AppConfig


class APP_NAME_CAMELConfig(AppConfig):
    """Configuration for APP_NAME app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'APP_NAME'
```

### APP_NAME/urls.py

```python
"""URL configuration for APP_NAME app."""

from django.urls import path
from . import views

app_name = 'APP_NAME'

urlpatterns = [
    path('health/', views.health_check, name='health'),
]
```

### APP_NAME/views.py

```python
"""API views for APP_NAME."""

import logging

from django.db import connection
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

logger = logging.getLogger(__name__)


class HealthCheckThrottle(AnonRateThrottle):
    """Custom throttle class that allows unlimited health check requests."""
    
    def allow_request(self, request, view):
        """Always allow health check requests."""
        return True


@api_view(['GET'])
@throttle_classes([HealthCheckThrottle])
def health_check(request):
    """Health check endpoint.
    
    Verifies database connectivity and returns service status.
    
    Returns:
        Response: JSON with health status
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return Response({
            'status': 'healthy',
            'database': 'connected',
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
        }, status=503)
```

### APP_NAME/models.py

```python
"""Database models for APP_NAME."""

from django.db import models

# Define your models here
```

### APP_NAME/admin.py

```python
"""Admin configuration for APP_NAME."""

from django.contrib import admin

# Register your models here
```

### APP_NAME/tests.py

```python
"""Tests for APP_NAME."""

from django.test import TestCase

# Create your tests here
```

### APP_NAME/__init__.py

```python
"""APP_NAME Django app."""
```

### APP_NAME/migrations/__init__.py

```python
"""Migrations for APP_NAME."""
```

## Configuration Files

### .python-version

```
3.13.1
```

### .env.example

```env
# Django Core
SECRET_KEY=your-secret-key-here-CHANGE-IN-PRODUCTION
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/PROJECT_NAME

# CORS - comma-separated list of allowed origins
# Use "*" for development, specific origins for production
ALLOWED_ORIGINS=*

# Rate Limiting
ANON_RATE_LIMIT=100/hour
USER_RATE_LIMIT=1000/hour

# Logging
DJANGO_LOG_LEVEL=INFO
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

# Django
db.sqlite3
db.sqlite3-journal
/static/
/media/
*.log
local_settings.py

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
```

### README.md

```markdown
# PROJECT_NAME

A production-ready Django REST Framework application with PostgreSQL database.

## Features

- 🎯 **Django 5.1** - Modern Python web framework
- 🔥 **Django REST Framework** - Powerful toolkit for building Web APIs
- 🗄️ **PostgreSQL** - Robust relational database
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
# IMPORTANT: Generate a new SECRET_KEY for production!
# You can generate one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Start Database

```bash
# Start PostgreSQL with Docker Compose
docker compose up -d

# Check database is running
docker compose ps
```

### 4. Run Migrations

```bash
# Apply database migrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
# Create admin user
python manage.py createsuperuser
```

### 6. Run Application

```bash
# Development server
python manage.py runserver
```

The API will be available at:
- **Application**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/

## Project Structure

```
PROJECT_NAME/
├── PROJECT_NAME/            # Django project configuration
│   ├── settings.py          # Settings with env var support
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
├── APP_NAME/                # Main Django app
│   ├── views.py             # API views
│   ├── models.py            # Database models
│   ├── urls.py              # App URL patterns
│   ├── admin.py             # Admin configuration
│   └── migrations/          # Database migrations
├── static/                  # Static files (collectstatic)
├── media/                   # User-uploaded files
├── manage.py                # Django management script
├── .env.example             # Environment variables template
├── .python-version          # Python version
├── docker-compose.yml       # PostgreSQL service
├── pyproject.toml           # Project dependencies
└── README.md
```

## Available Endpoints

### Health Check
```bash
GET /api/health/
```

Returns database connectivity status. Exempt from rate limiting.

### Admin Interface
```bash
http://localhost:8000/admin/
```

Django admin interface for managing models.

## Development

### Adding Dependencies

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --group dev package-name
```

### Database Migrations

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
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

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=APP_NAME
```

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

### Database Management

```bash
# Stop database
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v

# View logs
docker compose logs -f postgres

# Database shell
python manage.py dbshell
```

## Configuration

Key environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | *CHANGE IN PRODUCTION* |
| `DEBUG` | Debug mode | `true` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/PROJECT_NAME` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `*` |
| `ANON_RATE_LIMIT` | Anonymous user rate limit | `100/hour` |
| `USER_RATE_LIMIT` | Authenticated user rate limit | `1000/hour` |
| `DJANGO_LOG_LEVEL` | Django logging level | `INFO` |

## Production Deployment

Before deploying to production:

1. **Generate a strong `SECRET_KEY`** and never commit it
2. **Set `DEBUG=false`** in environment variables
3. **Configure `ALLOWED_HOSTS`** with your domain names
4. **Configure `ALLOWED_ORIGINS`** with specific domains (not `*`)
5. **Use strong database credentials** (not default postgres/postgres)
6. **Set up proper secret management** for sensitive values
7. **Configure rate limits** based on your needs
8. **Set up database backups**
9. **Configure logging** to appropriate level and destination
10. **Run `collectstatic`** to gather static files
11. **Use a production WSGI server** (Gunicorn, uWSGI)
12. **Set up HTTPS** with proper SSL certificates

### Production WSGI Server Example

```bash
# Install gunicorn
uv add gunicorn

# Run with gunicorn
gunicorn PROJECT_NAME.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## License

[Your License Here]
```

## Implementation Notes

### Variable Substitution

When creating files, replace these placeholders:
- `PROJECT_NAME` → User's project name (snake_case)
- `APP_NAME` → User's app name (snake_case)
- `APP_NAME_CAMEL` → App name in PascalCase (e.g., `my_app` → `MyApp`)

### Directory Creation

Create these empty directories:
- `APP_NAME/migrations/` (with `__init__.py`)
- `static/` (with `.gitkeep` to track in git)
- `media/` (with `.gitkeep` to track in git)

### Order of Operations

1. Run `django-admin startproject PROJECT_NAME .` in temp location if you want Django's file structure, OR
2. Create all files manually based on templates above
3. Create the app directory structure manually
4. Create configuration files
5. Create README.md

**Recommended**: Create files manually from templates to have full control over contents.

### After Creation

Remind the user to:
1. Navigate to project directory
2. Create and activate virtual environment
3. Install dependencies with `uv sync`
4. Start Docker Compose
5. Copy .env.example to .env
6. Generate a new SECRET_KEY for .env
7. Run migrations: `python manage.py migrate`
8. Create superuser (optional)
9. Run the development server

### Important Django-Specific Notes

- **SECRET_KEY**: Default is insecure, remind user to generate new one
- **ALLOWED_HOSTS**: Must be configured for production
- **Static files**: Need to run `collectstatic` for production
- **Migrations**: Must run `migrate` after setup
- **CORS order**: `corsheaders.middleware.CorsMiddleware` must be before `CommonMiddleware`
- **Rate limiting**: Using DRF's built-in throttling (simpler than django-ratelimit for API)
- **dj-database-url**: Handles DATABASE_URL parsing with connection pooling settings