---
name: django-best-practices
description: Django application best practices covering ORM performance, security, project structure, caching, testing, and deployment. This skill should be used when writing, reviewing, or refactoring Django code to ensure correct patterns and optimal performance. Triggers on tasks involving Django models, views, serializers, settings, migrations, or deployment configuration.
license: MIT
metadata:
  author: community
  version: "1.0.0"
---

# Django Best Practices

Comprehensive best practices guide for Django applications. Contains 45+ rules across 9 categories, prioritized by impact to guide automated refactoring, code review, and code generation.

## When to Apply

Reference these guidelines when:

- Writing new Django models, views, or services
- Reviewing code for performance or security issues
- Refactoring existing Django applications
- Configuring Django settings for production deployment
- Setting up testing infrastructure
- Working with Celery or async tasks

## Rule Categories by Priority

| Priority | Category                      | Impact   | Prefix       |
| -------- | ----------------------------- | -------- | ------------ |
| 1        | Database & ORM Performance    | CRITICAL | `db-`        |
| 2        | Security                      | CRITICAL | `security-`  |
| 3        | Project Structure             | HIGH     | `structure-` |
| 4        | Caching                       | HIGH     | `cache-`     |
| 5        | Static Files & Media          | HIGH     | `static-`    |
| 6        | Testing                       | HIGH     | `testing-`   |
| 7        | Async & Background Tasks      | HIGH     | `async-`     |
| 8        | Configuration & Deployment    | CRITICAL | `deploy-`    |
| 9        | Development Tooling & Quality | MEDIUM   | `tooling-`   |

## Quick Reference

### 1. Database & ORM Performance (CRITICAL)

- `db-select-related` - Eliminate N+1 queries with select_related and prefetch_related
- `db-prefetch-objects` - Use Prefetch objects for nested relation optimization
- `db-only-defer` - Use only() and defer() to limit fetched columns
- `db-values-list` - Use values() or values_list() when model instances aren't needed
- `db-f-expressions` - Use F() expressions for database-level operations
- `db-bulk-operations` - Use bulk_create and bulk_update for batch operations
- `db-indexes` - Add database indexes on frequently filtered/ordered fields
- `db-exists-count` - Use exists() and count() instead of evaluating entire querysets
- `db-iterator` - Use iterator() for large queryset processing
- `db-connection-pooling` - Use database connection pooling in production

### 2. Security (CRITICAL)

- `security-debug-off` - Never run DEBUG=True in production
- `security-secret-key` - Keep SECRET_KEY out of source control
- `security-allowed-hosts` - Configure ALLOWED_HOSTS properly
- `security-https-headers` - Enable HTTPS security headers
- `security-input-validation` - Always validate and sanitize user input
- `security-csrf` - Use Django's CSRF protection
- `security-password-hashing` - Use Django's password validation and hashing
- `security-mass-assignment` - Protect against mass assignment
- `security-deploy-checklist` - Run the deployment checklist

### 3. Project Structure (HIGH)

- `structure-custom-user-model` - Use a custom User model from day one
- `structure-split-settings` - Split settings by environment
- `structure-thin-views` - Keep business logic out of views
- `structure-app-per-domain` - Organize apps by domain, one responsibility per app
- `structure-app-urls` - Use app-level urls.py and include in root
- `structure-related-names` - Use meaningful related names on relationships

### 4. Caching (HIGH)

- `cache-backend` - Use a proper cache backend in production
- `cache-querysets` - Cache expensive querysets and computations
- `cache-per-view` - Use per-view caching for read-heavy pages
- `cache-template-fragment` - Use template fragment caching for partial content
- `cache-invalidation` - Invalidate cache properly on writes

### 5. Static Files & Media (HIGH)

- `static-no-django-serve` - Never serve static files with Django in production
- `static-collectstatic` - Always run collectstatic in deployment
- `static-upload-validation` - Validate and limit user-uploaded files
- `static-cache-busting` - Use content-hash file names for cache busting

### 6. Testing (HIGH)

- `testing-write-tests` - Write tests from the start
- `testing-factories` - Use factories instead of fixtures
- `testing-setup-test-data` - Use setUpTestData for expensive setup
- `testing-sqlite-memory` - Use in-memory SQLite database for tests when possible

### 7. Async & Background Tasks (HIGH)

- `async-background-tasks` - Offload long-running work to background tasks
- `async-celery-ids` - Pass IDs, not objects, to Celery tasks
- `async-views` - Use async views for I/O-bound operations

### 8. Configuration & Deployment (CRITICAL)

- `deploy-env-variables` - Use environment variables for all configuration
- `deploy-gunicorn` - Use Gunicorn or Uvicorn behind a reverse proxy
- `deploy-logging` - Configure logging properly
- `deploy-health-check` - Use health check endpoints
- `deploy-pin-dependencies` - Pin dependencies and use lock files

### 9. Development Tooling & Quality (MEDIUM)

- `tooling-debug-toolbar` - Use django-debug-toolbar in development
- `tooling-linting` - Use linting and formatting tools
- `tooling-type-hints` - Use type hints with django-stubs
- `tooling-migrations` - Use migrations responsibly
- `tooling-ci` - Use continuous integration

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/db-select-related.md
rules/security-input-validation.md
```

Each rule file contains:

- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references
