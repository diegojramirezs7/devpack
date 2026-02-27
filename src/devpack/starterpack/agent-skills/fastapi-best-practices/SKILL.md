---
name: fastapi-best-practices
description: FastAPI performance, security, and code quality guidelines for production Python APIs. This skill should be used when writing, reviewing, or refactoring FastAPI code to ensure optimal patterns. Triggers on tasks involving FastAPI routes, Pydantic models, dependency injection, async handlers, database integration, error handling, testing, or API design. Use this skill whenever the user mentions FastAPI, Starlette, Pydantic in an API context, or Python REST/HTTP API development.
metadata:
  tags:
    - fastapi
---

# FastAPI Best Practices

Comprehensive best practices guide for FastAPI applications, distilled from production systems and community expertise.

This skill contains 40+ rules across 9 categories, prioritized by impact on performance, security, and maintainability.

## How to Use

Read `references/rules.md` in this directory for the full categorized rule set. Each rule includes the rationale and concrete code examples so you can apply them directly when writing or reviewing FastAPI code.

## Categories

1. **Async & Concurrency** — Correct use of async/sync routes, threadpool offloading, CPU-bound task handling
2. **Pydantic & Validation** — Schema design, custom base models, settings decomposition, field validators
3. **Dependency Injection** — Request validation via deps, chaining, caching, async preference
4. **API Design** — REST conventions, versioning, response models, status codes, OpenAPI docs
5. **Error Handling** — Domain exceptions, centralized handlers, structured error responses
6. **Security** — CORS, secrets management, auth patterns, input sanitization, docs visibility
7. **Database & Migrations** — Naming conventions, SQL-first patterns, Alembic workflow, connection management
8. **Testing** — Async test clients, dependency overrides, unit vs integration strategy
9. **Performance & Deployment** — Middleware ordering, response streaming, caching headers, logging, linting

## Priority

Rules are tagged with impact level:

- 🔴 **Critical** — Gets it wrong and your app breaks or has a security hole
- 🟡 **Important** — Significant impact on maintainability, performance, or developer experience
- 🟢 **Recommended** — Good practice that improves code quality over time
