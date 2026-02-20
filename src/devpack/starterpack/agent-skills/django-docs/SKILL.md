---
name: django-docs
description: >
  Generates documentation for Django projects. Use this skill whenever the user wants to
  document a Django app — whether that means adding docstrings to a specific file (models.py,
  views.py, serializers.py, settings.py, urls.py, etc.) or generating a high-level spec
  document for an entire Django project. Trigger this skill for any request like "document
  my models", "add docstrings to this view", "generate a spec for my Django app", "write
  docs for my serializers", or anytime a .py file from a Django project is being discussed
  and documentation is the goal.
---

# Django Documentation Skill

This skill has two modes that work together:

- **Component mode**: Reads a Django source file, adds Google-style docstrings inline, and produces a companion markdown reference for that component.
- **App spec mode**: Scans an entire Django project and produces a single structured `SPEC.md` giving a high-level overview.

You can run either mode independently or both together.

---

## Component Mode

### When to use it

The user points you at a specific file or set of files: `models.py`, `views.py`, `serializers.py`, `urls.py`, `settings.py`, `admin.py`, `tasks.py`, `signals.py`, or similar.

### What to do

**Step 1 — Read the file carefully.**
Understand what the code does before writing a single word of documentation. Pay attention to relationships (ForeignKey, ManyToMany), business logic in methods, and anything non-obvious.

**Step 2 — Add Google-style docstrings directly to the source file.**
Edit the actual file. Rules:
- Every class gets a docstring explaining its purpose and role in the app.
- Every non-trivial method or function gets a docstring with `Args:`, `Returns:`, and `Raises:` sections where applicable. Skip boilerplate one-liners like `__str__` only if they're truly self-evident.
- For Django models specifically: document what the model represents, its key fields, and any important relationships.
- For views: document what endpoint it serves, expected inputs, and what it returns.
- For serializers: document what model it represents and any custom validation logic.
- For settings files: add inline comments explaining non-obvious settings, environment variables, and why certain values are set the way they are.
- Don't over-document. A docstring that just repeats the code adds noise. Focus on *why* and *what*, not *how* when the code already shows that clearly.

---

## App Spec Mode

### When to use it

The user asks for a project-level overview, a spec, or an architectural summary of their Django app.

### What to do

**Step 1 — Explore the project structure.**
Walk the directory tree. Identify all Django apps (directories with `models.py` or `apps.py`), the settings file(s), `urls.py` files, and any notable configuration files (`Dockerfile`, `.env.example`, `requirements.txt`, `celery.py`, etc.).

**Step 2 — Read the key files.**
You don't need to read every line of every file. Prioritize:
- All `models.py` files (to understand data shape and relationships)
- Root and app-level `urls.py` (to map endpoints)
- `serializers.py` and `views.py` (to understand the API surface)
- Settings file (to understand environment, installed apps, auth config, third-party integrations)
- `requirements.txt` or `pyproject.toml` (to note major dependencies)

**Step 3 — Write `SPEC.md` in the project root.**

Use this fixed template:

```markdown
# <Project Name> — App Spec

> One-paragraph summary of what this application does and who it's for.

---

## Data Models

For each Django app, describe its models and how they relate to each other.
Include a simple ASCII or text diagram if relationships are complex.

### <AppName>
- **<ModelName>**: What it represents. Key fields: `field1`, `field2`. Relates to: `OtherModel` (ForeignKey), `ThirdModel` (M2M).
[repeat]

---

## API Endpoints & Serializers

Group endpoints by app or router prefix. For each endpoint:

| Method | Path | View | Description |
|--------|------|------|-------------|
| GET | /api/users/ | UserListView | Returns paginated list of users |
[...]

Note any serializers with custom validation or non-obvious field mappings.

---

## Auth & Permissions

- **Authentication method**: (e.g., JWT via djangorestframework-simplejwt, session auth, token auth)
- **Permission classes in use**: List the DRF permission classes and where they're applied.
- **Custom permissions**: Describe any project-defined permission classes.
- **User model**: Default or custom? If custom, what fields are added?

---

## Settings & Configuration

- **Environment variables**: List all env vars the app depends on (from `.env.example` or `os.environ` calls in settings).
- **Installed apps**: Note any significant third-party apps and why they're there.
- **Key configuration decisions**: Anything non-default worth understanding (custom middleware, caching setup, CORS config, etc.).
- **Multiple settings files**: If the project splits settings (base/dev/prod), explain the structure.

---

## Notes for Developers

Anything a new developer joining this project should know that isn't obvious from the code:
gotchas, known tech debt, non-standard patterns, important conventions.
```

---

## General Principles

**Be precise, not exhaustive.** The goal is to make the codebase understandable to someone new, not to transcribe the code into prose. If something is self-evident from reading the code, don't repeat it.

**Write for the next developer.** Imagine someone intelligent but unfamiliar with this specific project. What do they need to know to be productive quickly?

**When in doubt about intent, ask.** If a method or class has unclear purpose and there's no obvious inference from context, it's better to ask the user than to guess and document it wrong.

**Flag surprises.** If you encounter something unusual — a model with no migrations, a view that manually manages transactions, settings that look like they might be wrong — mention it in the Notes section. You're not just a transcriber; you're also a second pair of eyes.