---
title: Keep SECRET_KEY Out of Source Control
impact: CRITICAL
impactDescription: leaked key allows session forgery and token manipulation
tags: security, secret-key, environment-variables, source-control
---

## Keep SECRET_KEY Out of Source Control

The `SECRET_KEY` is used for cryptographic signing (sessions, tokens, password resets). If leaked, attackers can forge sessions.

**Incorrect:**

```python
SECRET_KEY = 'django-insecure-abc123hardcoded'
```

**Correct:**

```python
import os

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']  # Fail loudly if not set
```
