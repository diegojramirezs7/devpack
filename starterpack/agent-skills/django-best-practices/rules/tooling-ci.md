---
title: Use Continuous Integration
impact: HIGH
impactDescription: catches regressions on every commit
tags: tooling, ci, github-actions, testing, linting
---

## Use Continuous Integration

Run tests, linting, and type checking on every commit.

**Correct:**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: testdb
          POSTGRES_PASSWORD: postgres
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements/test.txt
      - run: ruff check .
      - run: python manage.py test --settings=config.settings.test
```
