---
title: Pass IDs, Not Objects, to Celery Tasks
impact: HIGH
impactDescription: prevents serialization errors and stale data issues
tags: async, celery, serialization, task-arguments
---

## Pass IDs, Not Objects, to Celery Tasks

Celery serializes task arguments. Pass database IDs and re-fetch inside the task to avoid stale data and serialization issues.

**Incorrect (passing model instance):**

```python
@shared_task
def process_order(order):  # Passing a model instance — breaks serialization
    order.status = 'processed'
    order.save()
```

**Correct (passing ID, re-fetching inside task):**

```python
@shared_task
def process_order(order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'processed'
    order.save()
```
