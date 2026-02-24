from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class DetectedTechnology(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    is_frontend: bool = False


class StackDetectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    technologies: list[DetectedTechnology]
    summary: str


class SetupCommands(BaseModel):
    model_config = ConfigDict(extra="forbid")

    install: str | None = None
    dev:     str | None = None
    test:    str | None = None
    build:   str | None = None


class ProjectContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    technologies:        list[DetectedTechnology]
    summary:             str
    directory_structure: str
    setup_commands:      SetupCommands
    runtime_versions:    dict[str, str]


@dataclass
class Skill:
    id: str
    name: str
    description: str
    path: Path
    tags: list[str] = field(default_factory=list)


@dataclass
class IDETarget:
    id: str
    name: str
    skill_path: str  # Relative path inside the repo where skills are placed


CLAUDE_CODE = IDETarget("claude-code", "Claude Code", ".claude/skills")
CURSOR = IDETarget("cursor", "Cursor", ".cursor/skills")
VSCODE = IDETarget("vscode", "VS Code Copilot", ".agents/skills")

IDE_TARGETS: list[IDETarget] = [CLAUDE_CODE, CURSOR, VSCODE]
