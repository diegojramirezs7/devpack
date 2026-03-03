import atexit
import json
import os
import shutil
import sys
import tempfile
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


_SYSTEM_CLAUDE_PATH: str | None = None
_EMPTY_MCP_CONFIG_PATH: str | None = None


def _get_system_claude() -> str | None:
    """Return the path to the system-installed claude binary, bypassing any
    bundled binary that SDK 0.1.44+ ships alongside the package.

    SDK 0.1.44 introduced _find_bundled_cli() which prefers a bundled claude
    binary over the system one. The bundled version (2.1.59) has different
    MCP-server lifecycle behaviour than the user's installed version, causing
    the subprocess to hang indefinitely on devpack init. Explicitly passing
    cli_path forces the SDK to skip its bundled-binary lookup.
    """
    global _SYSTEM_CLAUDE_PATH
    if _SYSTEM_CLAUDE_PATH is None:
        _SYSTEM_CLAUDE_PATH = shutil.which("claude") or ""
    return _SYSTEM_CLAUDE_PATH or None


def _get_empty_mcp_config() -> str:
    """Return path to a temp file containing an empty MCP server config.

    The claude CLI expects --mcp-config to be a file path, not inline JSON.
    Created once per process; cleaned up on exit.
    """
    global _EMPTY_MCP_CONFIG_PATH
    if _EMPTY_MCP_CONFIG_PATH is None:
        fd, path = tempfile.mkstemp(suffix=".json", prefix="devpack-mcp-")
        with os.fdopen(fd, "w") as f:
            json.dump({"mcpServers": {}}, f)
        atexit.register(lambda p=path: os.path.exists(p) and os.unlink(p))
        _EMPTY_MCP_CONFIG_PATH = path
    return _EMPTY_MCP_CONFIG_PATH


def _make_stderr_logger():
    """Return a stderr callback that prints agent subprocess output.

    Enabled only when ANTHROPIC_LOG is set (i.e. --debug mode).
    Lets you see exactly which files the agent reads, helping diagnose
    buffer overflows caused by unexpectedly large file reads.
    """

    def _log(line: str) -> None:
        print(f"[agent] {line}", file=sys.stderr, flush=True)

    return _log


def _build_detection_prompt() -> str:
    known_ids = ", ".join(KNOWN_TECHNOLOGY_IDS)
    return f"""Identify the technology stack of this repository. Only Python and JavaScript/TypeScript stacks are supported.

## Tool budget
Use at most 6 Read or Glob calls. Work through the file list below in order and stop as soon as you can populate all fields.

## Files to check (in priority order)
Read ONLY these files, nothing else. Do not read lock files, source files, or any file not in this list.
1. package.json
2. pyproject.toml
3. requirements.txt
4. tsconfig.json
5. docker-compose.yml
6. Makefile

## Output rules
- Report only technologies with clear evidence in the files above.
- Use ONLY these technology IDs — no others are valid: {known_ids}
- Set is_frontend: true for: javascript, typescript, react, vue, nextjs, vite, angular
- Set is_frontend: false for all others.
- summary: 1-2 sentences describing the stack (e.g. "A Django REST API backed by PostgreSQL and Redis.")."""


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
        allowed_tools=["Read", "Glob"],
        cwd=str(repo_path),
        max_turns=3,
        max_buffer_size=20 * 1024 * 1024,
        cli_path=_get_system_claude(),
        extra_args={"mcp-config": _get_empty_mcp_config()},
        # When --debug is active, print every line the subprocess writes to
        # stderr so you can see exactly which files the agent is reading.
        stderr=_make_stderr_logger() if os.environ.get("ANTHROPIC_LOG") else None,
        output_format={
            "type": "json_schema",
            "schema": _build_json_schema(),
        },
    )

    structured_output = None
    result_subtype = None

    # SDK 0.1.44+ raises an exception after a successful result when account-level MCP
    # servers (e.g. Google Calendar) fail to disconnect cleanly (exit code 1). Re-raise
    # only if we received nothing at all — if structured_output is set, the query succeeded.
    try:
        async for message in query(prompt=_build_detection_prompt(), options=options):
            if isinstance(message, ResultMessage):
                structured_output = message.structured_output
                result_subtype = message.subtype
    except Exception:
        if structured_output is None:
            raise

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
    known_ids = ", ".join(KNOWN_TECHNOLOGY_IDS)
    return f"""Produce a structured project context for this repository. Only Python and JavaScript/TypeScript stacks are supported.

## Tool budget
Use at most 7 Read or Glob calls. Work through the steps below in order.

## Step 1 — List top-level directory (1 Glob call)
Call Glob("*") once. Use the result for the directory_structure field.

## Step 2 — Read manifest files (in priority order, skip if absent)
Read ONLY these files, nothing else. Do not read lock files, source files, or any file not in this list.
1. package.json
2. pyproject.toml
3. requirements.txt
4. tsconfig.json
5. docker-compose.yml
6. Makefile (first 30 lines — for setup commands)

## Output field instructions

**technologies**
Use ONLY these IDs: {known_ids}
Set is_frontend: true for: javascript, typescript, react, vue, nextjs, vite, angular

**summary**
1-2 sentences describing the stack.
Example: "A Next.js frontend with a FastAPI backend, using PostgreSQL and Docker."

**directory_structure**
Annotated tree of top-level entries from your Glob("*") result.
Include only entries that reveal project structure. Annotate each with a brief comment.
Example:
  src/        # application source
  tests/      # test suite
  Dockerfile  # container config

**setup_commands**
Infer from the package.json "scripts" section or Makefile targets only.
Set each field to null if not determinable.
- install: how to install dependencies
- dev: how to start a development server or watcher
- test: how to run tests
- build: how to produce a production build"""


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
        allowed_tools=["Read", "Glob"],
        cwd=str(repo_path),
        max_turns=10,
        max_buffer_size=25 * 1024 * 1024,
        cli_path=_get_system_claude(),
        extra_args={"mcp-config": _get_empty_mcp_config()},
        stderr=_make_stderr_logger() if os.environ.get("ANTHROPIC_LOG") else None,
        output_format={
            "type": "json_schema",
            "schema": _build_context_schema(),
        },
    )

    structured_output = None
    result_subtype = None

    try:
        async for message in query(prompt=_build_context_prompt(), options=options):
            if isinstance(message, ResultMessage):
                structured_output = message.structured_output
                result_subtype = message.subtype
    except Exception:
        if structured_output is None:
            raise

    if result_subtype == "error_max_structured_output_retries":
        raise ValueError(
            "Claude could not produce a valid project context after multiple attempts."
        )
    if structured_output is None:
        raise ValueError(
            f"Claude did not return structured output (subtype: {result_subtype})."
        )

    return ProjectContext.model_validate(structured_output)
