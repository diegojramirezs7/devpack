# FastAPI Best Practices

Production-grade guidelines for FastAPI applications. Each rule includes rationale and code examples.

---

## 1. Async & Concurrency

### 🔴 Never block the event loop in async routes

FastAPI runs `async` routes directly on the event loop. If you call blocking code (e.g., `time.sleep`, synchronous HTTP clients, blocking file I/O) inside an `async def` route, the entire server freezes for all users.

```python
# ❌ Bad — blocks the event loop
@router.get("/data")
async def get_data():
    time.sleep(5)  # freezes entire server
    return {"ok": True}

# ✅ Good — use a sync def so FastAPI runs it in a threadpool
@router.get("/data")
def get_data():
    time.sleep(5)  # runs in threadpool, event loop stays free
    return {"ok": True}

# ✅ Best — use async I/O
@router.get("/data")
async def get_data():
    await asyncio.sleep(5)  # non-blocking
    return {"ok": True}
```

If the route does only non-blocking `await` calls, use `async def`. If it must call blocking libraries, use plain `def` (FastAPI offloads it to a threadpool automatically) or explicitly use `run_in_threadpool`.

### 🟡 Offload sync SDKs with run_in_threadpool

When you must use a synchronous library inside an async route, wrap the call.

```python
from fastapi.concurrency import run_in_threadpool

@router.get("/external")
async def call_external():
    result = await run_in_threadpool(sync_client.make_request, data=payload)
    return result
```

### 🟡 Use worker processes for CPU-intensive tasks

`await` and threadpools help with I/O-bound work. CPU-bound work (heavy computation, video transcoding, data crunching) blocks regardless because of the GIL. Offload to a process pool or a task queue.

```python
# Use a task queue like Celery, arq, or SAQ for heavy work
from app.worker import heavy_computation_task

@router.post("/process")
async def process_data(data: ProcessInput):
    task = heavy_computation_task.delay(data.dict())
    return {"task_id": task.id}
```

### 🟡 Prefer async dependencies

Sync dependencies run in a threadpool, which adds overhead. If a dependency does no I/O or only async I/O, declare it `async`.

```python
# ❌ Unnecessary threadpool overhead
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token)  # pure CPU, no I/O
    return payload["user_id"]

# ✅ No threadpool needed
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_token(token)
    return payload["user_id"]
```

### 🟢 Be aware of threadpool limits

FastAPI's default threadpool size is limited (typically 40 threads). If all threads are occupied by sync routes, new requests queue up. Monitor thread usage and increase the pool size if needed, or better yet, migrate to async I/O libraries.

---

## 2. Pydantic & Validation

### 🔴 Use Pydantic models for all request and response data

Pydantic gives you automatic validation, serialization, and OpenAPI schema generation. Never accept raw dicts from request bodies.

```python
from pydantic import BaseModel, Field, EmailStr
from enum import StrEnum

class UserRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    email: EmailStr
    role: UserRole = UserRole.MEMBER
```

Use Pydantic's built-in validators (regex, enums, constrained types, `EmailStr`, `AnyUrl`, etc.) before writing custom logic.

### 🟡 Create a custom base model for project-wide defaults

A shared base model lets you enforce consistent serialization (e.g., datetime format, camelCase aliasing) across all schemas without repeating config.

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict

def to_utc_isoformat(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.isoformat()

class AppBaseModel(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: to_utc_isoformat},
        populate_by_name=True,
        from_attributes=True,
    )
```

### 🟡 Separate request schemas from response schemas

Even when fields overlap, keep `Create`, `Update`, and `Response` models distinct. This prevents accidentally exposing internal fields (like hashed passwords) and lets each schema evolve independently.

```python
class UserCreate(AppBaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(AppBaseModel):
    email: EmailStr | None = None
    display_name: str | None = None

class UserResponse(AppBaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    created_at: datetime
    # password is never here
```

### 🟡 Decouple BaseSettings by domain

A single monolithic settings class becomes unmanageable. Split configuration into domain-specific classes.

```python
# src/auth/config.py
from pydantic_settings import BaseSettings

class AuthConfig(BaseSettings):
    JWT_ALG: str = "HS256"
    JWT_SECRET: str
    JWT_EXP_MINUTES: int = 15
    REFRESH_TOKEN_EXP_DAYS: int = 30

auth_settings = AuthConfig()

# src/config.py
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    DATABASE_URL: PostgresDsn
    ENVIRONMENT: str = "production"
    CORS_ORIGINS: list[str] = []

app_settings = AppConfig()
```

### 🟢 Be cautious with ValueErrors in Pydantic schemas

A `ValueError` raised inside a Pydantic validator that's used as a request body will be caught by FastAPI and returned as a 422 validation error with full detail. This is usually what you want, but be aware it happens — don't put sensitive information in the error message.

---

## 3. Dependency Injection

### 🔴 Use dependencies for request validation beyond schema checks

Pydantic validates shape and types. Dependencies validate business rules that require I/O (e.g., "does this entity exist?", "is this user authorized?"). This keeps route bodies clean and avoids duplicating checks.

```python
# dependencies.py
async def valid_post_id(post_id: UUID4) -> Post:
    post = await post_service.get_by_id(post_id)
    if not post:
        raise PostNotFound()
    return post

# router.py
@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post: Post = Depends(valid_post_id)):
    return post

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(data: PostUpdate, post: Post = Depends(valid_post_id)):
    return await post_service.update(post.id, data)
```

### 🟡 Chain dependencies for layered validation

Build complex validation from small, reusable pieces. FastAPI caches dependency results within a request, so shared deps are called only once.

```python
async def parse_jwt(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALG])
    except JWTError:
        raise InvalidCredentials()

