---
title: Use a Proper Cache Backend in Production
impact: CRITICAL
impactDescription: default in-memory cache does not persist across processes
tags: caching, redis, memcached, backend, production
---

## Use a Proper Cache Backend in Production

The default in-memory cache does not persist across processes.

**Incorrect (per-process, no sharing):**

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

**Correct (Redis with django-redis):**

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'myapp',
        'TIMEOUT': 300,  # Default 5 minute TTL
    }
}
```
