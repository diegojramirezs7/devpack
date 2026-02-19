---
title: Use only() and defer() to Limit Fetched Columns
impact: HIGH
impactDescription: reduces memory usage and query time for large text/binary columns
tags: database, orm, only, defer, column-selection, performance
---

## Use only() and defer() to Limit Fetched Columns

Avoid fetching large text/binary columns when you only need a few fields.

**Incorrect (fetches ALL columns including large body text):**

```python
posts = Post.objects.all()
for post in posts:
    print(post.title)
```

**Correct (only fetch needed columns):**

```python
# Only fetch the columns you need
posts = Post.objects.only('id', 'title', 'created_at')
for post in posts:
    print(post.title)

# Or defer the expensive ones
posts = Post.objects.defer('body', 'raw_html')
```
