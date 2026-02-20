---
title: Enable HTTPS Security Headers
impact: HIGH
impactDescription: enforces encrypted transport and prevents downgrade attacks
tags: security, https, hsts, cookies, ssl, headers
---

## Enable HTTPS Security Headers

Always enforce HTTPS and set security headers in production.

**Correct:**

```python
# Production settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```
