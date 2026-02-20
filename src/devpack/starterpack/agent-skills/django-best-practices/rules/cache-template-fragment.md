---
title: Use Template Fragment Caching for Partial Content
impact: MODERATE
impactDescription: caches expensive template blocks without caching entire pages
tags: caching, templates, fragment-caching, partial-content
---

## Use Template Fragment Caching for Partial Content

Cache expensive template blocks instead of entire pages.

**Correct:**

```django
{% load cache %}

{% cache 600 sidebar request.user.id %}
    {# Expensive sidebar content #}
    {% for notification in notifications %}
        <div>{{ notification.message }}</div>
    {% endfor %}
{% endcache %}
```
