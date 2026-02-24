# DevPack Expansion Plan: Beyond Agent Skills

## Overview

DevPack currently runs one pipeline: detect the tech stack, match agent skills (SKILL.md bundles), prompt for selection, copy them into an IDE-specific directory, and update the README. The output is always files dropped into `.claude/skills/`, `.cursor/skills/`, or `.agents/skills/`.

This document outlines what else the tool can automatically add to a repo to enforce best practices — spanning AI tool config, IDE extensions, code quality tooling, documentation templates, security baselines, CI/CD workflows, and git hooks. Each phase builds on the last and introduces progressively more complex integration patterns.

---

## Extension Points in the Current Pipeline

The existing pipeline has three natural hooks for new features:

1. **New "pack types"** alongside agent skills — the same detect → match → prompt → write pattern can deliver other artifacts (config files, YAML workflows, `.vscode/extensions.json`, etc.).
2. **New writers** — `writer.py` currently does `shutil.copytree`. New writers can template-fill files, merge into existing JSON/YAML, or run shell commands.
3. **New starterpack directories** — `starterpack/` already has `agent-skills/`. New directories like `ai-config/`, `ide-extensions/`, `code-quality/`, `workflows/`, `git-hooks/` house the new artifacts.

### Safety principle

The tool should follow a **"never overwrite, always extend"** rule for everything outside IDE skill directories:
- If a file exists: offer to merge or skip, never replace.
- If unsure how to merge: skip and print a manual instruction.
- Always report what was added, what was skipped, and why.

---

## Phase 1 — AI Tool Config Files and Ignore Files

**Goal:** Seed the repo with AI assistant context and prevent secrets from leaking into LLM context windows.

**Integration pattern:** These are mostly new files dropped at the repo root or a known path. Very low risk — they are either skipped if they already exist or safely merged (append-only for ignore files).

### AI ignore files

| File | Tool |
|---|---|
| `.claudeignore` | Claude Code |
| `.cursorignore` | Cursor |
| `.aiignore` | General convention |
| `.copilotignore` | GitHub Copilot (emerging) |

A universal baseline to copy into all repos:
```
.env
.env.*
*.pem
*.key
*.p12
secrets/
```

**How it works:** Pure copy-if-not-exists. If the file already exists, append only the missing entries with an `# Added by devpack` comment block. No risk of data loss.

---

### AI config/instruction files

| File | Tool |
|---|---|
| `CLAUDE.md` | Claude Code |
| `.cursorrules` | Cursor |
| `.github/copilot-instructions.md` | GitHub Copilot |

These files are generated (not copied from a static template) using the Claude SDK. The output is a focused, repo-specific document with three sections:

1. **Stack summary** — what the project is, key commands, and detected conventions. Already available from `StackDetectionResult.summary`.
2. **Directory structure** — a concise, annotated map of the top-level directories and important files so the AI assistant understands the layout without having to re-explore on every session.
3. **Installed skills** — a list of the agent skills selected during this DevPack run, with a one-line description of each, so the assistant knows which skills are available to call on.

**How it works:** After the user confirms skill selection (end of the `prompter.py` step), DevPack makes a second Claude SDK call — a lightweight agent with `Glob` access to the target repo. It is given the stack summary and skill list and asked to produce the directory structure section and assemble the full config file. This keeps the output grounded in the actual repo rather than a generic template. The SDK call uses structured output or a tightly constrained prompt so the result is deterministic enough to write directly.

These files are only written if they don't already exist — a hand-crafted `CLAUDE.md` should never be overwritten. If the file exists, offer to append only the skills list section (which is the most likely thing to be out of date).

---

## Phase 2 — IDE Extensions

**Goal:** Ensure every collaborator who opens the repo gets prompted to install the right extensions for the stack.

**Integration pattern:** A JSON file listing extension IDs. The tool merges into the file if it exists (read → deduplicate → write) or creates it if it doesn't. No runtime behavior — the IDE does the prompting.

### Extension recommendation files

| IDE | File |
|---|---|
| VS Code | `.vscode/extensions.json` |
| Cursor | `.vscode/extensions.json` (Cursor reads the same file) |

