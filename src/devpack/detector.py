import asyncio
from pathlib import Path

from devpack.claude_agent import detect_tech_stack
from devpack.models import DetectedTechnology


def detect_stack(repo_path: Path) -> list[DetectedTechnology]:
    """Detect the tech stack by querying Claude against the repo."""
    result = asyncio.run(detect_tech_stack(repo_path))
    return result.technologies
