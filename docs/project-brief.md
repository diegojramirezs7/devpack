# mytool — AI-Optimized Project Scaffolding CLI

## What is this?
A command-line tool that helps solo developers and teams scaffold new projects (or augment existing ones) with proper structure, boilerplate code, and AI-optimized development files. It combines interactive project setup — similar to `npx create-vite` — with a config pack system that lets individuals and organizations distribute their conventions, best practices, and agent rules directly into repos where developers actually work.

## The Problem
Starting a new project involves dozens of small decisions (ORM, linter, folder structure, pre-commit hooks, etc.) and a lot of tedious wiring. Best practices and organizational standards live in wiki pages that nobody reads at the right moment. And AI-assisted development tools like Cursor, Claude Code, and Copilot work best when they have project context — but developers are manually creating rules files and context docs every time. This tool solves all three problems at once.

## Two Purposes
The tool serves a dual role. First, it's a **project scaffolder** — it generates directory structure, boilerplate code, dependency files, and configuration based on your stack choices. Second, it's a **knowledge distribution mechanism** — it takes organizational or personal conventions (git standards, code review practices, ticket formats, framework guidelines) and embeds them directly into the repo as agent skills, rules files, and reference docs so they're always in context where developers work.

## How it Works

### Config Packs
A config pack is a Git repo or local folder containing markdown files organized into subdirectories by concern. Subdirectories are things like `git-standards/`, `pre-commits/`, `agent-skills/`, `framework-react/`, `design-practices/`, etc. Every subdirectory is optional — you include only what's relevant. The authoring experience is just "write markdown, put it in the right folder."

To bridge the gap between human-friendly markdown and reliable tool execution, there's a compile step. The pack maintainer runs `mytool pack build`, which uses AI to interpret the markdown files and generate a structured `pack.json` manifest. This manifest gets committed alongside the markdown so it's versioned and reviewable. Other developers pulling the pack get the pre-compiled manifest and the tool can use it immediately.

### Pack Registry
The CLI stores registered packs in a global config at `~/.mytool/`. You register a pack once with `mytool pack add <name> <git-url-or-local-path>`. The tool clones remote repos to `~/.mytool/packs/<name>/` and pulls the latest version before each use. A developer might have an `org` pack from their company and a `personal` pack for side projects.

### Scaffolding Flow
1. Run `mytool init my-project` (creates the directory for you).
2. Tool asks which config pack to use.
3. Tool walks through interactive setup: frontend, backend, or full-stack? Which framework? Then framework-specific decisions (ORM, router, state management, etc.). Then cross-cutting concerns (linter, formatter, pre-commit hooks). Config packs can provide defaults at each step so you're confirming rather than choosing from scratch.
4. Tool generates everything: folder structure, boilerplate code, dependency files, pre-commit hooks, and all AI-development files (agent rules, skills, convention docs) pulled from the selected config pack.
5. A small `.mytool.yaml` is added to the project recording which pack and version was used.

### Augmenting Existing Projects
The tool can also layer onto existing repos without touching existing code. Running something like `mytool add agent-skills` or `mytool add pre-commits` brings in specific pieces from your config pack on top of what's already there.

## MVP Features
- `mytool pack add` — register a config pack from a Git URL or local path
- `mytool pack build` — AI-powered compile step that generates pack.json from markdown files
- `mytool init` — interactive scaffolding for new projects with framework and tooling choices
- Config pack spec — documented directory structure and format for authoring packs
- Generated AI-development files — agent rules, skills, and convention docs based on pack contents

## Future Iterations
- `mytool update` — check for newer pack versions and apply diffs to existing projects
- `mytool add` — selectively layer specific concerns onto existing repos
- Composable packs — combine multiple packs in a single scaffolding run (e.g., org + personal)
- Community pack registry — discover and share config packs publicly
- Framework-specific code templates — richer boilerplate beyond basic structure (auth patterns, API scaffolds, etc.)