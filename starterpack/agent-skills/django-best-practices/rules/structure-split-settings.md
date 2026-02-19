---
title: Split Settings by Environment
impact: HIGH
impactDescription: prevents dev settings from leaking into production
tags: structure, settings, configuration, environments
---

## Split Settings by Environment

Don't use a single settings.py for dev and production.

**Correct project structure:**

```
config/
├── settings/
│   ├── __init__.py
│   ├── base.py          # Shared settings
│   ├── development.py   # DEBUG=True, local DB
│   ├── production.py    # Security hardened
│   └── test.py          # Fast test settings
```

```python
# config/settings/development.py
from .base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Use environment variables to select: `DJANGO_SETTINGS_MODULE=config.settings.production`
