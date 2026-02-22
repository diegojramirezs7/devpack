# DevPack

CLI tool that detects a repo's tech stack and installs matching agent skills into your IDE's skills directory (`.claude/skills/`, `.cursor/skills/`, `.agents/skills/`).

## Installation

**Requires Python 3.11+**

```bash
git clone git@github.com:diegojramirezs7/devpack.git
cd devpack
uv tool install -e .
devpack configure
```

`uv tool install` puts `devpack` in your PATH in an isolated environment. The `-e` flag means `git pull` picks up changes immediately — no reinstall needed.

> **Alternative:** `pipx install -e .` works the same way if you prefer pipx.

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

## Shell completions

DevPack supports tab completion for bash, zsh, and fish. Run once after installing:

```bash
devpack --install-completion   # detects your current shell automatically
```

To preview what gets added to your shell config without writing it:

```bash
devpack --show-completion
```

After installing, restart your shell (or `source ~/.zshrc`) to activate completions.

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
uv run pytest -m "not integration"

# Run integration tests (requires ANTHROPIC_API_KEY)
uv run pytest -m integration
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for a full guide including project structure, how to add a skill, and the release process.
