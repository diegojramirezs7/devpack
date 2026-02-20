# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Dev Pack

CLI tool (`devpack add-skills`) that detects a target repo's tech stack via a Claude agent and installs matching agent skills (SKILL.md bundles) into IDE-specific directories (`.claude/skills/`, `.cursor/skills/`, `.agents/skills/`).

## Commands

```bash
# Install in editable mode (required for correct starterpack/ path resolution)
uv pip install -e ".[dev]"

# Run the CLI
devpack add-skills [PATH]        # defaults to current directory

# Tests (unit, no API key needed)
pytest

# Skip integration tests explicitly
pytest -m "not integration"

# Run integration tests (requires ANTHROPIC_API_KEY)
pytest -m integration

# Run a single test file
pytest tests/test_matcher.py
```

Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` before running the CLI or integration tests.

## Architecture

The `add-skills` command follows a linear pipeline in `cli.py`:

1. **Detect** (`detector.py` → `claude_agent.py`): Spawns a Claude agent via `claude-agent-sdk` with `Read/Glob/Grep` tools against the target repo. Returns a validated `StackDetectionResult` (Pydantic model). The agent is constrained to `KNOWN_TECHNOLOGY_IDS` (`registry/known_ids.py`) to prevent hallucinated tech IDs.

2. **Match** (`matcher.py`): Loads skills from `starterpack/agent-skills/` by parsing YAML frontmatter in each `SKILL.md`. Matches skills to the detected stack by text-matching tech names against skill IDs/descriptions. Frontend skills are matched by keyword (`web`, `accessibility`, etc.) when any frontend tech is detected. `feature-implementation-plan` is always included.

3. **Prompt** (`prompter.py`): Interactive checkboxes (InquirerPy) for skill selection and IDE target selection. Auto-detects an existing IDE config dir in the target repo to set the default.

4. **Write** (`writer.py`): `shutil.copytree` each selected skill directory into `<repo>/<ide.skill_path>/<skill-id>/`.

5. **Update README** (`readme_updater.py`): Appends or replaces a `<!-- devpack-skills -->…<!-- /devpack-skills -->` section in the target repo's README.

### Key models (`models.py`)

- `DetectedTechnology(id, name, is_frontend)` — Pydantic
- `StackDetectionResult(technologies, summary)` — Pydantic; used as structured output schema for the Claude agent
- `Skill(id, name, description, path)` — dataclass
- `IDETarget(id, name, skill_path)` — dataclass; three singletons: `CLAUDE_CODE`, `CURSOR`, `VSCODE`

### Skill format (`starterpack/agent-skills/<skill-id>/`)

Each skill is a directory with a `SKILL.md` whose YAML frontmatter must include `name` and `description`. Additional reference/rule files in subdirectories are copied verbatim.

### Starterpack path

`_STARTERPACK_PATH` in `cli.py` resolves relative to the installed package file — this works for editable installs (`uv pip install -e .`) but would need adjustment for a distributed package.

## Test structure

- Unit tests mock `detect_tech_stack` (the async Claude call) via `unittest.mock.AsyncMock`.
- Integration tests (`@pytest.mark.integration`) hit the real API and use fixture repos in `tests/fixtures/`.
- Fixtures: `django_repo/`, `react_repo/`, `node_repo/`, `empty_repo/`.
