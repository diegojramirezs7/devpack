---
title: Offload Long-Running Work to Background Tasks
impact: CRITICAL
impactDescription: prevents request timeouts and poor user experience
tags: async, celery, background-tasks, email, performance
---

## Offload Long-Running Work to Background Tasks

Never block a request to send emails, generate reports, or call external APIs.

**Incorrect (blocking the request):**

```python
def register(request):
    user = User.objects.create_user(...)
    send_mail('Welcome!', 'Thanks for joining.', 'no-reply@example.com', [user.email])
    generate_welcome_pdf(user)  # Takes 5 seconds!
    return redirect('dashboard')
```

**Correct (non-blocking with Celery):**

```python
# tasks.py
from celery import shared_task

@shared_task
def send_welcome_email(user_id):
    user = User.objects.get(id=user_id)
    send_mail('Welcome!', 'Thanks for joining.', 'no-reply@example.com', [user.email])

@shared_task
def generate_welcome_pdf(user_id):
    ...

# views.py
def register(request):
    user = User.objects.create_user(...)
    send_welcome_email.delay(user.id)  # Non-blocking
    generate_welcome_pdf.delay(user.id)  # Non-blocking
    return redirect('dashboard')
```
