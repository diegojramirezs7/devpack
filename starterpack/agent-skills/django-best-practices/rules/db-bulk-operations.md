---
title: Use bulk_create and bulk_update for Batch Operations
impact: MODERATE
impactDescription: reduces N insert/update queries to 1-2 batch queries
tags: database, orm, bulk-create, bulk-update, batch-operations, performance
---

## Use bulk_create and bulk_update for Batch Operations

Avoid saving objects one by one in a loop.

**Incorrect (N insert queries):**

```python
for item in items_data:
    Item.objects.create(name=item['name'], price=item['price'])
```

**Correct (single batch query):**

```python
items = [Item(name=d['name'], price=d['price']) for d in items_data]
Item.objects.bulk_create(items, batch_size=1000)

# For updates:
for item in items:
    item.price = item.price * 1.1
Item.objects.bulk_update(items, ['price'], batch_size=1000)
```
