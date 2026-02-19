---
title: Use Async Views for I/O-Bound Operations
impact: MODERATE
impactDescription: enables concurrent I/O without blocking the event loop
tags: async, views, httpx, asyncio, django-4
---

## Use Async Views for I/O-Bound Operations

Django 4.1+ supports native async views. Use them when calling external APIs or performing concurrent I/O.

**Correct:**

```python
import httpx

async def dashboard(request):
    async with httpx.AsyncClient() as client:
        weather, news = await asyncio.gather(
            client.get('https://api.weather.com/current'),
            client.get('https://api.news.com/headlines'),
        )
    return render(request, 'dashboard.html', {
        'weather': weather.json(),
        'news': news.json(),
    })
```

Note: The ORM is not fully async yet. Wrap sync ORM calls with `sync_to_async`:

```python
from asgiref.sync import sync_to_async

@sync_to_async
def get_user(user_id):
    return User.objects.get(id=user_id)
```
