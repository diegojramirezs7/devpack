# DevPack — `add-skills` MVP

## Description

`devpack add-skills` is a CLI command that examines an existing repo, detects its tech stack from config files, filters a bundled catalog of curated skills to those that are relevant, lets the user confirm selections via an interactive checklist, asks which IDE/agent to target, then copies the selected skill directories into the correct location in the repo and updates the README with usage instructions.

## Acceptance Criteria

1. Running `devpack add-skills <repo_path>` (defaulting to `.`) starts the flow.
2. The tool reads config files (`package.json`, `pyproject.toml`, `requirements.txt`, `Gemfile`, `go.mod`, `Cargo.toml`, `docker-compose.yml`) and identifies the detected technologies.
3. The detected stack is matched against the bundled skills in `starterpack/agent-skills/` using skill name and description — no explicit tags.
4. A checkbox list of applicable skills is presented via InquirerPy, all pre-selected.
5. The user is prompted to choose a target IDE (Cursor, VS Code Copilot, Claude Code); if one is already detected in the repo, it defaults to that.
6. Selected skill directories are copied as-is into the correct IDE-specific path (`.claude/skills/`, `.cursor/skills/`, `.agents/skills/`).
7. The repo's README gets an appended/updated "Skills" section describing what was added.
8. A summary is printed to stdout listing what was added and where.

---

## Plan

### Codebase Context

The repo is at Python 3.13.1 (`.python-version`). No source code exists yet — only `docs/`, `readme.md`, `starterpack/agent-skills/` (8 skills), and `.claude/skills/` (dev tools for this repo). There are no existing patterns to follow, so the plan establishes them from scratch using the system design document (`docs/system-design.md`) as the authoritative spec.

**Tech stack to set up:** Python 3.13, Typer (CLI), InquirerPy (prompts), PyYAML (SKILL.md frontmatter), `tomllib` (stdlib, Python 3.11+ — no extra dep needed for pyproject.toml parsing). Standard `pytest` for tests.

**Key structural decisions per the system design:**
- `src/devpack/` layout (src layout for clean packaging)
- One module per pipeline step: `detector` → `matcher` → `prompter` → `writer` → `readme_updater`, orchestrated by `cli`
- Skills discovered at runtime by scanning `starterpack/agent-skills/` — no Python skill registry
- Technologies defined as Python dataclasses in `registry/technologies.py`
- Skills bundled with the package via `pyproject.toml` `[tool.setuptools.package-data]`

---

### Implementation Steps

#### Phase 1: Project Scaffolding

Establish the package structure, dependencies, and entry point so the `devpack` command is installable.

1. Create `pyproject.toml` at the repo root. Use `[build-system]` with `setuptools`, declare the `devpack` package under `[project]` with dependencies: `typer>=0.12`, `inquirerpy>=0.3`, `pyyaml>=6.0`. Add a `[project.scripts]` entry: `devpack = "devpack.cli:app"`. Include `[tool.setuptools.package-data]` to bundle `starterpack/agent-skills/**/*` with the installed package.

2. Create the package skeleton:
   - `src/devpack/__init__.py` (empty)
   - `src/devpack/registry/__init__.py` (empty)
   - `tests/__init__.py` (empty)
   - `tests/fixtures/` directory with subdirs `django_repo/`, `react_repo/`, `node_repo/`, `empty_repo/` — each containing the minimal config files needed to trigger detection (e.g. `django_repo/requirements.txt` containing `django`, `react_repo/package.json` with `"react"` in dependencies).

3. Install the package in editable mode (`pip install -e ".[dev]"`) — note this for the developer, not a code step.

---

#### Phase 2: Data Models

Define the internal types used across all modules.

4. Create `src/devpack/models.py` with three dataclasses:
   - `Technology(id: str, name: str, indicators: list[Callable[[Path], bool]])` — `indicators` are callables that receive the repo path and return `True` if the technology is detected.
   - `Skill(id: str, name: str, description: str, path: Path)` — populated at runtime from scanning `starterpack/agent-skills/`.
   - `IDETarget(id: str, name: str, skill_path: str)` — three instances defined as constants: `CLAUDE_CODE`, `CURSOR`, `VSCODE`.

   Define the three `IDETarget` constants in `models.py`:
   ```python
   CLAUDE_CODE = IDETarget("claude-code", "Claude Code", ".claude/skills")
   CURSOR      = IDETarget("cursor", "Cursor", ".cursor/skills")
   VSCODE      = IDETarget("vscode", "VS Code Copilot", ".agents/skills")
   IDE_TARGETS = [CLAUDE_CODE, CURSOR, VSCODE]
   ```

