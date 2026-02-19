from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from devpack.models import IDETarget, IDE_TARGETS, Skill


def prompt_skill_selection(skills: list[Skill]) -> list[Skill]:
    """Present a checkbox list of skills, all pre-selected. Returns the confirmed subset."""
    choices = [
        Choice(value=skill, name=f"{skill.name} — {_truncate(skill.description, 80)}", enabled=True)
        for skill in skills
    ]

    selected: list[Skill] = inquirer.checkbox(
        message="Select skills to add (space to toggle, enter to confirm):",
        choices=choices,
        cycle=True,
        transformer=lambda result: f"{len(result)} skill(s) selected",
    ).execute()

    return selected


def prompt_ide_selection(repo_path: Path) -> IDETarget:
    """Prompt the user to choose a target IDE, defaulting to one already detected in the repo."""
    detected = _detect_existing_ide(repo_path)
    default = detected or IDE_TARGETS[0]

    choices = [
        Choice(value=ide, name=ide.name)
        for ide in IDE_TARGETS
    ]

    selected: IDETarget = inquirer.select(
        message="Target IDE / agent:",
        choices=choices,
        default=default,
        transformer=lambda result: result.name,
    ).execute()

    return selected


# --- Private helpers ---

def _detect_existing_ide(repo_path: Path) -> IDETarget | None:
    """Return an IDETarget if exactly one IDE config directory exists in the repo."""
    detected = [
        ide for ide in IDE_TARGETS
        if (repo_path / ide.skill_path.split("/")[0]).is_dir()
    ]
    return detected[0] if len(detected) == 1 else None


def _truncate(text: str, max_len: int) -> str:
    return text[:max_len - 1] + "…" if len(text) > max_len else text
