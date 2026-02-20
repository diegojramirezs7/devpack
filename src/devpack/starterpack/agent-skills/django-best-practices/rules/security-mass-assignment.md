---
title: Protect Against Mass Assignment
impact: MODERATE
impactDescription: prevents users from setting unauthorized fields like is_superuser
tags: security, mass-assignment, forms, serializers
---

## Protect Against Mass Assignment

Never blindly pass request data to model creation.

**Incorrect (user can set is_superuser=True):**

```python
User.objects.create(**request.POST.dict())  # User can set is_superuser=True!
```

**Correct (use forms or serializers to whitelist fields):**

```python
form = UserRegistrationForm(request.POST)
if form.is_valid():
    form.save()
```
