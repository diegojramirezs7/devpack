# DevPack Expansion Plan: Beyond Agent Skills

## Overview

DevPack currently runs one pipeline: detect the tech stack, match agent skills (SKILL.md bundles), prompt for selection, copy them into an IDE-specific directory, and update the README. The output is always files dropped into `.claude/skills/`, `.cursor/skills/`, or `.agents/skills/`.

This document outlines what else the tool can automatically add to a repo to enforce best practices — spanning AI tool config, IDE extensions, code quality tooling, documentation templates, security baselines, CI/CD workflows, and git hooks. Each phase builds on the last and introduces progressively more complex integration patterns.

---

## Extension Points in the Current Pipeline

The `init` command (Phase 0) runs all phases in sequence using a single `ProjectContext` gathered upfront. Each phase is a new extension point — given the same context object, it decides what to write, merge, or skip.

New starterpack directories house the artifacts for each phase: `starterpack/` already has `agent-skills/`. New directories like `ai-config/`, `ide-extensions/`, `code-quality/`, `workflows/`, `git-hooks/` will follow.

### Safety principle

The tool follows a **"never overwrite, always extend"** rule for everything outside IDE skill directories:
- If a file exists: merge or skip, never replace.
- If unsure how to merge: skip and print a manual instruction.
- Always report what was added, what was skipped, and why.

---

## Phase 0 — `init` Command and Project Context

**Goal:** Introduce `devpack init` as the primary orchestrator and establish a single upfront Claude SDK call that gathers everything every downstream phase needs — so no phase ever triggers a redundant API call.

---

### The `init` command

`devpack init [PATH]` is the new entry point for full repo setup. It runs all phases in sequence, passing a shared `ProjectContext` object through each step.

`devpack add-skills` is **unchanged** — it continues to run its own detect → match → prompt → write pipeline independently and is unaffected by this work.

---

### The initial SDK call — `ProjectContext`

Currently `detect_tech_stack` returns `StackDetectionResult(technologies, summary)`. The `init` command uses an extended version of this call that returns a richer model:

```python
class SetupCommands:
    install: str | None   # e.g. "npm install", "pip install -r requirements.txt"
    dev:     str | None   # e.g. "npm run dev", "python manage.py runserver"
    test:    str | None   # e.g. "pytest", "npm test"
    build:   str | None   # e.g. "npm run build"

class ProjectContext:
    technologies:        list[DetectedTechnology]  # for skill matching
    summary:             str                        # short project description
    directory_structure: str                        # annotated top-level tree with key files noted
    setup_commands:      SetupCommands              # inferred from package.json, Makefile, etc.
    runtime_versions:    dict[str, str]             # e.g. {"python": "3.11", "node": "20"}
```

The agent uses the same `Read/Glob/Grep` tools as the existing detector, but the prompt is extended to also capture structure, setup commands, and runtime versions. The result is validated as structured output before the pipeline continues.

**What each field is used for:**

| Field | Used by |
|---|---|
| `technologies` | Skill matching, IDE extension matching, linter config selection, pre-commit hook selection |
| `summary` | `agents.md` stack summary section |
| `directory_structure` | `agents.md` directory structure section |
| `setup_commands` | `agents.md` key commands, `CONTRIBUTING.md` template, CI workflow templates |
| `runtime_versions` | CI workflow templates (Python/Node version matrix), linter config defaults |

---

### `init` pipeline

```
devpack init [PATH]
    │
    ├─ 1. SDK call → ProjectContext          (single API call, all context gathered here)
    │
    ├─ 2. Match skills                       (uses ProjectContext.technologies)
    ├─ 3. Prompt: skill + IDE selection
    ├─ 4. Write skills
    │
    ├─ 5. Phase 1 — AI config files          (uses ProjectContext + selected skills)
    ├─ 6. Phase 2 — IDE extensions           (uses ProjectContext.technologies)
    ├─ 7. Phase 3 — Linter/formatter config  (uses ProjectContext.technologies + runtime_versions)
    ├─ 8. Phase 4 — Documentation templates  (uses ProjectContext.setup_commands + technologies)
    ├─ 9. Phase 5 — Security baseline        (uses ProjectContext.technologies)
    ├─ 10. Phase 6 — CI/CD workflows         (uses ProjectContext.runtime_versions + setup_commands)
    ├─ 11. Phase 7 — Pre-commit hooks        (uses ProjectContext.technologies)
    │
    └─ N. Summary: print what was written, what was skipped, and any manual steps required
```

Each phase receives `ProjectContext` and the list of selected skills. No phase triggers its own detection call.

---

## Phase 1 — AI Tool Config Files and Ignore Files

**Goal:** Seed the repo with AI assistant context and prevent secrets from leaking into LLM context windows.

