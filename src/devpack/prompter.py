from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from devpack.models import IDETarget, IDE_TARGETS, Skill


def prompt_skill_selection(skills: list[Skill]) -> list[Skill]:
    """Present a checkbox list of skills, all pre-selected. Returns the confirmed subset."""
    skills_by_id = {skill.id: skill for skill in skills}
    choices = [
        Choice(value=skill.id, name=f"{skill.name} — {_truncate(skill.description, 80)}", enabled=True)
        for skill in skills
    ]

    selected_ids: list[str] = inquirer.checkbox(
        message="Select skills to add (space to toggle, enter to confirm):",
        choices=choices,
        cycle=True,
        transformer=lambda result: f"{len(result)} skill(s) selected",
    ).execute()

    return [skills_by_id[sid] for sid in selected_ids]


def prompt_ide_selection(repo_path: Path) -> IDETarget:
    """Prompt the user to choose a target IDE, defaulting to one already detected in the repo."""
    detected = _detect_existing_ide(repo_path)
    default = detected or IDE_TARGETS[0]

    choices = [
        Choice(value=ide.id, name=ide.name)
        for ide in IDE_TARGETS
    ]

    selected_id: str = inquirer.select(
        message="Target IDE / agent:",
        choices=choices,
        default=default.id,
        transformer=lambda result: result,
    ).execute()

    return next(ide for ide in IDE_TARGETS if ide.id == selected_id)


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
