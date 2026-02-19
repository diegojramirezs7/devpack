from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class Technology:
    id: str
    name: str
    # Each indicator receives the repo path and returns True if the technology is present.
    indicators: list[Callable[[Path], bool]] = field(default_factory=list, repr=False)
    is_frontend: bool = False


@dataclass
class Skill:
    id: str
    name: str
    description: str
    path: Path


@dataclass
class IDETarget:
    id: str
    name: str
    skill_path: str  # Relative path inside the repo where skills are placed


CLAUDE_CODE = IDETarget("claude-code", "Claude Code", ".claude/skills")
CURSOR = IDETarget("cursor", "Cursor", ".cursor/skills")
VSCODE = IDETarget("vscode", "VS Code Copilot", ".agents/skills")

IDE_TARGETS: list[IDETarget] = [CLAUDE_CODE, CURSOR, VSCODE]
