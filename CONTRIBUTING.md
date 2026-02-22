# Contributing to DevPack

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — used for all dependency management
- An Anthropic API key (only needed for integration tests)

## Dev setup

```bash
git clone https://github.com/diegojramirezs7/devpack
cd devpack
uv pip install -e ".[dev]"
devpack configure   # saves your API key to ~/.config/devpack/.env
```

Verify everything is working:

```bash
devpack doctor
```

## Running tests

```bash
# Unit tests — no API key needed, run these freely
uv run pytest -m "not integration"

# Integration tests — hit the real Claude API, cost tokens
uv run pytest -m integration

# Single file
uv run pytest tests/test_matcher.py
```

Unit tests mock the Claude agent call (`detect_tech_stack`) with `AsyncMock`, so they run offline and quickly. Integration tests use fixture repos in `tests/fixtures/` and require `ANTHROPIC_API_KEY` to be set.

## Project structure

```
src/devpack/
├── cli.py              # Entry point — all commands defined here
├── config.py           # API key loading and storage
├── detector.py         # Thin wrapper: calls claude_agent.py via asyncio.run()
├── claude_agent.py     # Claude agent that reads the target repo and detects the stack
├── matcher.py          # Matches detected technologies to bundled skills
├── prompter.py         # InquirerPy interactive prompts (skill + IDE selection)
├── writer.py           # shutil.copytree each skill into the target repo
├── readme_updater.py   # Appends/replaces the skills table in the target README
├── models.py           # Pydantic + dataclass types shared across modules
├── registry/
│   └── known_ids.py    # Constrained list of technology IDs the agent can return
└── starterpack/
    └── agent-skills/   # Bundled skill directories, each with a SKILL.md
```

## Adding a skill

Each skill is a directory under `src/devpack/starterpack/agent-skills/<skill-id>/`. It must contain a `SKILL.md` with YAML frontmatter:

```markdown
---
name: my-skill-name
description: One sentence describing what this skill covers and which tech it applies to.
---

... skill content ...
```

The `description` field is what the matcher uses to link the skill to detected technologies, so make sure it mentions the relevant tech names (e.g. "Django", "React"). Additional files and subdirectories inside the skill folder are copied verbatim into the target repo.

To test that your skill is matched correctly, add a fixture repo to `tests/fixtures/` and write a unit test in `tests/test_matcher.py`.

## Release process

1. Work on a feature branch, open a PR into `main`
2. Once `main` is in a releasable state, tag the commit: `git tag v0.2.0`
3. Open a PR from `main` into `release` — CI runs tests automatically
4. Merge the PR — the publish workflow builds the wheel and uploads to PyPI
