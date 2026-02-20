---
title: Always Validate and Sanitize User Input
impact: CRITICAL
impactDescription: prevents SQL injection, XSS, and other injection attacks
tags: security, input-validation, sql-injection, xss, sanitization
---

## Always Validate and Sanitize User Input

Never pass unsanitized user input to raw SQL, ORM extras, or template rendering.

**Incorrect (SQL injection and XSS risks):**

```python
# SQL injection risk
User.objects.raw(f"SELECT * FROM auth_user WHERE email = '{email}'")

# Template XSS risk
return HttpResponse(f"<h1>Hello {user_input}</h1>")
```

**Correct (parameterized queries and template auto-escaping):**

```python
# Parameterized queries
User.objects.raw("SELECT * FROM auth_user WHERE email = %s", [email])

# Or just use the ORM
User.objects.filter(email=email)

# Use templates with auto-escaping (on by default)
return render(request, 'hello.html', {'name': user_input})
```
