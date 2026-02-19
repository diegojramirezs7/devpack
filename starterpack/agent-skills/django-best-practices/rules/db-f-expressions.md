---
title: Use F() Expressions for Database-Level Operations
impact: MODERATE
impactDescription: prevents race conditions and reduces round trips
tags: database, orm, f-expressions, atomic-operations, race-conditions
---

## Use F() Expressions for Database-Level Operations

Avoid pulling data into Python just to update it. Use `F()` to perform operations at the database level, preventing race conditions.

**Incorrect (race condition with concurrent requests):**

```python
product = Product.objects.get(id=1)
product.views += 1  # Race condition if concurrent requests
product.save()
```

**Correct (atomic database operation):**

```python
from django.db.models import F

Product.objects.filter(id=1).update(views=F('views') + 1)
```
