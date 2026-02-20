---
title: Use Migrations Responsibly
impact: HIGH
impactDescription: prevents data loss and downtime from migration mistakes
tags: tooling, migrations, data-migrations, schema, database
---

## Use Migrations Responsibly

- Never edit migration files after they've been applied in production.
- Squash migrations periodically to keep the history manageable.
- Use `RunPython` for data migrations, keeping them reversible.
- Always add `db_index` to fields you query by, but be aware that adding indexes on large tables locks the table.

**Correct (data migration with reverse function):**

```python
from django.db import migrations

def populate_slug(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    for post in Post.objects.filter(slug=''):
        post.slug = slugify(post.title)
        post.save(update_fields=['slug'])

def reverse_slug(apps, schema_editor):
    pass  # Slug removal is safe to skip

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_slug, reverse_slug),
    ]
```
