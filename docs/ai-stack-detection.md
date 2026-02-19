# AI-Powered Stack Detection

## Description

Replace the static indicator-based tech stack detector with a Claude agent that actively
reads the target repository using SDK tools (Read, Glob, Grep) and returns a structured,
validated list of detected technologies. This gives richer, more accurate detection without
maintaining a hand-crafted registry of file patterns for every possible framework.

## Acceptance Criteria

- `detect_stack()` uses `claude_agent_sdk` to analyze a repo and return detected technologies.
- Claude's output is constrained to a known set of technology IDs (prevents free-form hallucinations).
- The output is a `DetectedTechnology` Pydantic model — the old `Technology` dataclass with indicator callables is removed.
- `matcher.py` is updated to work with the new model; existing skill matching logic is otherwise unchanged.
- The CLI pipeline (`detect_stack → match_skills → prompt → write → readme`) continues to work end-to-end.
- Tests mock the Claude SDK call at the `detect_tech_stack()` boundary; fixture-based integration tests are kept but marked.
- The `logs/agent_responses/` directory is no longer created inside target repos.

---

## Plan

### Codebase Context

| Area | Current state |
|---|---|
| Detector | `detector.py` → iterates `TECHNOLOGIES` list from `registry/technologies.py`; each `Technology` holds `Callable[[Path], bool]` indicators |
| Models | `Technology` dataclass with `indicators`, `is_frontend`; `Skill`, `IDETarget` dataclasses |
| Matcher | `match_skills()` accepts `list[Technology]`; extracts `id`/`name` as term set for string matching |
| CLI | Synchronous; calls `detect_stack(repo_path)` and passes result to `match_skills()` |
| claude_agent.py | Generic SDK adapter (copied from another project); has 3 functions, module-level `LOGS_DIR.mkdir()` side effect |
| Tests | 40 tests passing; `test_detector.py` has 12 tests against static indicators; `test_matcher.py` constructs `Technology` objects directly |

The closest existing analog is `claude_agent.py`'s `query_codebase_json()` — it already
has the SDK call pattern, Pydantic structured output plumbing, and error handling.

---

### Implementation Steps

#### Phase 1: Resolve dependency & fix module-level side effect

**Goal**: Confirm the SDK is installable and remove the directory-creation that pollutes target repos.

1. **Confirm the SDK pip install command.**

   The import in `claude_agent.py` is `from claude_agent_sdk import ...` but the package is
   not currently installed. Check the source project's `pyproject.toml` or run
   `pip show claude_agent_sdk` there to get the exact install name. Then add it to
   `pyproject.toml` alongside `pydantic>=2.0`:

   ```toml
   dependencies = [
       "typer>=0.12",
       "inquirerpy>=0.3",
       "pyyaml>=6.0",
       "pydantic>=2.0",
       "claude-agent-sdk",   # ← replace with confirmed package name
   ]
   ```

   Run `uv sync` to update the lockfile.

2. **Remove the module-level `LOGS_DIR.mkdir()` from `claude_agent.py`.**

   ```python
   # REMOVE these two lines:
   LOGS_DIR = Path("logs/agent_responses")
   LOGS_DIR.mkdir(parents=True, exist_ok=True)
   ```

   Currently this runs at import time and creates `logs/agent_responses/` inside whatever
   directory the user ran `devpack` from — i.e., inside their repo. Fix: either remove
   logging entirely (simplest for MVP) or write logs lazily to `~/.devpack/logs/` only
   when a response is actually received.

---

#### Phase 2: Define output model and known technology IDs

**Goal**: Create the Pydantic schema Claude's structured output must conform to, and the canonical ID list that constrains Claude's vocabulary.

3. **Add `KNOWN_TECHNOLOGY_IDS` to a new `src/devpack/registry/known_ids.py`** (keep the
   registry package; just delete `technologies.py`):

   ```python
   KNOWN_TECHNOLOGY_IDS: list[str] = [
       # Languages
       "python", "javascript", "typescript", "ruby", "go", "rust",
       # Python frameworks
       "django", "fastapi", "flask",
       # JS frameworks
       "react", "vue", "nextjs", "svelte", "angular",
       # Ruby
       "rails",
       # Databases
       "postgres", "mysql", "sqlite", "redis", "mongodb",
       # Infrastructure
       "docker", "kubernetes",
       # Other common
       "celery", "graphql",
   ]
   ```

   This list is independent of any Python code — Claude receives it as text in the prompt.
   It can grow over time without touching detection logic.

4. **Add Pydantic models to `src/devpack/models.py`:**

   ```python
   from pydantic import BaseModel

   class DetectedTechnology(BaseModel):
       id: str          # Must be one of KNOWN_TECHNOLOGY_IDS
       name: str        # Human-readable, e.g. "Next.js", "PostgreSQL"
       is_frontend: bool

   class StackDetectionResult(BaseModel):
       technologies: list[DetectedTechnology]
       summary: str     # Brief prose Claude writes, shown to the user
   ```

5. **Remove the old `Technology` dataclass** (and its `indicators` field) from `models.py`.
   Also delete `src/devpack/registry/technologies.py` — it's no longer needed once the
   indicator approach is gone.

---

#### Phase 3: Refactor `claude_agent.py` into a devpack-specific module

**Goal**: Replace the generic three-function adapter with a focused `detect_tech_stack()` function.

