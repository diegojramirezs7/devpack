import warnings
from pathlib import Path

import yaml

from devpack.models import Skill, Technology

# Skills always offered regardless of detected stack.
GENERAL_SKILL_IDS: set[str] = {"feature-implementation-plan"}

# Keywords in a skill's description that make it relevant for any frontend stack.
FRONTEND_KEYWORDS: set[str] = {"web", "performance", "accessibility", "frontend", "lighthouse", "seo"}


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
            warnings.warn(f"Skipping {skill_dir.name}: frontmatter missing 'name' or 'description'")
            continue

        skills.append(Skill(
            id=skill_dir.name,
            name=name,
            description=description,
            path=skill_dir,
        ))

    return skills


def match_skills(skills: list[Skill], stack: list[Technology]) -> list[Skill]:
    """Return skills relevant to the detected stack."""
    if not stack:
        return skills

    tech_terms = {t.id.lower() for t in stack} | {t.name.lower() for t in stack}
    has_frontend = any(t.is_frontend for t in stack)

    matched = []
    for skill in skills:
        if _is_relevant(skill, tech_terms, has_frontend):
            matched.append(skill)

    return matched


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


def _is_relevant(skill: Skill, tech_terms: set[str], has_frontend: bool) -> bool:
    if skill.id in GENERAL_SKILL_IDS:
        return True

    skill_text = f"{skill.id} {skill.description}".lower()

    # Match if any detected technology name/id appears in the skill text.
    if any(term in skill_text for term in tech_terms):
        return True

    # Match cross-cutting frontend skills when a frontend stack is detected.
    if has_frontend and any(kw in skill_text for kw in FRONTEND_KEYWORDS):
        return True

    return False
