---
title: Use Type Hints
impact: LOW
impactDescription: improves IDE support and catches bugs early
tags: tooling, type-hints, django-stubs, mypy, typing
---

## Use Type Hints

Type hints improve IDE support and catch bugs early. Use `django-stubs` for Django-specific types.

**Correct:**

```python
from django.http import HttpRequest, HttpResponse

def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {'product': product})
```
