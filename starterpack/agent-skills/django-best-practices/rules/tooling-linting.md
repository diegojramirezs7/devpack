---
title: Use Linting and Formatting Tools
impact: MODERATE
impactDescription: consistent code formatting reduces review friction
tags: tooling, linting, ruff, formatting, code-quality
---

## Use Linting and Formatting Tools

Consistent code formatting reduces review friction and prevents style debates.

**Correct:**

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "DJ"]  # DJ = Django-specific rules

[tool.ruff.lint.isort]
known-first-party = ["apps"]
```