---

#### Phase 3: Technology Registry

Define which technologies exist and how to detect them.

5. Create `src/devpack/registry/technologies.py`. Define a `TECHNOLOGIES: list[Technology]` list covering at minimum: `python`, `django`, `fastapi`, `flask`, `react`, `vue`, `nextjs`, `typescript`, `javascript`, `ruby`, `rails`, `go`, `rust`, `postgres`, `docker`.

   Each `Technology` gets one or more indicator callables. Examples:
   - `django`: checks `requirements.txt` or `pyproject.toml` for the string `django` (case-insensitive).
   - `react`: checks `package.json` `dependencies` or `devDependencies` for key `"react"`.
   - `nextjs`: checks `package.json` for key `"next"`.
   - `typescript`: checks for `tsconfig.json` existence or `typescript` in `package.json`.
   - `docker`: checks for `Dockerfile` or `docker-compose.yml` existence.

   Use simple file reads — no deep parsing. For `package.json`, use `json.loads`. For `pyproject.toml`, use `tomllib` (stdlib). For text files like `requirements.txt`, use a plain string `in` check.

---

#### Phase 4: Stack Detector

6. Create `src/devpack/detector.py` with a single public function:
   ```python
   def detect_stack(repo_path: Path) -> list[Technology]: ...
   ```
   Iterates over all `TECHNOLOGIES` from `registry/technologies.py`, runs each technology's indicators against `repo_path`, and returns the list of matched `Technology` objects. Pure detection logic — no I/O side effects, no printing.

7. Write `tests/test_detector.py`. Use the fixture directories from Step 2. Assert that `detect_stack(fixtures/django_repo)` returns a list containing `django` and `python`. Assert that `detect_stack(fixtures/react_repo)` contains `react`. Assert that `detect_stack(fixtures/empty_repo)` returns `[]`. Use `pytest` with `tmp_path` where fixture files are created inline for portability.

---

#### Phase 5: Skill Catalog & Matcher

Load skills from the filesystem and filter by detected stack.

8. Create `src/devpack/matcher.py` with two functions:

   **`load_skills(starterpack_path: Path) -> list[Skill]`** — Scans `starterpack_path/agent-skills/` for subdirectories, reads each `SKILL.md`, parses the YAML frontmatter block (everything between the first `---` and second `---`), extracts `name` and `description`, and returns a list of `Skill` objects. Use `pyyaml` for frontmatter parsing. The `Skill.id` is the directory name; `Skill.path` is the full directory path. Skip any skill with missing or malformed frontmatter with a warning rather than crashing.

   **`match_skills(skills: list[Skill], stack: list[Technology]) -> list[Skill]`** — For each skill, check if it is relevant to the detected stack. Matching strategy (simple string matching, no LLM):
   - A skill is **always included** if its `id` is in a `GENERAL_SKILL_IDS` set (e.g. `{"feature-implementation-plan"}`).
   - A skill is included if any detected technology's `id` or `name` appears (case-insensitive) in the skill's `id` or `description`.
   - A skill is included if any detected technology is a frontend framework and the skill description contains `"web"`, `"performance"`, `"accessibility"`, or `"frontend"`.
   - If no stack is detected (empty repo), return all skills.

9. Write `tests/test_matcher.py`. Test that `match_skills` with a Django stack returns `django-best-practices` and `django-docs` but not `react-best-practices`. Test that `feature-implementation-plan` is always included. Test that `optimize-lighthouse-metrics` is included for a React stack but not a pure Django stack.

---

#### Phase 6: Interactive Prompter

