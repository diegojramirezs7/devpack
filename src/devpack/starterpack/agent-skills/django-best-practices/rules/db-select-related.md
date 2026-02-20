---
title: Eliminate N+1 Queries with select_related and prefetch_related
impact: CRITICAL
impactDescription: "#1 Django performance killer, can reduce queries from N+1 to 1-2"
tags: database, orm, n-plus-one, select-related, prefetch-related, performance
---

## Eliminate N+1 Queries with select_related and prefetch_related

The N+1 problem is Django's #1 performance killer. Every time you access a related object in a loop without prefetching, Django issues a separate query.

**Incorrect (N+1: 1 query for books + N queries for each book's author):**

```python
books = Book.objects.all()
for book in books:
    print(book.author.name)  # Separate query per book!
```

**Correct (single query with SQL JOIN):**

```python
# ForeignKey / OneToOne → use select_related (SQL JOIN, single query)
books = Book.objects.select_related('author').all()
for book in books:
    print(book.author.name)  # No additional query

# ManyToMany / reverse FK → use prefetch_related (separate query, joined in Python)
authors = Author.objects.prefetch_related('books').all()
for author in authors:
    print(list(author.books.all()))  # No additional query
```

**When to use which:**

- `select_related`: ForeignKey, OneToOneField — uses SQL JOIN, single query.
- `prefetch_related`: ManyToManyField, reverse ForeignKey — uses separate queries + Python join.
