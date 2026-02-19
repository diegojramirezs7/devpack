---
name: init-backend
description: Initialize production-ready Django or FastAPI projects with Postgres, proper structure, and best practices. Use when users want to start a new web API project with opinionated defaults.
---

# Project Initialization Skill

Initialize production-ready Python web API projects with opinionated best practices, proper structure, and all necessary configuration files.

## Supported Stacks

- **FastAPI + Postgres** - Async API with SQLModel ORM
- **Django + Postgres** - Traditional REST API with Django REST Framework

## When to Use

Trigger this skill when the user wants to:

- "Initialize a new FastAPI project"
- "Set up a Django API project"
- "Create a new API project with Postgres"
- "Start a new [FastAPI/Django] project"

## High-Level Process

1. **Gather Requirements**
   - Ask which stack (FastAPI or Django)
   - Ask for project name
   - For Django: ask for app name
   - Confirm current directory or ask for target location

2. **Present Plan**
   - Show what will be created (files and directory structure)
   - Explain key decisions and configurations
   - **Wait for user confirmation before proceeding**

3. **Execute Initialization**
   - Route to appropriate reference document
   - Create all files and directories
   - Report what was created

4. **Provide Next Steps**
   - Show commands to get started
   - Explain how to run the project

## Interaction Flow

### Step 1: Gather Information

Start by asking:

```
I'll help you initialize a production-ready Python API project!

Which stack would you like to use?
1. FastAPI + Postgres (async, SQLModel)
2. Django + Postgres (Django REST Framework)
```

Then collect:

- **Project name** (used for directory and package names)
- **For Django only**: App name (the main Django app within the project)
- **Target directory** (default to current directory, but ask if unclear)

### Step 2: Present the Plan

Before creating anything, show the user:

**What will be created:**

- List of all files
- Directory structure overview
- Key configurations (CORS, rate limiting, DB setup, etc.)

**Example output:**

```
I'll create a FastAPI project with the following structure:

project-name/
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI app with lifespan, CORS, rate limiting
│   ├── config.py         # Pydantic settings
│   ├── database.py       # SQLModel + asyncpg connection pool
│   ├── dependencies.py   # Dependency injection
│   ├── exceptions.py     # Custom exception handlers
│   ├── logging_config.py # Logging setup
│   └── routers/
│       ├── __init__.py
│       └── health.py     # Health check endpoint
├── .env.example          # All required environment variables
├── .gitignore
├── .python-version       # 3.13.1
├── docker-compose.yml    # Postgres service
├── pyproject.toml        # uv + dependencies
├── README.md

Key configurations:
- CORS: All origins in dev, configurable via ALLOWED_ORIGINS env var for prod
- Rate limiting: Configured and ready to use
- DB: asyncpg connection pool with min=2, max=10
- Health endpoint: GET /health

Proceed with creation? (yes/no)
```

### Step 3: Route to Reference and Execute

Based on the chosen stack:

- **FastAPI** → Read and follow `references/fastapi-init.md`
- **Django** → Read and follow `references/django-init.md`

The reference document contains:

- Exact file contents/templates
- Directory structure details
- All necessary imports and configurations
- Stack-specific best practices

### Step 4: Completion Message

After creating all files:

```
✅ Project initialized successfully!

Next steps:
1. cd project-name
2. uv venv --python 3.13.1
3. source .venv/bin/activate  # On Windows: .venv\Scripts\activate
4. uv sync
5. docker compose up -d  # Start Postgres
6. cp .env.example .env  # Configure your environment variables
7. [stack-specific run command]

Your project is ready! Check the README.md for more details.
```

## Important Notes

### Always Use References

When creating files, always read the appropriate reference document first:

- For FastAPI: `view references/fastapi-init.md`
- For Django: `view references/django-init.md`

The reference contains the complete, up-to-date templates and configurations.

### Confirmation Required

Never create files without showing the plan and getting explicit user confirmation.

### Python Version

Always pin to Python 3.13.1 in `.python-version` file.

### Database Setup

Both stacks include:

- docker-compose.yml with Postgres
- Proper connection configuration
- Connection pooling
- Required psycopg/asyncpg dependencies

### Common Elements

Both stacks get:

- uv for dependency management
- ruff for linting
- .env.example with all required variables
- .gitignore with Python essentials
- README with clear setup instructions
- Health check endpoint
- CORS middleware (dev + prod config)
- Rate limiting
- Logging configuration

## Error Handling

If the target directory already contains a project:

- Warn the user
- Ask if they want to proceed anyway
- Suggest initializing in a different directory

If required tools are missing:

- Check for `uv` availability
- Provide installation instructions if needed

## Directory Naming Conventions

- Use kebab-case for project directories: `my-api-project`
- Use snake_case for Python packages: `my_api_project`
- Convert between them as needed when creating files
