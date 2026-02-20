---
title: Use values() or values_list() When Model Instances Aren't Needed
impact: HIGH
impactDescription: skips model instantiation overhead for raw data access
tags: database, orm, values, values-list, performance, serialization
---

## Use values() or values_list() When Model Instances Aren't Needed

If you only need raw data (for serialization, aggregation, or template rendering), skip model instantiation entirely.

**Incorrect (instantiates full model objects):**

```python
emails = [user.email for user in User.objects.all()]
```

**Correct (returns raw values directly):**

```python
emails = list(User.objects.values_list('email', flat=True))
```
