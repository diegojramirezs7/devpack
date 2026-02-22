# DevPack

CLI tool that detects a repo's tech stack and installs matching agent skills into your IDE's skills directory (`.claude/skills/`, `.cursor/skills/`, `.agents/skills/`).

## Installation

**Requires Python 3.11+**

```bash
# Install in editable mode (until published to PyPI)
uv pip install -e .

# Once published, the recommended install will be:
# pipx install devpack
```

> `pipx` installs CLI tools in an isolated environment and automatically adds them to your PATH — no virtual environment activation needed.

## Quick start

**1. Configure your Anthropic API key:**

```bash
devpack configure
```

This walks you through saving your key to `~/.config/devpack/.env` (or your preferred location). You can get an API key at [console.anthropic.com](https://console.anthropic.com).

**2. Add skills to a repo:**

```bash
devpack add-skills                  # target: current directory
devpack add-skills ./path/to/repo   # target: specific path
```

DevPack will analyze the repo with Claude, show you a checklist of matching skills, and copy them into the IDE directory you choose.

## Commands

| Command | Description |
|---|---|
| `devpack add-skills [PATH]` | Detect stack and install matching skills |
| `devpack configure` | Set up your Anthropic API key |
| `devpack doctor` | Check that your installation is healthy |
| `devpack --version` | Print the installed version |

## Options

```bash
devpack add-skills --debug [PATH]   # show full tracebacks and verbose API logs
```

## How it works

1. **Detect** — a Claude agent reads the repo's manifest files (`package.json`, `pyproject.toml`, etc.) and identifies the tech stack
2. **Match** — the detected technologies are matched against the bundled skill library
3. **Select** — you confirm which skills to add and which IDE to target
4. **Write** — skill directories are copied into `<repo>/<ide>/skills/<skill-id>/`
5. **README** — a skills table is appended to the repo's `README.md`

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests (no API key needed)
pytest -m "not integration"

# Run integration tests (requires ANTHROPIC_API_KEY)
pytest -m integration
```
