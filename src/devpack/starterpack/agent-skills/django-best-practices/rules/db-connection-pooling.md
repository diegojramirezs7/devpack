---
title: Use Database Connection Pooling
impact: HIGH
impactDescription: reduces connection overhead for high-traffic applications
tags: database, connection-pooling, postgresql, performance, deployment
---

## Use Database Connection Pooling

Django creates a new database connection per request by default. Use connection pooling for high-traffic apps.

**Correct (Django 5.1+ built-in connection pooling):**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'pool': {
                'min_size': 2,
                'max_size': 10,
            },
        },
    }
}
```

For older Django versions, use external pooling solutions like PgBouncer.
