---
title: Use Meaningful Related Names
impact: LOW
impactDescription: improves code readability on reverse lookups
tags: structure, models, related-name, foreignkey, readability
---

## Use Meaningful Related Names

Always set `related_name` on ForeignKey and ManyToMany fields to make reverse lookups readable.

**Incorrect:**

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # Access: post.comment_set.all() — unclear
```

**Correct:**

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # Access: post.comments.all() — clear and readable
```
