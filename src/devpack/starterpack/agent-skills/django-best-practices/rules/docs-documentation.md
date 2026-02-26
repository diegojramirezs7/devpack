# docs-documentation

**Category**: Documentation
**Priority**: HIGH
**Prefix**: `docs-`

---

## Why It Matters

Well-documented Django code dramatically reduces onboarding time and prevents knowledge silos. Documentation should explain _why_ and _what_, not just _how_. This rule covers both inline docstrings for individual components and project-level spec documents.

---

## Component Documentation (Inline Docstrings)

### Applies to

`models.py`, `views.py`, `serializers.py`, `urls.py`, `settings.py`, `admin.py`, `tasks.py`, `signals.py`, and similar Django source files.

### Process

1. **Read the file carefully** before writing documentation. Understand relationships (ForeignKey, ManyToMany), business logic in methods, and anything non-obvious.
2. **Add Google-style docstrings** directly to the source file:
   - Every class gets a docstring explaining its purpose and role in the app.
   - Every non-trivial method/function gets `Args:`, `Returns:`, and `Raises:` sections where applicable. Skip truly self-evident one-liners like `__str__`.
   - **Models**: Document what the model represents, key fields, and important relationships.
   - **Views**: Document the endpoint served, expected inputs, and return value.
   - **Serializers**: Document the represented model and any custom validation logic.
   - **Settings**: Add inline comments explaining non-obvious settings, environment variables, and rationale.
3. **Don't over-document.** If a docstring just repeats the code, it adds noise.

### Incorrect

```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def cancel(self):
        if self.status == "shipped":
            raise ValueError("Cannot cancel shipped orders")
        self.status = "cancelled"
        self.save()
```

### Correct

```python
class Order(models.Model):
    """A customer purchase order.

    Tracks the lifecycle of an order from creation through fulfillment.
    Each order belongs to a single user and progresses through statuses:
    pending → confirmed → shipped → delivered (or cancelled at any point
    before shipping).

    Key fields:
        user: The customer who placed the order.
        total: Order total in USD, calculated at checkout.
        status: Current lifecycle state (see STATUS_CHOICES).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def cancel(self):
        """Cancel this order if it has not yet shipped.

        Raises:
            ValueError: If the order has already been shipped.
        """
        if self.status == "shipped":
            raise ValueError("Cannot cancel shipped orders")
        self.status = "cancelled"
        self.save()
```

---

## App Spec Documentation (Project-Level)

### When to Use

When a project-level overview, spec, or architectural summary is needed.

### Process

1. **Explore the project structure.** Identify all Django apps (directories with `models.py` or `apps.py`), settings files, `urls.py` files, and config files (`Dockerfile`, `.env.example`, `requirements.txt`, `celery.py`, etc.).
2. **Read key files** (prioritize in this order):
   - All `models.py` files (data shape and relationships)
   - Root and app-level `urls.py` (endpoint mapping)
   - `serializers.py` and `views.py` (API surface)
   - Settings file (environment, installed apps, auth, integrations)
   - `requirements.txt` or `pyproject.toml` (major dependencies)
3. **Write `SPEC.md`** in the project root using this template:

```markdown
# <Project Name> — App Spec

> One-paragraph summary of what this application does and who it's for.

---

## Data Models

For each Django app, describe its models and relationships.
Include a simple ASCII diagram if relationships are complex.

### <AppName>

- **<ModelName>**: What it represents. Key fields: `field1`, `field2`. Relates to: `OtherModel` (FK), `ThirdModel` (M2M).

---

## API Endpoints & Serializers

| Method | Path        | View         | Description                     |
| ------ | ----------- | ------------ | ------------------------------- |
| GET    | /api/users/ | UserListView | Returns paginated list of users |

Note serializers with custom validation or non-obvious field mappings.

---

## Auth & Permissions

- **Authentication method**: (JWT, session, token, etc.)
- **Permission classes in use**: List DRF permission classes and where applied.
- **Custom permissions**: Describe project-defined permission classes.
- **User model**: Default or custom? If custom, what fields are added?

---

## Settings & Configuration

- **Environment variables**: All env vars the app depends on.
- **Installed apps**: Significant third-party apps and why.
- **Key configuration decisions**: Non-default middleware, caching, CORS, etc.
- **Multiple settings files**: If split (base/dev/prod), explain the structure.

---

## Notes for Developers

Gotchas, known tech debt, non-standard patterns, important conventions.
```

---

## General Principles

- **Be precise, not exhaustive.** Make the codebase understandable to someone new without transcribing code into prose.
- **Write for the next developer.** What does someone intelligent but unfamiliar with this project need to be productive quickly?
- **When in doubt about intent, ask.** Don't guess and document incorrectly.
- **Flag surprises.** Models with no migrations, views manually managing transactions, suspicious settings — mention them in the Notes section.