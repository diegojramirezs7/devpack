---
title: Add Database Indexes on Frequently Filtered/Ordered Fields
impact: HIGH
impactDescription: prevents full table scans on large tables
tags: database, orm, indexes, composite-index, partial-index, performance
---

## Add Database Indexes on Frequently Filtered/Ordered Fields

Missing indexes cause full table scans on large tables.

**Incorrect (no indexes):**

```python
class Order(models.Model):
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_email = models.EmailField()
    # No indexes — queries filtering by status or created_at are slow
```

**Correct (indexed fields with composite and partial indexes):**

```python
class Order(models.Model):
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    customer_email = models.EmailField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),  # Composite index
            models.Index(
                fields=['status'],
                condition=models.Q(status='pending'),
                name='pending_orders_idx',  # Partial index
            ),
        ]
```