6. **Rewrite `claude_agent.py`** keeping only the structured-output pattern from
   `query_codebase_json()`, specialized for tech stack detection:

   ```python
   async def detect_tech_stack(repo_path: Path) -> StackDetectionResult:
       """Run a Claude agent against repo_path and return a validated StackDetectionResult."""
       ...
   ```

   Remove `query_codebase()` and `query_codebase_markdown()` — they're not needed here.

7. **Write the detection prompt** (constructed inside `detect_tech_stack()`):

   ```
   Analyze the repository and identify the technologies, frameworks, and tools used.

   Use the Read, Glob, and Grep tools to inspect:
   - Package manifests: package.json, requirements.txt, pyproject.toml, Gemfile,
     go.mod, Cargo.toml, composer.json
   - Config files: tsconfig.json, docker-compose.yml, .env*, *.config.js
   - Key source files to confirm actual usage, not just listed dependencies

   Only report technologies clearly present in the project.

   You MUST use ONLY the following technology IDs — do not invent new ones:
   {known_ids_formatted}

   For is_frontend, set true for: javascript, typescript, react, vue, nextjs, svelte, angular.

   In the summary field, write 1-2 sentences describing the project's stack
   (e.g. "A Django REST API backed by PostgreSQL, containerized with Docker.").
   ```

   Pass `allowed_tools=["Read", "Glob", "Grep"]` and `cwd=str(repo_path)` in `ClaudeAgentOptions`
   so Claude can inspect the actual repository.

---

#### Phase 4: Update `detector.py`

**Goal**: Swap out the synchronous indicator loop for an async Claude call, keeping the public interface synchronous so the CLI needs no changes.

8. **Rewrite `detector.py`:**

   ```python
   import asyncio
   from pathlib import Path

   from devpack.claude_agent import detect_tech_stack
   from devpack.models import DetectedTechnology


   def detect_stack(repo_path: Path) -> list[DetectedTechnology]:
       """Detect the tech stack by querying Claude against the repo."""
       result = asyncio.run(detect_tech_stack(repo_path))
       return result.technologies
   ```

   Keeping `detect_stack()` synchronous (wrapping with `asyncio.run()`) means `cli.py`
   and all call sites remain unchanged.

9. **Add a progress message** in `cli.py` before calling `detect_stack()`, since the call
   now takes several seconds:

   ```python
   typer.echo("Analyzing your stack with Claude...")
   stack = detect_stack(repo_path)
   ```

---

#### Phase 5: Update `matcher.py`

**Goal**: Update the type signature to accept `list[DetectedTechnology]`; matching logic is otherwise unchanged since we constrain to known IDs.

10. Update `matcher.py` — the only change is the import and type annotation:

    ```python
    # Before
    from devpack.models import Skill, Technology
    def match_skills(skills: list[Skill], stack: list[Technology]) -> list[Skill]:

    # After
    from devpack.models import DetectedTechnology, Skill
    def match_skills(skills: list[Skill], stack: list[DetectedTechnology]) -> list[Skill]:
    ```

    The `tech_terms` extraction and `is_frontend` check work identically because
    `DetectedTechnology` has the same `id`, `name`, and `is_frontend` fields.

---

#### Phase 6: Update tests

**Goal**: Replace indicator-based detector tests with mocked SDK tests; update matcher test fixtures.

11. **`tests/test_detector.py`** — rewrite using `unittest.mock.patch`:

    ```python
    from unittest.mock import AsyncMock, patch
    from devpack.models import DetectedTechnology, StackDetectionResult

    @patch("devpack.claude_agent.detect_tech_stack")
    def test_detect_stack_returns_technologies(mock_detect, tmp_path):
        mock_detect.return_value = StackDetectionResult(
            technologies=[DetectedTechnology(id="python", name="Python", is_frontend=False)],
            summary="A Python project.",
        )
        # asyncio.run wraps the coroutine; mock must be a coroutine
        ...
    ```

    Keep the fixture directories (`tests/fixtures/django_repo`, etc.) and mark
    fixture-based tests as `@pytest.mark.integration` so they can be skipped
    in CI without an API key (`pytest -m "not integration"`).

12. **`tests/test_matcher.py`** — replace `Technology(...)` fixtures with `DetectedTechnology(...)`:

    ```python
    # Before
    from devpack.models import Technology
    stack = [Technology(id="django", name="Django")]

    # After
    from devpack.models import DetectedTechnology
    stack = [DetectedTechnology(id="django", name="Django", is_frontend=False)]
    ```

---

### Risks & Considerations

| Risk | Mitigation |
|---|---|
| **SDK package name unknown** | Must confirm exact pip install name before Phase 1 can complete. All other phases can be coded in parallel. |
| **Latency** | Each `devpack add-skills` now makes an LLM call (5–15 s). The "Analyzing your stack..." progress message (Phase 4, step 9) is the minimum mitigation. Could add a spinner later. |
| **API key requirement** | Claude SDK requires `ANTHROPIC_API_KEY`. If absent, `detect_stack()` should raise a clear error with a helpful message rather than a raw SDK exception. Add a guard in `detect_tech_stack()`. |
| **`asyncio.run()` in tests** | Mocking `detect_tech_stack` at the async boundary avoids event loop issues in tests. Do not call `asyncio.run()` from tests directly. |
| **Module-level `LOGS_DIR.mkdir()`** | Fixed in Phase 1; must be resolved before the module can be imported without side effects. |
| **ID drift** | If `KNOWN_TECHNOLOGY_IDS` grows, old skills may start matching new techs unexpectedly. This is acceptable for now; a formal skill tagging system is a future improvement. |
