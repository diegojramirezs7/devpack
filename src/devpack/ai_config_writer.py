"""Phase 1 — AI tool config files and ignore files.

Writes .claudeignore / .cursorignore / .copilotignore and agents.md
into the target repo without ever overwriting user content.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devpack.models import IDETarget, ProjectContext, Skill

# ---------------------------------------------------------------------------
# Ignore files
# ---------------------------------------------------------------------------

_IGNORE_BASELINE: list[str] = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "secrets/",
]

_IDE_IGNORE_FILE: dict[str, str] = {
    "claude-code": ".claudeignore",
    "cursor": ".cursorignore",
    "vscode": ".copilotignore",
}

_DEVPACK_COMMENT = "# Added by devpack"


def write_ignore_files(repo_path: Path, ide: "IDETarget") -> list[tuple[str, str]]:
    """Create or merge the AI ignore file for *ide* in *repo_path*.

    Returns a list of ``(filename, action)`` where action is one of:
    ``"created"``, ``"updated"``, or ``"skipped"`` (already had all entries).
    """
    filename = _IDE_IGNORE_FILE.get(ide.id)
    if not filename:
        return []

    target = repo_path / filename
    if not target.exists():
        target.write_text("\n".join(_IGNORE_BASELINE) + "\n")
        return [(filename, "created")]

    existing_text = target.read_text()
    existing_lines = {line.strip() for line in existing_text.splitlines()}
    missing = [e for e in _IGNORE_BASELINE if e not in existing_lines]
    if missing:
        addition = "\n" + _DEVPACK_COMMENT + "\n" + "\n".join(missing) + "\n"
        target.write_text(existing_text.rstrip("\n") + addition)
        return [(filename, "updated")]

    return [(filename, "skipped")]


# ---------------------------------------------------------------------------
# agents.md
# ---------------------------------------------------------------------------


def _build_agents_md(context: "ProjectContext", selected_skills: list["Skill"]) -> str:
    lines: list[str] = ["# agents.md", ""]

    # Stack summary
    lines += ["## Stack Summary", "", context.summary, ""]

    # Directory structure
    if context.directory_structure:
        lines += [
            "## Directory Structure",
            "",
            "```",
            context.directory_structure,
            "```",
            "",
        ]

    # Key commands
    cmds = context.setup_commands
    has_any_cmd = any([cmds.install, cmds.dev, cmds.test, cmds.build])
    if has_any_cmd:
        lines += ["## Key Commands", ""]
        if cmds.install:
            lines.append(f"- **Install:** `{cmds.install}`")
        if cmds.dev:
            lines.append(f"- **Dev server:** `{cmds.dev}`")
        if cmds.test:
            lines.append(f"- **Test:** `{cmds.test}`")
        if cmds.build:
            lines.append(f"- **Build:** `{cmds.build}`")
        lines.append("")

    # Installed skills
    if selected_skills:
        lines += ["## Installed Skills", ""]
        lines.append("| Skill | Description |")
        lines.append("|---|---|")
        for skill in selected_skills:
            # Escape pipes inside descriptions
            desc = skill.description.replace("|", "\\|")
            lines.append(f"| `{skill.id}` | {desc} |")
        lines.append("")

    return "\n".join(lines)


def write_agents_md(
    repo_path: Path,
    context: "ProjectContext",
    selected_skills: list["Skill"],
) -> tuple[Path, str]:
    """Write agents.md to *repo_path*.

    Returns ``(path, action)`` where action is ``"created"`` or ``"skipped"``.
    If the file already exists it is not modified; only the Installed Skills
    section is offered for update (not automated — reported for manual action).
    """
    target = repo_path / "agents.md"
    if target.exists():
        return target, "skipped"

    content = _build_agents_md(context, selected_skills)
    target.write_text(content)
    return target, "created"