**How it works:** DevPack maintains a registry of extension IDs per tech tag. At write time, it reads the existing file (if any), appends the stack-matched IDs, deduplicates, and writes back. The format is a simple JSON object with a `"recommendations"` array — safe to merge programmatically.

### What gets recommended (examples)

| Stack | Extensions |
|---|---|
| React / TS | ESLint, Prettier, Tailwind IntelliSense, Vitest runner |
| Django | Python, Pylance, Django template support, Black formatter |
| All repos | EditorConfig, GitLens, Conventional Commits |
| Frontend | Axe Accessibility Linter |

---

## Phase 3 — Linter, Formatter, and Editor Config Files

**Goal:** Give developers in-editor feedback on style and correctness before any hook or CI run. Standardize line endings, indentation, and tool configuration across the team.

**Integration pattern:** Config files dropped at the repo root. Preference is to write a standalone config file rather than modify an existing one (e.g., `ruff.toml` instead of merging into `pyproject.toml`). If a config file already exists, skip and report.

### Files added by stack

| File | Stack | Purpose |
|---|---|---|
| `.editorconfig` | All | Tabs vs spaces, line endings, trailing whitespace — respected by nearly every editor without a plugin |
| `ruff.toml` | Python | Linting rules and line length. Written standalone to avoid touching `pyproject.toml` |
| `pyproject.toml` snippet | Python (if no `pyproject.toml` exists yet) | Minimal Black + Ruff config |
| `.prettierrc` | JS / TS | Formatting rules |
| `eslint.config.js` | JS / TS | ESLint flat config (ESLint 9+ standard) |
| `tsconfig.json` | TypeScript (only if none exists) | Strict mode baseline — skipped if any `tsconfig` is detected |

**How it works:** DevPack copies a stack-matched template from `starterpack/code-quality/`. `.editorconfig` is always safe to add. For Python, `ruff.toml` is preferred over touching `pyproject.toml`. For JS/TS, the flat config format (`eslint.config.js`) is used. `tsconfig.json` is only written if no `tsconfig*.json` exists in the repo — too many valid project-specific shapes exist to merge safely.

---

## Phase 4 — Documentation Templates

**Goal:** Reduce onboarding friction and standardize contribution workflows with templates GitHub renders natively.

**Integration pattern:** Static files copied only if they don't already exist. No merging needed — templates are standalone. Frontend-detected repos get an accessibility checklist added to the PR template.

### Files added

| File | Purpose |
|---|---|
| `CONTRIBUTING.md` | Local setup, branch naming, PR process |
| `.github/pull_request_template.md` | Checklist for PR authors (description, tests, a11y check if frontend) |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Structured bug reports |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Structured feature requests |
| `SECURITY.md` | Responsible disclosure policy |
| `CHANGELOG.md` | Starter changelog following Keep a Changelog format |

**How it works:** Pure copy-if-not-exists. `CONTRIBUTING.md` is templated with commands inferred from `StackDetectionResult.summary` (e.g., the detected dev server command is inserted automatically). The PR template conditionally includes an accessibility checklist when frontend tech is in the detected stack.

---

## Phase 5 — Security Baseline

**Goal:** Prevent accidental secret exposure and keep dependencies up to date automatically.

**Integration pattern:** `.gitignore` is merged (append missing entries). `dependabot.yml` and `.env.example` are copy-if-not-exists. No destructive writes.

### Files added

| File | Purpose |
|---|---|
| `.gitignore` (merge) | Append missing entries: `.env`, `*.pem`, `*.key`, `__pycache__`, `.DS_Store`, `node_modules` |
| `.env.example` | Documents required environment variables with placeholder values |
| `.github/dependabot.yml` | Automated dependency update PRs, ecosystem-specific |
| `SECURITY.md` | (if not added in Phase 4) Basic responsible disclosure policy |

**How it works:** For `.gitignore`, DevPack reads the existing file, checks for a list of critical entries, and appends any that are missing under an `# Added by devpack` block — never removing or reordering existing entries. For `dependabot.yml`, the package ecosystem is inferred from the detected stack (npm, pip, docker) and a template is filled accordingly.

---

## Phase 6 — CI/CD Workflows

**Goal:** Enforce quality gates on every push and PR, catching issues that local tooling might miss.

