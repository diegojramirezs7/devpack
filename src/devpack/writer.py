import shutil
from pathlib import Path

from devpack.models import Agent, IDETarget, Skill

_AGENTS_PATH = ".claude/agents"


def write_agents(agents: list[Agent], repo_path: Path) -> list[Path]:
    """Copy each agent .md file into .claude/agents/ in the repo."""
    written = []
    base = repo_path / _AGENTS_PATH
    base.mkdir(parents=True, exist_ok=True)

    for agent in agents:
        dest = base / f"{agent.id}.md"
        shutil.copy2(agent.path, dest)
        written.append(dest)

    return written


def write_skills(skills: list[Skill], repo_path: Path, ide: IDETarget) -> list[Path]:
    """Copy each skill directory into the IDE-specific skills path in the repo."""
    written = []
    base = repo_path / ide.skill_path

    for skill in skills:
        dest = base / skill.id
        shutil.copytree(skill.path, dest, dirs_exist_ok=True)
        written.append(dest)

    return written
