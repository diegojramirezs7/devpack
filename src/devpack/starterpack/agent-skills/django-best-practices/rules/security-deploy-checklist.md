---
title: Run the Deployment Checklist
impact: MODERATE
impactDescription: catches missing security settings before deployment
tags: security, deployment, checklist, audit
---

## Run the Deployment Checklist

Django includes a built-in security checker.

**Correct:**

```bash
python manage.py check --deploy
```

This warns about missing security settings like `SECURE_SSL_REDIRECT`, `CSRF_COOKIE_SECURE`, etc. Run it as part of your CI/CD pipeline.