**Integration pattern:** Ignore files are merged entry-by-entry. `agents.md` is assembled in-process from `ProjectContext` — no additional SDK call needed.

---

### AI ignore files

| File | Tool |
|---|---|
| `.claudeignore` | Claude Code |
| `.cursorignore` | Cursor |
| `.copilotignore` | GitHub Copilot |

**Universal baseline:**
```
.env
.env.*
*.pem
*.key
*.p12
secrets/
```

**How it works:** Each file is handled independently. If the file does not exist, it is created with the full baseline. If it already exists, each baseline entry is checked individually — entries already present are left untouched, missing entries are appended at the end under an `# Added by devpack` comment. Nothing is removed or reordered.

---

### AI config/instruction file

Every IDE gets a single `agents.md` at the repo root — one shared file readable by Claude Code, Cursor, GitHub Copilot, and any other AI assistant.

`agents.md` is assembled in-process from `ProjectContext` and the selected skills list. No additional SDK call is made. The output contains three sections:

1. **Stack summary** — sourced from `ProjectContext.summary`.
2. **Directory structure** — sourced from `ProjectContext.directory_structure`.
3. **Key commands** — sourced from `ProjectContext.setup_commands` (install, dev, test, build).
4. **Installed skills** — the list of skills selected during this `init` run, with a one-line description of each.

**How it works:**
- **File does not exist** → assemble and write `agents.md` in full.
- **File already exists** → do not overwrite. Offer to update only the **Installed skills** section, since that is the part most likely to be out of date after a new DevPack run.

---

## Phase 2 — IDE Extensions

**Goal:** Ensure every collaborator who opens the repo gets prompted to install the right extensions for the stack.

**Integration pattern:** A JSON file listing extension IDs. Merged into the file if it exists (read → deduplicate → write), created if it doesn't. No runtime behavior — the IDE does the prompting.

### Extension recommendation files

| IDE | File |
|---|---|
| VS Code | `.vscode/extensions.json` |
| Cursor | `.vscode/extensions.json` (Cursor reads the same file) |

**How it works:** DevPack maintains a registry of extension IDs keyed by technology ID — the same IDs used in `ProjectContext.technologies`. At write time, it reads the existing file (if any), appends the matched extension IDs, deduplicates, and writes back. Safe to merge programmatically since the format is a simple JSON object with a `"recommendations"` array.

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

**Integration pattern:** Config files dropped at the repo root. Prefer writing a standalone config file over modifying an existing one (e.g., `ruff.toml` instead of merging into `pyproject.toml`). If a config file already exists, skip and report.

### Files added by stack

| File | Stack | Purpose |
|---|---|---|
| `.editorconfig` | All | Tabs vs spaces, line endings, trailing whitespace — respected by nearly every editor without a plugin |
| `ruff.toml` | Python | Linting rules and line length. Written standalone to avoid touching `pyproject.toml` |
| `pyproject.toml` | Python (only if none exists) | Minimal Black + Ruff config |
| `.prettierrc` | JS / TS | Formatting rules |
| `eslint.config.js` | JS / TS | ESLint flat config (ESLint 9+ standard) |
| `tsconfig.json` | TypeScript (only if none exists) | Strict mode baseline |

**How it works:** Stack selection uses `ProjectContext.technologies`. For linter config defaults (line length, target Python/Node version), `ProjectContext.runtime_versions` is used to fill template tokens rather than hardcoding defaults. `tsconfig.json` is only written if no `tsconfig*.json` exists — too many valid project-specific shapes exist to merge safely.

---

## Phase 4 — Documentation Templates

**Goal:** Reduce onboarding friction and standardize contribution workflows with templates GitHub renders natively.

**Integration pattern:** Static files copied only if they don't already exist. Frontend-detected repos get an accessibility checklist added to the PR template.

### Files added

| File | Purpose |
|---|---|
| `CONTRIBUTING.md` | Local setup, branch naming, PR process |
| `.github/pull_request_template.md` | Checklist for PR authors (description, tests, a11y check if frontend) |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Structured bug reports |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Structured feature requests |
| `SECURITY.md` | Responsible disclosure policy |
| `CHANGELOG.md` | Starter changelog following Keep a Changelog format |

**How it works:** Pure copy-if-not-exists. `CONTRIBUTING.md` is templated using `ProjectContext.setup_commands` — the actual detected install, dev, and test commands are inserted directly, making it immediately accurate rather than a placeholder. The PR template conditionally includes an accessibility checklist when any frontend technology is present in `ProjectContext.technologies`.

---

## Phase 5 — Security Baseline

**Goal:** Prevent accidental secret exposure and keep dependencies up to date automatically.

**Integration pattern:** `.gitignore` is merged entry-by-entry (same logic as ignore files in Phase 1). `dependabot.yml` and `.env.example` are copy-if-not-exists.

