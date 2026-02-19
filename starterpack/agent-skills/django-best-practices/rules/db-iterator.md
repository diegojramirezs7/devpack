---
title: Use iterator() for Large QuerySet Processing
impact: MODERATE
impactDescription: prevents memory exhaustion when processing large datasets
tags: database, orm, iterator, memory, large-datasets, performance
---

## Use iterator() for Large QuerySet Processing

When processing large datasets, `iterator()` avoids caching the entire queryset in memory.

**Correct:**

```python
# Process millions of rows without memory issues
for order in Order.objects.filter(status='completed').iterator(chunk_size=2000):
    process_order(order)
```

Without `iterator()`, Django caches the entire queryset result in memory, which can cause out-of-memory errors on large tables.
