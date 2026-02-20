---
title: Use Health Check Endpoints
impact: MODERATE
impactDescription: enables load balancers and orchestrators to monitor app health
tags: deployment, health-check, monitoring, load-balancer
---

## Use Health Check Endpoints

**Correct:**

```python
# health/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        connection.ensure_connection()
        return JsonResponse({'status': 'healthy'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)
```
