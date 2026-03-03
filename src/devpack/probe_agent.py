"""Minimal Claude SDK diagnostic — used by `devpack probe`."""

import asyncio
import atexit
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

# Must be set before importing the SDK so it doesn't spawn its own version-check subprocess.
os.environ.setdefault("CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK", "1")
# Must be unset before any SDK call so the subprocess doesn't see CLAUDECODE=1 and refuse to start.
os.environ.pop("CLAUDECODE", None)

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from devpack.config import api_key_source, load_api_key

# Force the SDK to use the system-installed claude binary instead of any
# bundled binary that SDK 0.1.44+ ships. The bundled version (2.1.59) has
# different MCP-server lifecycle behaviour and is the root cause of failures
# observed when devpack is run as a uv-tools install.
_SYSTEM_CLAUDE = shutil.which("claude")


def _log(prefix: str, msg: str) -> None:
    print(f"[{prefix}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Step 0 — Environment snapshot
# ---------------------------------------------------------------------------

def run_step0() -> bool:
    """Print environment information. Returns False if a hard blocker is found."""
    _log("env", "=" * 50)
    _log("env", "Step 0: Environment snapshot")
    _log("env", "=" * 50)

    ok = True

    # Python
    _log("env", f"Python:          {sys.version}")
    _log("env", f"Platform:        {platform.platform()}")

    # claude binary
    claude_path = shutil.which("claude")
    if claude_path:
        _log("env", f"claude binary:   {claude_path}  (system — used by devpack)")
    else:
        _log("env", "claude binary:   NOT FOUND — install Claude Code first")
        return False

    if _SYSTEM_CLAUDE:
        _log("env", f"cli_path override: {_SYSTEM_CLAUDE}  (bypasses SDK bundled binary)")

    # claude --version
    result = subprocess.run(
        ["claude", "--version"],
        capture_output=True,
        text=True,
    )
    version_out = result.stdout.strip() or result.stderr.strip()
    _log("env", f"claude version:  {version_out!r}  (exit code: {result.returncode})")
    if result.returncode != 0:
        _log("env", f"claude stderr:   {result.stderr.strip()!r}")
        _log("env", "WARN: 'claude --version' returned non-zero — the binary may be broken")
        ok = False

    # SDK version
    try:
        sdk_version = importlib.metadata.version("claude-agent-sdk")
    except importlib.metadata.PackageNotFoundError:
        sdk_version = "not found"
    _log("env", f"claude-agent-sdk: {sdk_version}")

    # API key
    source = api_key_source()
    if source:
        _log("env", f"ANTHROPIC_API_KEY: set (source: {source})")
    else:
        _log("env", "ANTHROPIC_API_KEY: NOT SET — run `devpack configure`")
        ok = False

    # Relevant env vars (CLAUDECODE is removed and SKIP_VERSION_CHECK is set at module level)
    for var in ("CLAUDECODE", "CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK", "ANTHROPIC_LOG"):
        val = os.environ.get(var)
        val_display = repr(val) if val is not None else "not set"
        _log("env", f"{var}: {val_display}")

    _log("env", "")
    if ok:
        _log("env", "Step 0: PASS")
    else:
        _log("env", "Step 0: FAIL — fix the issues above before proceeding")
    return ok


# ---------------------------------------------------------------------------
# Step 1 — Minimal SDK call (no tools, no structured output)
# ---------------------------------------------------------------------------

async def _run_step1_async() -> tuple[bool, list[str]]:
    """Make the smallest possible SDK call. Returns (passed, stderr_lines)."""
    stderr_lines: list[str] = []

    def _capture_stderr(line: str) -> None:
        stderr_lines.append(line)
        print(f"[step1][stderr] {line}", flush=True)

    # Load API key into the process env so the subprocess inherits it
    load_api_key()

    options = ClaudeAgentOptions(
        allowed_tools=[],
        max_turns=1,
        max_buffer_size=1 * 1024 * 1024,  # 1 MB — nothing returned should approach this
        cli_path=_SYSTEM_CLAUDE,
        stderr=_capture_stderr,
        # Deliberately omitting: extra_args, output_format, cwd
        # This is the bare minimum to test whether the SDK works at all
    )

    prompt = "Reply with exactly the word: OK"
    _log("step1", f"Prompt:  {prompt!r}")
    _log("step1", "Options: allowed_tools=[], max_turns=1, max_buffer_size=1MB")
    _log("step1", "         no extra_args, no output_format, no cwd")
    _log("step1", "Sending...")

    message_count = 0
    try:
        async for message in query(prompt=prompt, options=options):
            message_count += 1
            msg_type = getattr(message, "type", type(message).__name__)
            msg_subtype = getattr(message, "subtype", "—")
            # Estimate size from repr
            raw_size = len(repr(message))
            _log("step1", f"Message {message_count}: type={msg_type!r}  subtype={msg_subtype!r}  ~{raw_size} bytes")
            if isinstance(message, ResultMessage):
                _log("step1", f"  content preview: {str(getattr(message, 'content', ''))[:120]!r}")
    except Exception as exc:
        _log("step1", f"EXCEPTION: {type(exc).__name__}: {exc}")
        if stderr_lines:
            _log("step1", f"Subprocess stderr ({len(stderr_lines)} lines):")
            for line in stderr_lines:
                _log("step1", f"  stderr> {line}")
        return False, stderr_lines

    _log("step1", f"Received {message_count} message(s) total")
    return True, stderr_lines


def run_step1() -> bool:
    """Run the minimal SDK call. Returns True on success."""
    _log("step1", "=" * 50)
    _log("step1", "Step 1: Minimal SDK call (no tools, no schema, 1 MB limit)")
    _log("step1", "=" * 50)

    passed, stderr_lines = asyncio.run(_run_step1_async())

    _log("step1", "")
    if passed:
        _log("step1", "Step 1: PASS")
    else:
        _log("step1", "Step 1: FAIL")
        if not stderr_lines:
            _log("step1", "No stderr captured — the subprocess may have failed silently")
    return passed


# ---------------------------------------------------------------------------
# Step 2 — Same call but with --mcp-config override (empty server list)
# ---------------------------------------------------------------------------

_PROBE_MCP_CONFIG_PATH: str | None = None


def _get_probe_mcp_config() -> str:
    """Write an empty MCP config to a temp file and return its path.

    The claude CLI expects --mcp-config to be a file path, not inline JSON.
    Created once per process; deleted on exit.
    """
    global _PROBE_MCP_CONFIG_PATH
    if _PROBE_MCP_CONFIG_PATH is None:
        fd, path = tempfile.mkstemp(suffix=".json", prefix="devpack-probe-mcp-")
        with os.fdopen(fd, "w") as f:
            json.dump({"mcpServers": {}}, f)
        atexit.register(lambda p=path: os.path.exists(p) and os.unlink(p))
        _PROBE_MCP_CONFIG_PATH = path
    return _PROBE_MCP_CONFIG_PATH


async def _run_step2_async() -> tuple[bool, list[str]]:
    """Same as Step 1 but adds --mcp-config to suppress account-level MCP servers."""
    stderr_lines: list[str] = []

    def _capture_stderr(line: str) -> None:
        stderr_lines.append(line)
        print(f"[step2][stderr] {line}", flush=True)

    load_api_key()

    mcp_config_path = _get_probe_mcp_config()
    _log("step2", f"mcp-config file: {mcp_config_path}")
    _log("step2", f"  contents: {open(mcp_config_path).read()!r}")

    options = ClaudeAgentOptions(
        allowed_tools=[],
        max_turns=1,
        max_buffer_size=1 * 1024 * 1024,
        cli_path=_SYSTEM_CLAUDE,
        stderr=_capture_stderr,
        extra_args={"mcp-config": mcp_config_path},
    )

    prompt = "Reply with exactly the word: OK"
    _log("step2", f"Prompt:  {prompt!r}")
    _log("step2", "Options: same as Step 1 + extra_args={mcp-config: <temp_file>}")
    _log("step2", "Sending...")

    message_count = 0
    try:
        async for message in query(prompt=prompt, options=options):
            message_count += 1
            msg_type = getattr(message, "type", type(message).__name__)
            msg_subtype = getattr(message, "subtype", "—")
            raw_size = len(repr(message))
            _log("step2", f"Message {message_count}: type={msg_type!r}  subtype={msg_subtype!r}  ~{raw_size} bytes")
            if isinstance(message, ResultMessage):
                _log("step2", f"  content preview: {str(getattr(message, 'content', ''))[:120]!r}")
    except Exception as exc:
        _log("step2", f"EXCEPTION: {type(exc).__name__}: {exc}")
        if stderr_lines:
            _log("step2", f"Subprocess stderr ({len(stderr_lines)} lines):")
            for line in stderr_lines:
                _log("step2", f"  stderr> {line}")
        return False, stderr_lines

    _log("step2", f"Received {message_count} message(s) total")
    return True, stderr_lines


def run_step2() -> bool:
    """Run Step 1 + --mcp-config override. Returns True on success."""
    _log("step2", "=" * 50)
    _log("step2", "Step 2: Same call + --mcp-config (suppress account MCP servers)")
    _log("step2", "=" * 50)

    passed, stderr_lines = asyncio.run(_run_step2_async())

    _log("step2", "")
    if passed:
        _log("step2", "Step 2: PASS  ← MCP servers were the cause of Step 1 failure")
    else:
        _log("step2", "Step 2: FAIL")
        if not stderr_lines:
            _log("step2", "No stderr captured — the subprocess may have failed silently")
        _log("step2", "  --mcp-config did NOT fix the issue; cause is something else")
    return passed


# ---------------------------------------------------------------------------
# Step 3 — Ignore post-result cleanup errors
# ---------------------------------------------------------------------------

async def _run_step3_async() -> tuple[bool, str]:
    """Same call as Step 1 but ignores exceptions that happen AFTER a ResultMessage.

    Hypothesis: account-level MCP servers (e.g. Google Calendar) can't
    cleanly disconnect, causing exit code 1.  The query itself succeeds —
    the error only occurs during subprocess shutdown.  If we already have the
    result we should not treat that as a failure.
    """
    stderr_lines: list[str] = []

    def _capture_stderr(line: str) -> None:
        stderr_lines.append(line)
        print(f"[step3][stderr] {line}", flush=True)

    load_api_key()

    options = ClaudeAgentOptions(
        allowed_tools=[],
        max_turns=1,
        max_buffer_size=1 * 1024 * 1024,
        cli_path=_SYSTEM_CLAUDE,
        stderr=_capture_stderr,
    )

    prompt = "Reply with exactly the word: OK"
    _log("step3", f"Prompt:  {prompt!r}")
    _log("step3", "Options: same as Step 1")
    _log("step3", "Change:  exception after ResultMessage is treated as success")
    _log("step3", "Sending...")

    result_received = False
    result_subtype = None
    message_count = 0

    try:
        async for message in query(prompt=prompt, options=options):
            message_count += 1
            msg_type = getattr(message, "type", type(message).__name__)
            msg_subtype = getattr(message, "subtype", "—")
            raw_size = len(repr(message))
            _log("step3", f"Message {message_count}: type={msg_type!r}  subtype={msg_subtype!r}  ~{raw_size} bytes")
            if isinstance(message, ResultMessage):
                result_received = True
                result_subtype = getattr(message, "subtype", None)
                _log("step3", f"  content preview: {str(getattr(message, 'content', ''))[:120]!r}")
    except Exception as exc:
        if result_received:
            _log("step3", f"Post-result exception (ignored): {type(exc).__name__}: {exc}")
            _log("step3", "  → Query succeeded; this is cleanup noise from account MCP servers")
        else:
            _log("step3", f"Pre-result EXCEPTION (real failure): {type(exc).__name__}: {exc}")
            return False, "pre-result exception"

    _log("step3", f"Received {message_count} message(s) total  result_subtype={result_subtype!r}")
    return True, result_subtype or "unknown"


def run_step3() -> bool:
    """Step 1 with post-result exception tolerance. Returns True on success."""
    _log("step3", "=" * 50)
    _log("step3", "Step 3: Ignore post-result cleanup errors")
    _log("step3", "=" * 50)

    passed, detail = asyncio.run(_run_step3_async())

    _log("step3", "")
    if passed:
        _log("step3", f"Step 3: PASS  (result_subtype={detail!r})")
        _log("step3", "  ← Fix confirmed: ignore post-result exceptions in SDK calls")
    else:
        _log("step3", f"Step 3: FAIL  ({detail})")
        _log("step3", "  The exception occurred before any result — a different problem")
    return passed
