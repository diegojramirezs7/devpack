---
title: Use Per-View Caching for Read-Heavy Pages
impact: MODERATE
impactDescription: caches entire view responses to avoid repeated computation
tags: caching, views, decorators, cache-page
---

## Use Per-View Caching for Read-Heavy Pages

**Correct:**

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutes
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'products/list.html', {'products': products})
```