### Files added

| File | Purpose |
|---|---|
| `.gitignore` (merge) | Append missing entries: `.env`, `*.pem`, `*.key`, `__pycache__`, `.DS_Store`, `node_modules` |
| `.env.example` | Documents required environment variables with placeholder values |
| `.github/dependabot.yml` | Automated dependency update PRs, ecosystem-specific |
| `SECURITY.md` | (if not added in Phase 4) Basic responsible disclosure policy |

**How it works:** `.gitignore` entries are checked individually — present entries are untouched, missing ones are appended under an `# Added by devpack` block. For `dependabot.yml`, the package ecosystem (npm, pip, docker) is read from `ProjectContext.technologies` and used to fill the template. Only ecosystems that are actually detected are included.

---

## Phase 6 — CI/CD Workflows

**Goal:** Enforce quality gates on every push and PR, catching issues that local tooling might miss.

**Integration pattern:** New files written to `.github/workflows/`. Never overwrite an existing workflow file — check for filename collisions and skip with a message if one exists.

### Workflows added

| Workflow | Stack | What it does |
|---|---|---|
| `ci.yml` | All | Lint + test on every PR |
| `secret-scan.yml` | All | Runs `gitleaks` on every push |
| `lighthouse.yml` | Frontend | Accessibility + performance audit via Lighthouse CI |
| `dependency-audit.yml` | Python / JS | `pip audit` or `npm audit` on schedule |

**How it works:** Templates in `starterpack/workflows/` use sentinel tokens that are filled from `ProjectContext` before writing — `{{PYTHON_VERSION}}` and `{{NODE_VERSION}}` from `runtime_versions`, `{{TEST_COMMAND}}` from `setup_commands.test`, `{{DEFAULT_BRANCH}}` from the local git config. Only workflows that don't collide with existing files are written. Post-install output lists what was written and what manual steps remain (e.g., configuring secrets in GitHub Settings).

---

## Phase 7 — Pre-commit Hooks and Code Analysis Scripts

**Goal:** Block bad commits at the source — catching secrets, style violations, and type errors before they enter the history.

**Integration pattern:** The most complex integration. Repos often already have `.pre-commit-config.yaml` or a `husky` setup. If no config exists, copy the stack-specific template; if one exists, offer to add individual missing hooks rather than replacing the file. Post-install instructions are always printed.

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

**How it works:** Stack selection uses `ProjectContext.technologies`. For Python repos, DevPack writes `.pre-commit-config.yaml` from a stack-matched template and prints `pre-commit install`. For Node repos, it generates a `husky` + `lint-staged` config and prints `npm install && npx husky install`. If a config already exists, it diffs the existing hooks against the template and offers to add only the missing ones — never removing anything.

---

## Architectural Implications

### `ProjectContext` replaces `StackDetectionResult` in the `init` path

`StackDetectionResult` continues to exist and is used unchanged by `add-skills`. The `init` command uses `ProjectContext` — a superset that adds `directory_structure`, `setup_commands`, and `runtime_versions`. These two models live in parallel; no migration of existing code is needed.

### New model: `Pack`

The current `Skill` model maps to agent-skill directories. New pack types need a parallel model:

```python
Pack(id, name, description, type, path, tags)
# type ∈ {agent-skill, config-file, workflow, documentation, git-hook}
```

The `init` pipeline presents packs grouped by phase in the interactive selection UI.

### Writer behaviors by pack type

| Pack type | Writer behavior |
|---|---|
| `agent-skill` | `shutil.copytree` (existing behavior) |
| `config-file` | Copy if not exists, or merge (type-aware: JSON dedupe, line-by-line for plaintext) |
| `workflow` | Copy to `.github/workflows/` only if no file with the same name exists |
| `documentation` | Copy if not exists |
| `git-hook` | Write config from template + print setup reminder |

### Template tokens

Files that need variable substitution use sentinel tokens filled from `ProjectContext` at write time: `{{PYTHON_VERSION}}`, `{{NODE_VERSION}}`, `{{TEST_COMMAND}}`, `{{DEV_COMMAND}}`, `{{PROJECT_NAME}}`. Python's `str.replace()` is sufficient — no need for Jinja2 unless templates grow complex.

---

## What to Ignore (Non-Automatable)

The following are valuable practices but not suitable for repo-level automation:

- **Jira standards, sprint ceremonies, project roles** — process, not code
- **Slack setup, communications cadence** — outside the repo
- **Architecture decisions (migration patterns, legacy modernization)** — context-dependent; agent skills are the right format here
- **Figma conventions** — design tooling, not dev tooling
- **Sphinx documentation generation** — requires understanding of module structure; better as an on-demand agent skill than a static config
