---
title: Use a Custom User Model from Day One
impact: CRITICAL
impactDescription: changing user model after initial migration is extremely painful
tags: structure, user-model, auth, models
---

## Use a Custom User Model from Day One

Changing the user model after initial migration is extremely painful. Always start with a custom model.

**Incorrect:**

```python
# Using Django's built-in User model directly
from django.contrib.auth.models import User
```

**Correct:**

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass  # Add custom fields later as needed

# settings.py
AUTH_USER_MODEL = 'accounts.User'
```

Always reference the user model dynamically:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
```
