---
title: Configure ALLOWED_HOSTS Properly
impact: CRITICAL
impactDescription: prevents HTTP Host header attacks
tags: security, allowed-hosts, host-header, configuration
---

## Configure ALLOWED_HOSTS Properly

An empty or wildcard `ALLOWED_HOSTS` enables HTTP Host header attacks.

**Incorrect:**

```python
ALLOWED_HOSTS = ['*']  # Accepts any Host header
```

**Correct:**

```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
# e.g., DJANGO_ALLOWED_HOSTS=example.com,www.example.com
```
