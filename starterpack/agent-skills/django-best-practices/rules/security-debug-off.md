---
title: Never Run DEBUG=True in Production
impact: CRITICAL
impactDescription: exposes full tracebacks, settings, and environment details publicly
tags: security, debug, production, configuration
---

## Never Run DEBUG=True in Production

Debug mode exposes full tracebacks, settings, and environment details to anyone who triggers an error.

**Incorrect:**

```python
# settings.py
DEBUG = True  # In production — exposes secrets, paths, SQL queries
```

**Correct:**

```python
import os

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
```
