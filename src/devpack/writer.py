import shutil
from pathlib import Path

from devpack.models import IDETarget, Skill


def write_skills(skills: list[Skill], repo_path: Path, ide: IDETarget) -> list[Path]:
    """Copy each skill directory into the IDE-specific skills path in the repo."""
    written = []
    base = repo_path / ide.skill_path

    for skill in skills:
        dest = base / skill.id
        shutil.copytree(skill.path, dest, dirs_exist_ok=True)
        written.append(dest)

    return written