async def get_current_user(payload: dict = Depends(parse_jwt)) -> User:
    user = await user_service.get_by_id(payload["sub"])
    if not user or not user.is_active:
        raise UserInactive()
    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise InsufficientPermissions()
    return user
```

### 🟡 Use Depends for dependency injection, not global variables

Injecting dependencies makes testing trivial — override with `app.dependency_overrides` instead of monkeypatching globals.

```python
# ❌ Global — hard to test, tightly coupled
db = DatabasePool()

@router.get("/items")
async def list_items():
    return await db.fetch_all("SELECT * FROM items")

# ✅ Injected — easy to mock and swap
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    return await db.execute(select(Item)).scalars().all()
```

### 🟢 Leverage dependency caching

FastAPI caches a dependency's return value per request by default. If you need a fresh instance per call, use `Depends(my_dep, use_cache=False)`.

---

## 4. API Design

### 🔴 Follow REST conventions consistently

Use plural nouns for collections, proper HTTP verbs, and consistent naming throughout.

```
GET    /api/v1/users          — list users
POST   /api/v1/users          — create user
GET    /api/v1/users/{id}     — get user
PUT    /api/v1/users/{id}     — replace user
PATCH  /api/v1/users/{id}     — partial update
DELETE /api/v1/users/{id}     — delete user
```

Use lowercase, hyphen-separated paths. Keep resource hierarchies logical: `/users/{id}/orders`.

### 🟡 Version your API

Include the version in the URL prefix so breaking changes don't affect existing consumers.

```python
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")
```

### 🟡 Set response_model, status_code, and descriptions on every route

This drives OpenAPI doc quality and enforces response shape at the framework level.

```python
@router.post(
    "/animals",
    response_model=AnimalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an animal",
    description="Register a new animal in the system",
    tags=["Animals"],
    responses={
        409: {"model": ErrorResponse, "description": "Animal already exists"},
    },
)
async def create_animal(data: AnimalCreate) -> AnimalResponse:
    ...
```

### 🟡 Add Field examples to Pydantic models for better docs

Examples appear directly in Swagger UI and help consumers understand expected formats.

```python
class AnimalCreate(BaseModel):
    name: str = Field(..., min_length=2, examples=["Simba", "Nala"])
    species: Species = Field(..., examples=["lion"])
    date_of_birth: date = Field(..., examples=["2020-01-15"])
```

### 🟢 Understand double serialization

FastAPI converts your Pydantic return object to a dict, then validates it against `response_model`, creating the model twice. For performance-critical routes, consider returning a dict directly and using `response_model_exclude_unset=True`.

---

## 5. Error Handling

### 🔴 Use domain-specific exceptions, not HTTPException in business logic

Business logic and service layers should not know about HTTP. Raise domain exceptions and map them to HTTP responses at the application layer.

```python
# exceptions.py
class AppException(Exception):
    pass

class EntityNotFound(AppException):
    def __init__(self, entity: str, id: Any):
        self.entity = entity
        self.id = id

class DuplicateEntity(AppException):
    pass

# main.py
@app.exception_handler(EntityNotFound)
async def not_found_handler(request: Request, exc: EntityNotFound):
    return JSONResponse(status_code=404, content={
        "error": f"{exc.entity} not found",
        "id": str(exc.id),
    })

@app.exception_handler(DuplicateEntity)
async def duplicate_handler(request: Request, exc: DuplicateEntity):
    return JSONResponse(status_code=409, content={"error": "Resource already exists"})
```

### 🟡 Return consistent error response shapes

Pick a format and stick with it across all endpoints. Consumers should be able to parse every error the same way.

```python
class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    code: str | None = None
```

### 🟢 Document error responses in the route decorator

FastAPI won't auto-generate error response docs. Add them manually with the `responses` parameter (see API Design section).

---

## 6. Security

### 🔴 Never hardcode secrets

Use environment variables via Pydantic `BaseSettings`. Never commit `.env` files to version control.

```python
class AuthConfig(BaseSettings):
    JWT_SECRET: str  # loaded from env
    model_config = ConfigDict(env_file=".env")
```

### 🔴 Configure CORS properly

Restrict origins to known domains. Never use `allow_origins=["*"]` in production.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS,  # explicit list
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 🟡 Hide docs in production

Unless your API is intentionally public, disable the OpenAPI docs endpoint outside development/staging.

```python
SHOW_DOCS = app_settings.ENVIRONMENT in ("local", "staging")