**Integration pattern:** New files written to `.github/workflows/`. Never overwrite existing workflow files — check for filename collisions and skip with a message if one exists. Templates use placeholder tokens (`{{PYTHON_VERSION}}`, `{{DEFAULT_BRANCH}}`) filled from the detected stack.

### Workflows added

| Workflow | Stack | What it does |
|---|---|---|
| `ci.yml` | All | Lint + test on every PR |
| `secret-scan.yml` | All | Runs `gitleaks` on every push |
| `lighthouse.yml` | Frontend | Accessibility + performance audit via Lighthouse CI |
| `dependency-audit.yml` | Python / JS | `pip audit` or `npm audit` on schedule |

**How it works:** DevPack maintains stack-specific YAML templates in `starterpack/workflows/`. At write time, placeholder tokens are replaced with values inferred from `StackDetectionResult` (Python version, Node version, test command). Only workflows that don't conflict with existing files are written. Post-install output lists what was written and what manual steps remain (e.g., configuring secrets in GitHub Settings).

---

## Phase 7 — Pre-commit Hooks and Code Analysis Scripts

**Goal:** Block bad commits at the source — catching secrets, style violations, and type errors before they enter the history.

**Integration pattern:** The most complex integration. Repos often already have `.pre-commit-config.yaml` or a `husky` setup. DevPack checks first: if no config exists, copy the stack-specific template; if one exists, offer to add individual missing hooks rather than replacing the file. Post-install instructions are always printed.

### What gets added

**Universal (all stacks):**
- `detect-secrets` — blocks commits containing secrets or API keys
- `trailing-whitespace`, `end-of-file-fixer`, `check-merge-conflict` (pre-commit built-ins)
- `conventional-pre-commit` — commit message format check

**Python stacks (Django, FastAPI, Flask):**
- `ruff` — linting + auto-fix
- `black` — formatting
- `bandit` — security linting
- `mypy` — type checking (opt-in, noted as slow)

**JS/TS stacks (React, Next.js, Vue, Express):**
- `eslint` via `husky` + `lint-staged`
- `prettier` — formatting
- `@commitlint/cli` — commit message format
- `tsc --noEmit` (TypeScript only)

**Django specifically:**
- `djhtml` — Django template formatting
- `django-upgrade` — auto-upgrade deprecated patterns

**How it works:** For Python repos, DevPack writes `.pre-commit-config.yaml` from a stack-matched template and prints `pre-commit install`. For Node repos, it generates a `husky` + `lint-staged` config and prints `npm install && npx husky install`. If a config already exists, it diffs the existing hooks against the template and offers to add only the missing ones — never removing anything. The tool cannot run `pre-commit install` itself (it can't touch the developer's global git config), so a clear post-install reminder is always shown.

---

## Architectural Implications

### New model: `Pack`

The current `Skill` model maps to agent-skill directories. New pack types need a parallel model:

```python
Pack(id, name, description, type, path, tags)
# type ∈ {agent-skill, config-file, workflow, documentation, git-hook}
```

The `prompter.py` groups packs by type in the interactive selection UI, making it clear what category each item belongs to.

### Writer behaviors by pack type

| Pack type | Writer behavior |
|---|---|
| `agent-skill` | `shutil.copytree` (existing behavior) |
| `config-file` | Copy if not exists, or merge (type-aware: JSON dedupe, append-only for plaintext) |
| `workflow` | Copy to `.github/workflows/` only if no file with the same name exists |
| `documentation` | Copy if not exists |
| `git-hook` | Write `.pre-commit-config.yaml` or `package.json` changes + print setup reminder |

### Template engine

Some files need variable substitution (Python version, project name, detected commands). A lightweight approach: Python's `str.replace()` with sentinel tokens (`{{PROJECT_NAME}}`, `{{PYTHON_VERSION}}`). No need for Jinja2 unless templates grow complex.

---

## What to Ignore (Non-Automatable)

The following are valuable practices but not suitable for repo-level automation:

- **Jira standards, sprint ceremonies, project roles** — process, not code
- **Slack setup, communications cadence** — outside the repo
- **Architecture decisions (migration patterns, legacy modernization)** — context-dependent; agent skills are the right format here
- **Figma conventions** — design tooling, not dev tooling
- **Sphinx documentation generation** — requires understanding of module structure; better as an on-demand agent skill than a static config
