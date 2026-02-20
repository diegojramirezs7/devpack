---
title: Cache Expensive QuerySets and Computations
impact: HIGH
impactDescription: avoids redundant database hits for infrequently changing data
tags: caching, querysets, computations, performance
---

## Cache Expensive QuerySets and Computations

Cache database queries and computed results that don't change frequently.

**Correct:**

```python
from django.core.cache import cache

def get_popular_products():
    key = 'popular_products'
    products = cache.get(key)
    if products is None:
        products = list(
            Product.objects.filter(is_active=True)
            .annotate(order_count=Count('orderitem'))
            .order_by('-order_count')[:20]
        )
        cache.set(key, products, timeout=60 * 15)  # 15 minutes
    return products
```