app = FastAPI(
    title="My API",
    openapi_url="/openapi.json" if SHOW_DOCS else None,
    docs_url="/docs" if SHOW_DOCS else None,
    redoc_url="/redoc" if SHOW_DOCS else None,
)
```

### 🟡 Validate and sanitize all user input

Pydantic handles type validation, but also constrain string lengths, use regex patterns, and validate enums to prevent injection attacks and abuse.

### 🟡 Use OAuth2 / JWT with proper expiration

Keep access tokens short-lived (5–15 minutes) and use refresh tokens for session continuity. Validate tokens in a dependency, not inline in routes.

### 🟢 Add rate limiting

Use middleware or a dependency to prevent abuse. Libraries like `slowapi` integrate with FastAPI.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/search")
@limiter.limit("30/minute")
async def search(request: Request, q: str):
    ...
```

---

## 7. Database & Migrations

### 🟡 Set explicit naming conventions for DB constraints

Let SQLAlchemy generate predictable constraint names so Alembic migrations are clean and reversible.

```python
from sqlalchemy import MetaData

NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

### 🟡 Follow consistent table naming rules

Use `lower_case_snake`, singular form (`user`, `post_like`), and group related tables with a module prefix (`payment_account`, `payment_bill`). Use `_at` suffix for datetime columns and `_date` for date columns.

### 🟡 Prefer SQL for complex data operations

Databases handle joins, aggregation, and filtering far more efficiently than Python. Do heavy lifting in SQL; use Pydantic to shape the output.

```python
# ✅ Let the database do the work
select_query = (
    select(Post.id, Post.title, func.count(PostLike.id).label("likes"))
    .join(PostLike, Post.id == PostLike.post_id, isouter=True)
    .group_by(Post.id)
    .order_by(desc("likes"))
)
```

### 🟡 Use descriptive Alembic migration names

Configure a human-readable file template so migration history is scannable.

```ini
# alembic.ini
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
```

Generate with: `alembic revision --autogenerate -m "add_user_email_index"`

Result: `2025-03-15_add_user_email_index.py`

### 🟡 Manage async database connections with lifespan

Use FastAPI's lifespan context manager to create and close connection pools cleanly.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.db_pool = await create_pool(app_settings.DATABASE_URL)
    yield
    # shutdown
    await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)
```

---

## 8. Testing

### 🔴 Set up an async test client from day one

Mixing sync and async test clients leads to event loop errors that are painful to debug later. Start async.

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_create_user(client: AsyncClient):
    resp = await client.post("/api/v1/users", json={"username": "testuser", "email": "t@t.com"})
    assert resp.status_code == 201
```

### 🟡 Override dependencies for isolated unit tests

Use `app.dependency_overrides` to swap real services for mocks. This keeps tests fast, deterministic, and free from external system dependencies.

```python
from app.dependencies import get_db

async def mock_db():
    yield FakeDatabase()

app.dependency_overrides[get_db] = mock_db

# test runs against FakeDatabase, no real DB needed
```

### 🟡 Use unit tests for most cases, integration tests for critical paths

Unit test individual services and dependencies with mocks. Reserve integration tests (which hit a real DB or external service) for end-to-end flows that must work together.

### 🟢 Use fixtures and conftest.py to reduce boilerplate

Share test client, sample data, and database setup across tests.

```python
# conftest.py
@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Str0ng!Pass"
    }
```

---

## 9. Performance & Deployment

### 🟡 Order middleware carefully

Middleware executes in the order it's added. Put CORS first, then auth/logging, then request processing. Incorrect ordering can cause subtle bugs (e.g., CORS headers missing on error responses).

### 🟡 Use streaming responses for large payloads

For file downloads or large data exports, stream instead of loading everything into memory.

```python
from fastapi.responses import StreamingResponse

@router.get("/export")
async def export_data():
    async def generate():
        async for row in db.stream_query("SELECT * FROM large_table"):
            yield row.to_csv_line()

    return StreamingResponse(generate(), media_type="text/csv")
```

### 🟡 Use structured logging

Configure structured JSON logging for production. This makes logs machine-parseable for aggregation tools like Datadog, Grafana, or CloudWatch.

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "timestamp": self.formatTime(record),
        })
```

### 🟡 Use Ruff for linting and formatting

Ruff replaces black, isort, autoflake, and flake8 in a single fast tool. Enforce it in CI.

```bash
#!/bin/sh
ruff check --fix src
ruff format src
```

### 🟢 Add health check endpoints

Provide a lightweight endpoint for load balancers and orchestrators. Optionally check downstream dependencies.

```python
@router.get("/health", status_code=200)
async def health():
    return {"status": "ok"}

@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unavailable"})
```

### 🟢 Run with Uvicorn behind a process manager

Use Gunicorn with Uvicorn workers for production, or use Uvicorn directly with a process manager like systemd or Docker. Configure workers based on CPU cores.

```bash
# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```