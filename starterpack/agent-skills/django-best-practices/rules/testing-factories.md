---
title: Use Factories Instead of Fixtures
impact: HIGH
impactDescription: factories are more maintainable and flexible than JSON fixtures
tags: testing, factory-boy, fixtures, test-data
---

## Use Factories Instead of Fixtures

Fixtures are brittle and hard to maintain. Use factory_boy for test data.

**Incorrect (brittle JSON fixtures):**

```python
# fixtures/test_data.json — breaks when models change
[{"model": "accounts.user", "pk": 1, "fields": {"username": "test"}}]
```

**Correct (factory_boy):**

```python
# tests/factories.py
import factory
from apps.accounts.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')

# In tests
user = UserFactory()
admin = UserFactory(is_staff=True, is_superuser=True)
```
