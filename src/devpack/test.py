from pathlib import Path

import yaml

from devpack.models import Skill
import warnings

_STARTERPACK_PATH = Path(__file__).parent.parent.parent / "starterpack"


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


def load_skills(starterpack_path: Path) -> list[Skill]:
    """Scan starterpack_path/agent-skills/ and return all valid skills."""
    skills_dir = starterpack_path / "agent-skills"

    print(f"Looking for skills in {skills_dir}...")  # Debug print

    if not skills_dir.is_dir():
        return []

    skills = []
    print(f"Scanning {skills_dir} for skills...")
    print(skills_dir.iterdir())
    for skill_dir in sorted(skills_dir.iterdir()):
        print(skill_dir)
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

        skills.append(
            Skill(
                id=skill_dir.name,
                name=name,
                description=description,
                path=skill_dir,
            )
        )

    return skills


if __name__ == "__main__":

    skills = load_skills(_STARTERPACK_PATH)

    print(skills)

    # for skill in skills:
    #     print(f"{skill.name}: {skill.description}")
