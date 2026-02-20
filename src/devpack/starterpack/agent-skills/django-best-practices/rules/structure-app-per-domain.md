---
title: Organize Apps by Domain, One Responsibility Per App
impact: MODERATE
impactDescription: keeps apps focused, testable, and potentially reusable
tags: structure, apps, domain-driven, organization
---

## Organize Apps by Domain, One Responsibility Per App

Each app should have a clear, focused purpose.

**Correct project structure:**

```
project/
├── apps/
│   ├── accounts/       # User auth, profiles
│   ├── orders/         # Order management
│   ├── products/       # Product catalog
│   └── notifications/  # Email, push notifications
├── config/
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

Each app should be independently testable and potentially reusable.
