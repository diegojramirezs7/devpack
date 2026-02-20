from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel


class DetectedTechnology(BaseModel):
    id: str
    name: str
    is_frontend: bool = False


class StackDetectionResult(BaseModel):
    technologies: list[DetectedTechnology]
    summary: str


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
