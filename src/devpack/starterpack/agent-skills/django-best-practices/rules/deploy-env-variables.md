---
title: Use Environment Variables for All Configuration
impact: CRITICAL
impactDescription: prevents hardcoded credentials and enables environment-specific config
tags: deployment, environment-variables, configuration, secrets
---

## Use Environment Variables for All Configuration

Never hardcode database credentials, API keys, or secrets.

**Correct:**

```python
import os

# Or use django-environ / python-decouple
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```
