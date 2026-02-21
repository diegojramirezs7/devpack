import importlib.metadata
import importlib.resources
from pathlib import Path
from typing import Annotated, Optional

import typer

from devpack.detector import detect_stack
from devpack.matcher import load_skills, match_skills
from devpack.prompter import prompt_ide_selection, prompt_skill_selection
from devpack.readme_updater import update_readme
from devpack.writer import write_skills

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        v = importlib.metadata.version("devpack")
        typer.echo(f"devpack {v}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """DevPack — add agent skills to your repo."""


_STARTERPACK_PATH = importlib.resources.files("devpack") / "starterpack"


@app.command("add-skills")
def add_skills(
    repo_path: Annotated[
        Path, typer.Argument(help="Path to the target repository.")
    ] = Path("."),
) -> None:
    """Detect your stack and add matching agent skills to the repo."""
    repo_path = repo_path.resolve()

    if not repo_path.is_dir():
        raise typer.BadParameter(f"{repo_path} is not a directory.")

    # 1. Detect stack
    typer.echo("Analyzing your stack with Claude...")
    stack = detect_stack(repo_path)
    if stack:
        tech_names = ", ".join(t.name for t in stack)
        typer.echo(f"\nDetected stack: {tech_names}\n")
    else:
        typer.echo("\nNo stack detected — showing all available skills.\n")

    # 2. Load and match skills
    skills = load_skills(_STARTERPACK_PATH)
    matched = match_skills(skills, stack)

    if not matched:
        typer.echo("No applicable skills found for this stack.")
        raise typer.Exit()

    # 3. User selects skills
    selected = prompt_skill_selection(matched)

    if not selected:
        typer.echo("No skills selected. Nothing to do.")
        raise typer.Exit()

    # 4. User selects IDE
    ide = prompt_ide_selection(repo_path)

    # 5. Write skills to repo
    written = write_skills(selected, repo_path, ide)

    # 6. Update README
    update_readme(repo_path, selected, ide)

    # 7. Summary
    typer.echo(f"\nAdded {len(written)} skill(s) to {ide.skill_path}/")
    for path in written:
        typer.echo(f"  + {path.name}")
    typer.echo("\nUpdated README with skills documentation.")
