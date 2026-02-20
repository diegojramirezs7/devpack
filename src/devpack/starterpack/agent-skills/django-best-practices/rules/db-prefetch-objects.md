---
title: Use Prefetch Objects for Nested Relation Optimization
impact: HIGH
impactDescription: prevents nested N+1 queries in complex relation chains
tags: database, orm, prefetch, nested-relations, performance
---

## Use Prefetch Objects for Nested Relation Optimization

When prefetched objects themselves have ForeignKey relationships, use `Prefetch` with a custom queryset to avoid a second layer of N+1.

**Incorrect (nested N+1):**

```python
# Prefetches chapters, but each chapter.editor triggers another query
books = Book.objects.prefetch_related('chapters').all()
for book in books:
    for chapter in book.chapters.all():
        print(chapter.editor.name)  # N+1 inside N+1!
```

**Correct (Prefetch with select_related):**

```python
from django.db.models import Prefetch

books = Book.objects.prefetch_related(
    Prefetch('chapters', queryset=Chapter.objects.select_related('editor'))
).all()
for book in books:
    for chapter in book.chapters.all():
        print(chapter.editor.name)  # Already loaded
```
