---
title: Use Django's CSRF Protection
impact: HIGH
impactDescription: prevents cross-site request forgery attacks
tags: security, csrf, forms, middleware
---

## Use Django's CSRF Protection

Never disable CSRF middleware. Use `{% csrf_token %}` in every POST form.

**Incorrect:**

```python
@csrf_exempt  # Don't do this unless you have a very specific API reason
def my_view(request):
    ...
```

**Correct:**

```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

For APIs (DRF), use token or session authentication — both handle CSRF properly.
