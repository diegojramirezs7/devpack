---
title: Use Content-Hash File Names for Cache Busting
impact: MODERATE
impactDescription: ensures browsers load updated static files after deployments
tags: static-files, cache-busting, manifest, hashing
---

## Use Content-Hash File Names for Cache Busting

**Correct:**

```python
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
# Produces filenames like: css/style.a1b2c3d4.css
```

This ensures browsers always fetch the latest version of static files after deployments.
