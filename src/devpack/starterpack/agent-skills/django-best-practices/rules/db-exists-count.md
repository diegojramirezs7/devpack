---
title: Use exists() and count() Instead of Evaluating Entire QuerySets
impact: MODERATE
impactDescription: avoids loading all objects into memory for simple checks
tags: database, orm, exists, count, queryset, performance
---

## Use exists() and count() Instead of Evaluating Entire QuerySets

Don't load all objects into memory just to check if something exists or count rows.

**Incorrect (loads ALL matching objects into memory):**

```python
if len(User.objects.filter(email=email)):  # Loads ALL matching users
    raise ValidationError("Email taken")

total = len(Order.objects.filter(status='pending'))  # Loads all rows
```

**Correct (efficient database operations):**

```python
if User.objects.filter(email=email).exists():  # SELECT 1 ... LIMIT 1
    raise ValidationError("Email taken")

total = Order.objects.filter(status='pending').count()  # SELECT COUNT(*)
```