10. Create `src/devpack/prompter.py` with two functions:

    **`prompt_skill_selection(skills: list[Skill]) -> list[Skill]`** — Uses InquirerPy's `checkbox` prompt. Each choice displays `skill.name` and `skill.description`. All skills are pre-checked. Returns the user-selected subset.

    **`prompt_ide_selection(repo_path: Path) -> IDETarget`** — Detects which IDE is already configured in `repo_path` by checking for `.claude/`, `.cursor/`, `.agents/` directories. If exactly one is found, default to it in the prompt. Uses InquirerPy's `select` prompt showing all three `IDE_TARGETS`. Returns the chosen `IDETarget`.

---

#### Phase 7: Skill Writer & README Updater

11. Create `src/devpack/writer.py` with one public function:
    ```python
    def write_skills(skills: list[Skill], repo_path: Path, ide: IDETarget) -> list[Path]: ...
    ```
    For each skill, compute the destination: `repo_path / ide.skill_path / skill.id`. Use `shutil.copytree(skill.path, dest, dirs_exist_ok=True)` to copy the skill directory (preserving subdirectories like `rules/`, `references/`). Returns a list of written destination paths.

12. Create `src/devpack/readme_updater.py` with one public function:
    ```python
    def update_readme(repo_path: Path, skills: list[Skill], ide: IDETarget) -> None: ...
    ```
    Glob for `README.md` or `readme.md` (case-insensitive). If not found, create `README.md`. Read existing content. If a `## Skills` section already exists, replace it. Otherwise, append it. The section lists each skill with its name and description, plus a one-liner on how to invoke it in the chosen IDE (e.g. for Claude Code: `"Type /skill-name in your Claude Code session"`).

13. Write `tests/test_writer.py`. Use `tmp_path` to create a fake repo. Call `write_skills` with a real skill directory from `starterpack/agent-skills/` and assert the destination exists and contains `SKILL.md`. Test `update_readme` appends the section to an empty README. Test a second run replaces rather than duplicates the section (idempotent).

---

#### Phase 8: CLI Orchestration

Wire up all modules into the `devpack add-skills` command.

14. Create `src/devpack/cli.py`:
    ```python
    import typer
    from pathlib import Path

    app = typer.Typer()

    @app.command("add-skills")
    def add_skills(repo_path: Path = typer.Argument(Path("."))):
        ...
    ```
    The command body is a linear pipeline:
    1. Resolve `repo_path` to an absolute path. Validate it exists and is a directory (`typer.BadParameter` if not).
    2. Call `detect_stack(repo_path)` → print detected technologies.
    3. Resolve `starterpack_path` using `Path(__file__).parent.parent.parent / "starterpack"` (or `importlib.resources` for installed packages). Call `load_skills` then `match_skills`.
    4. If no skills matched, print a message and exit cleanly.
    5. Call `prompt_skill_selection(matched_skills)` → user confirms.
    6. Call `prompt_ide_selection(repo_path)` → user picks IDE.
    7. Call `write_skills(selected, repo_path, ide)`.
    8. Call `update_readme(repo_path, selected, ide)`.
    9. Print summary: `"Added N skills to <ide.skill_path>/"` and list each skill name.

---

### Risks & Considerations

- **`starterpack` path resolution at runtime** — When installed as a package, `Path(__file__)` relative paths may not point to `starterpack/`. The cleanest fix is to include `starterpack/` as package data in `pyproject.toml` and use `importlib.resources` (`files()` API, Python 3.9+). Alternatively, move `starterpack/` inside `src/devpack/` so it's always co-located with the package. This is the most important structural decision to resolve in Phase 1.

- **SKILL.md frontmatter parsing** — Skills must have valid YAML frontmatter with `name` and `description` keys. `load_skills` must skip malformed entries with a warning rather than crashing, to guard against future skill additions with typos.

- **Inferred matching false positives/negatives** — The string-matching strategy is intentionally simple. If a skill isn't matching when expected, the most likely cause is a mismatch between technology `id` values in `technologies.py` and the naming patterns in skill directory names. Keep them consistent.

- **`shutil.copytree` with `dirs_exist_ok=True`** — Requires Python 3.8+. Fine on 3.13, but worth noting for future compatibility.

- **README idempotency** — Running `add-skills` twice must not duplicate the skills section. The `readme_updater` must reliably detect and replace the existing section using a stable marker comment or section heading.

- **No existing tests or CI** — `pytest` conventions are established from scratch. Use `tmp_path` fixtures for all filesystem operations to keep tests hermetic and fast.
