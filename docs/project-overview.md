# Project Overview

## What DevPack Does

In one sentence: **you point `devpack add-skills` at any repo, it figures out what tech that repo uses, and then copies relevant "skill" files into it so your AI coding assistant knows how to work with that stack.**

---

## The Big Picture: A 6-Step Pipeline

Every time you run `devpack add-skills [path]`, execution flows linearly through `cli.py`:

```
User's repo
    │
    ▼
1. DETECT   → Ask Claude "what tech is in this repo?"
    │
    ▼
2. MATCH    → Filter the bundled skills down to relevant ones
    │
    ▼
3. PROMPT   → Show the user checkboxes to confirm skills + IDE
    │
    ▼
4. WRITE    → Copy skill directories into the target repo
    │
    ▼
5. README   → Append a skills table to the repo's README.md
    │
    ▼
Done ✓
```

---

## The Entry Point: `cli.py`

This is where the command is defined. It uses **Typer**, which is a library that turns a Python function into a CLI command — similar to how you might use `argparse`, but much less boilerplate.

```python
@app.command("add-skills")
def add_skills(repo_path: Path = Path(".")):
    ...
```

The `repo_path` argument defaults to `.` (the current directory), so running `devpack add-skills` with no arguments targets wherever you are in your terminal. The `pyproject.toml` registers `devpack = "devpack.cli:app"` as the installed script, which is how `devpack` becomes a runnable command after `uv pip install -e .`.

---

## Step 1: Detection — `detector.py` + `claude_agent.py`

`detector.py` is a thin synchronous wrapper:

```python
def detect_stack(repo_path) -> list[DetectedTechnology]:
    result = asyncio.run(detect_tech_stack(repo_path))  # runs the async agent
    return result.technologies
```

The real work is in `claude_agent.py`. It uses the **Claude Agent SDK** to spawn a Claude agent that actually reads the target repo's files (`package.json`, `pyproject.toml`, etc.) and figures out the stack. Key design choices here:

- The agent is given a **constrained list** of technology IDs (`KNOWN_TECHNOLOGY_IDS` in `registry/known_ids.py`) so it can't hallucinate made-up tech names.
- The output is **structured** — Claude is forced to return a JSON object matching the `StackDetectionResult` Pydantic schema, which includes a list of `DetectedTechnology` objects and a human-readable summary.
- The agent uses `async for message in query(...)` because the SDK streams messages; we only care about the final `ResultMessage`.

---

## Step 2: Matching — `matcher.py`

After detection, we have a list of `DetectedTechnology` objects. Now we load all bundled skills from `starterpack/agent-skills/` and filter to the relevant ones.

**How skills are stored:** Each skill is a directory (e.g., `django-best-practices/`) containing a `SKILL.md` with YAML frontmatter:

```yaml
---
name: django-best-practices
description: Django application best practices covering ORM performance...
---
```

`load_skills()` reads each `SKILL.md`, parses the frontmatter, and returns `Skill` dataclass instances.

`match_skills()` uses a **3-tier relevance check** (`_is_relevant()`):

1. **Always included** — skills in `GENERAL_SKILL_IDS` (currently just `feature-implementation-plan`)
2. **Tech match** — skill ID or description mentions a detected technology (e.g., "django" in `django-best-practices`)
3. **Frontend wildcard** — if any frontend tech is detected, include skills with keywords like "web", "accessibility", "lighthouse"

---

## Step 3: Prompting — `prompter.py`

Uses **InquirerPy** for interactive terminal UI — think the checkbox menus you see in some CLI installers.

Two prompts:
1. **Skill selection** — a checkbox list of matched skills, all pre-checked. User can deselect any.
2. **IDE selection** — a single-select for Claude Code, Cursor, or VS Code Copilot. It auto-detects which one to default to by checking if `.claude/`, `.cursor/`, or `.agents/` already exists in the target repo.

---

## Step 4: Writing — `writer.py`

The simplest module. For each selected skill, it does:

```python
shutil.copytree(skill.path, dest, dirs_exist_ok=True)
```

That's a standard library recursive directory copy. `dest` is `<repo>/<ide.skill_path>/<skill-id>/` — for example `.claude/skills/django-best-practices/` for Claude Code.

---

## Step 5: README Update — `readme_updater.py`

Appends (or replaces, if it already ran before) a markdown table into the target repo's `README.md`. It uses HTML comment markers as anchors:

```
<!-- devpack-skills -->
...table...
<!-- /devpack-skills -->
```

On a re-run, it finds and replaces the existing section rather than duplicating it.

---

## The Data Models — `models.py`

Three core types:

| Type | What it represents |
|---|---|
| `DetectedTechnology` | One detected tech (e.g., `id="django"`, `name="Django"`, `is_frontend=False`) |
| `Skill` | One bundled skill (id, name, description, path on disk) |
| `IDETarget` | One of the 3 supported IDEs, with its target skill directory path |

`DetectedTechnology` and `StackDetectionResult` are Pydantic models (used for Claude's structured output). `Skill` and `IDETarget` are plain dataclasses (used for internal logic).

---

## The Starterpack

`src/devpack/starterpack/agent-skills/` is the bundled library of skills. Currently it has 9:

```
accessibility-best-practices
django-best-practices
django-docs
express-best-practices
feature-implementation-plan
optimize-lighthouse-metrics
react-best-practices
react-docs
website-tags-best-practices
```

Each skill directory can contain a `rules/` subdirectory with additional files — all of it gets copied verbatim into the target repo.

---

## Key Dependencies

| Library | Role |
|---|---|
| `typer` | CLI framework (argument parsing, help text, exit codes) |
| `inquirerpy` | Interactive terminal checkboxes/selects |
| `pydantic` | Data validation + JSON schema generation for Claude's structured output |
| `pyyaml` | Parse YAML frontmatter in SKILL.md files |
| `claude-agent-sdk` | Runs the Claude agent for stack detection |
| `python-dotenv` | Loads `ANTHROPIC_API_KEY` from `.env` |
