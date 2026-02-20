---
title: Use django-debug-toolbar in Development
impact: HIGH
impactDescription: essential for spotting N+1 queries, slow templates, and cache misses
tags: tooling, debug-toolbar, development, profiling
---

## Use django-debug-toolbar in Development

Essential for spotting N+1 queries, slow templates, and cache misses.

**Correct:**

```python
# config/settings/development.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```
