---
title: Use In-Memory SQLite Database for Tests When Possible
impact: MODERATE
impactDescription: significantly speeds up test suite execution
tags: testing, sqlite, in-memory, performance, test-settings
---

## Use In-Memory SQLite Database for Tests When Possible

**Correct:**

```python
# config/settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']  # Faster hashing
```

Note: If you rely on PostgreSQL-specific features (JSONField lookups, array fields, full-text search), test against PostgreSQL instead.
