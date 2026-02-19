from pathlib import Path

from devpack.models import Technology
from devpack.registry.technologies import TECHNOLOGIES


def detect_stack(repo_path: Path) -> list[Technology]:
    """Return all technologies detected in the given repo path."""
    detected = []
    for tech in TECHNOLOGIES:
        if any(indicator(repo_path) for indicator in tech.indicators):
            detected.append(tech)
    return detected
