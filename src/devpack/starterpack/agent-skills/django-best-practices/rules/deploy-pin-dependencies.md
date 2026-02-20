---
title: Pin Dependencies and Use Lock Files
impact: HIGH
impactDescription: ensures deterministic builds and prevents unexpected breakage
tags: deployment, dependencies, requirements, lock-files, reproducibility
---

## Pin Dependencies and Use Lock Files

**Correct:**

```
# requirements/base.txt
Django==5.2.*
psycopg2-binary==2.9.*
celery==5.4.*

# requirements/production.txt
-r base.txt
gunicorn==22.*
django-redis==5.*
sentry-sdk==2.*
```

Or better yet, use `pyproject.toml` with `uv`, `poetry`, or `pip-tools` for deterministic builds.
