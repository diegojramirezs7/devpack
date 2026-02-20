---
title: Use Django's Password Validation and Hashing
impact: HIGH
impactDescription: prevents weak passwords and plaintext storage
tags: security, passwords, hashing, authentication, validators
---

## Use Django's Password Validation and Hashing

Never store plaintext passwords. Use Django's built-in auth system.

**Correct:**

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```
