---
title: Never Serve Static Files with Django in Production
impact: CRITICAL
impactDescription: Django's static file serving is single-threaded and not designed for production
tags: static-files, production, whitenoise, cdn, performance
---

## Never Serve Static Files with Django in Production

Django's static file serving is single-threaded and not designed for production.

**Incorrect:**

```python
# In production — using Django to serve statics
if DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# ^^^ This should NEVER be the production strategy
```

**Correct (WhiteNoise or CDN):**

```python
# Option 1: WhiteNoise (simple, works well for most apps)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add right after SecurityMiddleware
    # ...
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Option 2: CDN / object storage (S3, GCS, etc.)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```
