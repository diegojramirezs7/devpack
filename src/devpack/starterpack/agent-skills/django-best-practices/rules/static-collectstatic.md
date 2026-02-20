---
title: Always Run collectstatic in Deployment
impact: HIGH
impactDescription: ensures static files are gathered and served correctly
tags: static-files, deployment, collectstatic
---

## Always Run collectstatic in Deployment

```bash
python manage.py collectstatic --noinput
```

Configure `STATIC_ROOT` to point to the directory your web server or WhiteNoise serves from. Include this in your deployment pipeline.
