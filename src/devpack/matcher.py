import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from devpack.models import DetectedTechnology, Skill

if TYPE_CHECKING:
    from devpack.models import IDETarget


def load_skills(starterpack_path: Path) -> list[Skill]:
    """Scan starterpack_path/agent-skills/ and return all valid skills."""
    skills_dir = starterpack_path / "agent-skills"
    if not skills_dir.is_dir():
        return []

    skills = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        frontmatter = _parse_frontmatter(skill_md)
        if not frontmatter:
            warnings.warn(f"Skipping {skill_dir.name}: missing or invalid frontmatter")
            continue

        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not name or not description:
            warnings.warn(
                f"Skipping {skill_dir.name}: frontmatter missing 'name' or 'description'"
            )
            continue

        metadata = frontmatter.get("metadata") or {}
        tags = metadata.get("tags") or []

        skills.append(
            Skill(
                id=skill_dir.name,
                name=name,
                description=description,
                path=skill_dir,
                tags=[t.lower() for t in tags],
            )
        )

    return skills


def load_installed_skills(repo_path: Path, ide: "IDETarget") -> list[Skill]:
    """Return skills already installed in *repo_path* for *ide*.

    Scans ``<repo_path>/<ide.skill_path>/`` and parses each subdirectory's
    SKILL.md, using the same logic as :func:`load_skills`.  Directories
    without a valid SKILL.md are silently skipped.
    """
    skills_dir = repo_path / ide.skill_path
    if not skills_dir.is_dir():
        return []

    skills = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        frontmatter = _parse_frontmatter(skill_md)
        if not frontmatter:
            continue

        name = frontmatter.get("name") or skill_dir.name
        description = frontmatter.get("description") or ""
        metadata = frontmatter.get("metadata") or {}
        tags = metadata.get("tags") or []

        skills.append(
            Skill(
                id=skill_dir.name,
                name=name,
                description=description,
                path=skill_dir,
                tags=[t.lower() for t in tags],
            )
        )

    return skills


def match_skills(skills: list[Skill], stack: list[DetectedTechnology]) -> list[Skill]:
    """Return skills relevant to the detected stack."""
    if not stack:
        return skills

    detected_ids = {t.id.lower() for t in stack}
    has_frontend = any(t.is_frontend for t in stack)

    return [s for s in skills if _is_relevant(s, detected_ids, has_frontend)]


# --- Private helpers ---


def _parse_frontmatter(skill_md: Path) -> dict | None:
    """Extract and parse the YAML frontmatter from a SKILL.md file."""
    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None

    if not content.startswith("---"):
        return None

    # Find the closing --- after the opening one.
    end = content.find("---", 3)
    if end == -1:
        return None

    raw = content[3:end].strip()
    try:
        return yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return None


def _is_relevant(skill: Skill, detected_ids: set[str], has_frontend: bool) -> bool:
    if "general" in skill.tags:
        return True
    if has_frontend and "frontend" in skill.tags:
        return True
    if detected_ids.intersection(skill.tags):
        return True
    return False
