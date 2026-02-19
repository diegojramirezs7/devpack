from pathlib import Path

from devpack.models import IDETarget, Skill

_SECTION_MARKER = "<!-- devpack-skills -->"
_SECTION_END_MARKER = "<!-- /devpack-skills -->"

_IDE_INVOKE_HINT = {
    "claude-code": "Type `/{name}` in your Claude Code session.",
    "cursor":      "Use `@{name}` in a Cursor chat.",
    "vscode":      "Reference `#{name}` in a VS Code Copilot chat.",
}


def update_readme(repo_path: Path, skills: list[Skill], ide: IDETarget) -> None:
    """Append or replace the Skills section in the repo's README."""
    readme_path = _find_readme(repo_path)
    existing = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

    section = _build_section(skills, ide)

    if _SECTION_MARKER in existing:
        updated = _replace_section(existing, section)
    else:
        separator = "\n\n" if existing and not existing.endswith("\n\n") else ""
        updated = existing + separator + section + "\n"

    readme_path.write_text(updated, encoding="utf-8")


# --- Private helpers ---

def _find_readme(repo_path: Path) -> Path:
    for name in ("README.md", "readme.md", "Readme.md"):
        candidate = repo_path / name
        if candidate.exists():
            return candidate
    return repo_path / "README.md"


def _build_section(skills: list[Skill], ide: IDETarget) -> str:
    hint_template = _IDE_INVOKE_HINT.get(ide.id, "See your IDE documentation.")
    lines = [
        _SECTION_MARKER,
        "",
        "## Agent Skills",
        "",
        f"This repo includes {len(skills)} agent skill(s) added by [DevPack](https://github.com/your-org/devpack).",
        "",
        "| Skill | Description | How to use |",
        "| ----- | ----------- | ---------- |",
    ]

    for skill in skills:
        hint = hint_template.format(name=skill.id)
        desc = skill.description.split(".")[0]  # First sentence only
        lines.append(f"| **{skill.name}** | {desc} | {hint} |")

    lines += ["", _SECTION_END_MARKER]
    return "\n".join(lines)


def _replace_section(content: str, new_section: str) -> str:
    start = content.find(_SECTION_MARKER)
    end = content.find(_SECTION_END_MARKER)
    if start == -1 or end == -1:
        return content + "\n\n" + new_section + "\n"
    end += len(_SECTION_END_MARKER)
    return content[:start] + new_section + content[end:]
