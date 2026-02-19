---
title: Invalidate Cache Properly
impact: HIGH
impactDescription: stale caches cause subtle bugs and data inconsistencies
tags: caching, invalidation, signals, consistency
---

## Invalidate Cache Properly

Stale caches cause subtle bugs. Use signals or explicit invalidation.

**Correct:**

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, **kwargs):
    cache.delete('popular_products')
    cache.delete('product_categories')
```
