import os
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

# Skip the SDK's `claude -v` subprocess version check. When called from devpack
# (a library context), the check spawns a short-lived subprocess and then waits
# for it to exit via asyncio. If any interactive prompt (e.g. InquirerPy) ran
# before this point, the asyncio event-loop's subprocess-monitoring state may be
# disrupted, causing that wait to hang indefinitely before any API call is made.
os.environ.setdefault("CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK", "1")

# When devpack is invoked from inside a Claude Code session (e.g. from the
# integrated terminal), CLAUDECODE is set in the environment. The claude CLI
# treats that as a nested-session signal and refuses to start. Unset it so
# the subprocess spawned by claude_agent_sdk starts cleanly.
os.environ.pop("CLAUDECODE", None)

from devpack.config import load_api_key
from devpack.models import StackDetectionResult, ProjectContext
from devpack.registry.known_ids import KNOWN_TECHNOLOGY_IDS


def _build_detection_prompt() -> str:
    known_ids_formatted = ", ".join(KNOWN_TECHNOLOGY_IDS)
    return f"""
    Analyze the repository and identify the technologies, frameworks, and tools used.

    Use the Read, Glob, and Grep tools to inspect:
    - Package manifests: package.json, requirements.txt, pyproject.toml, Gemfile, go.mod, Cargo.toml, composer.json
    - Config files: tsconfig.json, docker-compose.yml, .env*, *.config.js
    - Key source files to confirm actual usage, not just listed dependencies

    Only report technologies clearly present in the project.

    You MUST use ONLY the following technology IDs — do not invent new ones:
    {known_ids_formatted}

    For is_frontend, set true for: javascript, typescript, react, vue, nextjs, vite, angular.

    In the summary field, write 1-2 sentences describing the project's stack \
    (e.g. "A Django REST API backed by PostgreSQL, containerized with Docker.").
    """


def _build_json_schema() -> dict:
    # extra="forbid" on the models ensures additionalProperties: false is emitted automatically.
    return StackDetectionResult.model_json_schema()


async def detect_tech_stack(repo_path: Path) -> StackDetectionResult:
    """Run a Claude agent against repo_path and return a validated StackDetectionResult."""
    if not load_api_key():
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set.\n\n"
            "Run `devpack configure` to set it up, or export it manually:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        cwd=str(repo_path),
        max_buffer_size=10
        * 1024
        * 1024,  # 10MB — default 1MB is too small for large repos
        output_format={
            "type": "json_schema",
            "schema": _build_json_schema(),
        },
    )

    structured_output = None
    result_subtype = None

    # We only care about the final ResultMessage; intermediate messages are streaming progress.
    async for message in query(prompt=_build_detection_prompt(), options=options):
        if isinstance(message, ResultMessage):
            structured_output = message.structured_output
            result_subtype = message.subtype

    if result_subtype == "error_max_structured_output_retries":
        raise ValueError(
            "Claude could not produce a valid stack detection response after multiple attempts. "
            "Check that the repository is accessible and try again."
        )

    if structured_output is None:
        raise ValueError(
            f"Claude did not return structured output (subtype: {result_subtype}). "
            "Ensure the repository path is correct and the API key is valid."
        )

    return StackDetectionResult.model_validate(structured_output)


def _build_context_prompt() -> str:
    known_ids_formatted = ", ".join(KNOWN_TECHNOLOGY_IDS)
    return f"""
    Analyze the repository and produce a structured project context.

    Use Read, Glob, and Grep to inspect:
    - Package manifests: package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod
    - Config files: tsconfig.json, docker-compose.yml, Makefile, .python-version, .nvmrc
    - Top-level directory layout

    Return all fields:

    technologies: Only IDs from this list — {known_ids_formatted}
    Set is_frontend: true for javascript, typescript, react, vue, nextjs, vite, angular.

    summary: 1-2 sentences describing the project stack.

    directory_structure: Annotated top-level tree. Example:
      src/          # application source
      tests/        # test suite
      Dockerfile    # container config
    Keep it concise, annotate only what matters.

    setup_commands: Infer from package.json scripts, Makefile, README, or common conventions.
    Set fields to null if not determinable.

    runtime_versions: Dict of runtime → version (e.g. {{"python": "3.11", "node": "20"}}).
    Infer from .python-version, .nvmrc, pyproject.toml requires-python, package.json engines.
    Use empty dict {{}} if not determinable.
    """


def _build_context_schema() -> dict:
    return ProjectContext.model_json_schema()


async def detect_project_context(repo_path: Path) -> ProjectContext:
    """Run a Claude agent against repo_path and return a validated ProjectContext."""
    if not load_api_key():
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set.\n\n"
            "Run `devpack configure` to set it up, or export it manually:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        cwd=str(repo_path),
        max_buffer_size=10
        * 1024
        * 1024,  # 10MB — default 1MB is too small for large repos
        output_format={
            "type": "json_schema",
            "schema": _build_context_schema(),
        },
    )

    structured_output = None
    result_subtype = None

    async for message in query(prompt=_build_context_prompt(), options=options):
        if isinstance(message, ResultMessage):
            structured_output = message.structured_output
            result_subtype = message.subtype

    if result_subtype == "error_max_structured_output_retries":
        raise ValueError(
            "Claude could not produce a valid project context after multiple attempts."
        )
    if structured_output is None:
        raise ValueError(
            f"Claude did not return structured output (subtype: {result_subtype})."
        )

    return ProjectContext.model_validate(structured_output)
