---
title: Use Gunicorn or Uvicorn Behind a Reverse Proxy
impact: CRITICAL
impactDescription: manage.py runserver is single-threaded and insecure for production
tags: deployment, gunicorn, uvicorn, nginx, production, wsgi, asgi
---

## Use Gunicorn or Uvicorn Behind a Reverse Proxy

Never use `manage.py runserver` in production.

**Correct:**

```bash
# WSGI (synchronous)
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000

# ASGI (if using async views or WebSockets)
uvicorn config.asgi:application --workers 4 --host 0.0.0.0 --port 8000
```

Put Nginx or a load balancer in front for SSL termination, static files, and connection management.
