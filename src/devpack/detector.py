import asyncio
from pathlib import Path

from devpack.claude_agent import detect_tech_stack, detect_project_context
from devpack.models import DetectedTechnology, ProjectContext


def detect_stack(repo_path: Path) -> list[DetectedTechnology]:
    """Detect the tech stack by querying Claude against the repo."""
    result = asyncio.run(detect_tech_stack(repo_path))
    return result.technologies


def detect_context(repo_path: Path) -> ProjectContext:
    """Detect full project context by querying Claude against the repo."""
    return asyncio.run(detect_project_context(repo_path))
