import importlib.metadata
import importlib.resources
import os
from pathlib import Path
from typing import Annotated, Optional

import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from devpack.config import (
    api_key_source,
    append_to_shell_rc,
    load_api_key,
    save_to_config_file,
)
from devpack.detector import detect_stack, detect_context
from devpack.matcher import load_skills, load_installed_skills, match_skills
from devpack.prompter import prompt_ide_selection, prompt_skill_selection
from devpack.guide_writer import write_guide
from devpack.writer import write_skills
from devpack.ai_config_writer import write_ignore_files, write_agents_md

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        v = importlib.metadata.version("devpack-kit")
        typer.echo(f"devpack-kit {v}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(  # noqa: ARG001
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


@app.command("doctor")
def doctor() -> None:
    """Check your devpack installation."""
    import sys

    all_ok = True

    def check(label: str, ok: bool, detail: str) -> None:
        status = "✓" if ok else "✗"
        typer.echo(f"  {label:<14}{detail}  {status}")

    v = sys.version_info
    py_ok = v >= (3, 11)
    check(
        "Python",
        py_ok,
        f"{v.major}.{v.minor}.{v.micro}" + ("" if py_ok else "  (requires 3.11+)"),
    )
    if not py_ok:
        all_ok = False

    pkg_version = importlib.metadata.version("devpack-kit")
    check("Package", True, f"devpack {pkg_version}")

    source = api_key_source()
    if source:
        check("API key", True, f"found in {source}")
    else:
        check("API key", False, "not set  —  run `devpack configure`")
        all_ok = False

    skills = load_skills(_STARTERPACK_PATH)
    check("Starterpack", True, f"{len(skills)} skills loaded")

    typer.echo()
    if all_ok:
        typer.echo("Everything looks good.")
    else:
        typer.echo("Some checks failed. See above for details.")
        raise typer.Exit(1)


@app.command("configure")
def configure() -> None:
    """Set up your Anthropic API key."""
    typer.echo("DevPack Configuration\n")

    existing = load_api_key()
    if existing:
        masked = existing[:12] + "..." + existing[-4:]
        typer.echo(f"An API key is already configured ({masked}).")
        if not typer.confirm("Replace it?", default=False):
            raise typer.Exit()
        typer.echo()

    key = typer.prompt(
        "Anthropic API key (get one at console.anthropic.com/settings/api-keys) or from your administrator",
        hide_input=True,
    )

    if not key.startswith("sk-ant-"):
        typer.echo(
            "Error: that doesn't look like a valid Anthropic API key (expected prefix: sk-ant-).",
            err=True,
        )
        raise typer.Exit(1)

    location: str = inquirer.select(
        message="Where should devpack store it?",
        choices=[
            Choice(
                value="config",
                name="~/.config/devpack/.env  (recommended — never committed to a repo)",
            ),
            Choice(value="zshrc", name="~/.zshrc"),
            Choice(value="zprofile", name="~/.zprofile"),
            Choice(value="manual", name="I'll set it myself — just show me what to do"),
        ],
    ).execute()

    typer.echo()

    if location == "config":
        path = save_to_config_file(key)
        typer.echo(f"API key saved to {path}")
    elif location == "zshrc":
        rc = Path.home() / ".zshrc"
        append_to_shell_rc(key, rc)
        typer.echo(f"Added to {rc}  —  run: source ~/.zshrc")
    elif location == "zprofile":
        rc = Path.home() / ".zprofile"
        append_to_shell_rc(key, rc)
        typer.echo(f"Added to {rc}  —  run: source ~/.zprofile")
    elif location == "manual":
        typer.echo(
            "Add this line to your shell config (e.g. ~/.zshrc or ~/.zprofile):\n"
        )
        typer.echo(f'  export ANTHROPIC_API_KEY="{key}"\n')
        typer.echo("Then reload your shell or run: source ~/.zshrc")

    typer.echo("\nAll set. Run `devpack add-skills` to get started.")


@app.command("add-skills")
def add_skills(
    repo_path: Annotated[
        Path, typer.Argument(help="Path to the target repository.")
    ] = Path("."),
    debug: bool = typer.Option(
        False, "--debug", help="Show full tracebacks and verbose API logging."
    ),
) -> None:
    """Detect your stack and add matching agent skills to the repo."""
    if debug:
        os.environ["ANTHROPIC_LOG"] = "debug"

    repo_path = repo_path.resolve()

    # Early validation
    if not repo_path.is_dir():
        raise typer.BadParameter(f"{repo_path} is not a directory.")

    if not os.access(repo_path, os.W_OK):
        typer.echo(f"Error: no write permission for {repo_path}.", err=True)
        raise typer.Exit(1)

    if not any(repo_path.iterdir()):
        typer.echo("Warning: the target directory appears to be empty.\n")

    try:
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

        # 6. Write local guide (merge with any previously installed skills)
        typer.echo("Generating skill usage guide...")
        prev = load_installed_skills(repo_path, ide)
        selected_ids = {s.id for s in selected}
        all_skills = selected + [s for s in prev if s.id not in selected_ids]
        guide_path = write_guide(repo_path, all_skills, ide, stack)

        # 7. Summary
        typer.echo(f"\nAdded {len(written)} skill(s) to {ide.skill_path}/")
        for path in written:
            typer.echo(f"  + {path.name}")
        typer.echo(
            f"Wrote local usage guide to {guide_path.relative_to(repo_path)} (gitignored)"
        )

    except (typer.Exit, typer.Abort):
        raise
    except KeyboardInterrupt:
        typer.echo("\nCancelled.")
        raise typer.Exit(1)
    except EnvironmentError as e:
        typer.echo(f"\nError: {e}", err=True)
        raise typer.Exit(1)
    except PermissionError:
        typer.echo(
            f"\nError: permission denied writing to {repo_path}.\n"
            "Check that you own that directory.",
            err=True,
        )
        raise typer.Exit(1)
    except Exception as e:
        if debug:
            raise
        typer.echo(f"\nError: {e}", err=True)
        typer.echo(
            "\nRun with --debug for full details, or report the issue:\n"
            "  https://github.com/diegojramirezs7/devpack/issues",
            err=True,
        )
        raise typer.Exit(1)


@app.command("init")
def init(
    repo_path: Annotated[
        Path, typer.Argument(help="Path to the target repository.")
    ] = Path("."),
    debug: bool = typer.Option(False, "--debug", help="Show full tracebacks."),
) -> None:
    """Set up your repo with agent skills and AI config."""
    if debug:
        os.environ["ANTHROPIC_LOG"] = "debug"

    repo_path = repo_path.resolve()

    if not repo_path.is_dir():
        raise typer.BadParameter(f"{repo_path} is not a directory.")
    if not os.access(repo_path, os.W_OK):
        typer.echo(f"Error: no write permission for {repo_path}.", err=True)
        raise typer.Exit(1)
    if not any(repo_path.iterdir()):
        typer.echo("Warning: the target directory appears to be empty.\n")

    try:
        # 1. Single SDK call — gather all context upfront
        typer.echo("Analyzing your project with Claude...")
        context = detect_context(repo_path)

        if context.technologies:
            tech_names = ", ".join(t.name for t in context.technologies)
            typer.echo(f"\nDetected stack: {tech_names}")
        else:
            typer.echo("\nNo stack detected — showing all available skills.")
        if context.setup_commands.dev:
            typer.echo(f"Dev server:    {context.setup_commands.dev}")
        if context.setup_commands.test:
            typer.echo(f"Test command:  {context.setup_commands.test}")
        typer.echo()

        # 2–4. Skills: match → prompt → write  (identical to add-skills)
        skills = load_skills(_STARTERPACK_PATH)
        matched = match_skills(skills, context.technologies)

        if not matched:
            typer.echo("No applicable skills found for this stack.")
            raise typer.Exit()

        selected = prompt_skill_selection(matched)
        if not selected:
            typer.echo("No skills selected. Nothing to do.")
            raise typer.Exit()

        ide = prompt_ide_selection(repo_path)
        written = write_skills(selected, repo_path, ide)

        typer.echo("Generating skill usage guide...")
        prev = load_installed_skills(repo_path, ide)
        selected_ids = {s.id for s in selected}
        all_skills = selected + [s for s in prev if s.id not in selected_ids]
        guide_path = write_guide(repo_path, all_skills, ide, context.technologies)

        # Phase 1 — AI config files and ignore files
        ignore_results = write_ignore_files(repo_path, ide)
        _, agents_action = write_agents_md(repo_path, context, selected)

        # Summary
        typer.echo(f"\nAdded {len(written)} skill(s) to {ide.skill_path}/")
        for path in written:
            typer.echo(f"  + {path.name}")
        typer.echo(
            f"Wrote local usage guide to {guide_path.relative_to(repo_path)} (gitignored)"
        )

        typer.echo("\nAI config files:")
        for filename, action in ignore_results:
            if action == "skipped":
                typer.echo(f"  ~ {filename} (already complete — skipped)")
            else:
                typer.echo(f"  + {filename} ({action})")
        if agents_action == "created":
            typer.echo("  + agents.md (created)")
        else:
            typer.echo(
                "  ~ agents.md already exists — skipped\n"
                "    To refresh the Installed Skills section, edit agents.md manually."
            )

    except (typer.Exit, typer.Abort):
        raise
    except KeyboardInterrupt:
        typer.echo("\nCancelled.")
        raise typer.Exit(1)
    except EnvironmentError as e:
        typer.echo(f"\nError: {e}", err=True)
        raise typer.Exit(1)
    except PermissionError:
        typer.echo(
            f"\nError: permission denied writing to {repo_path}.\n"
            "Check that you own that directory.",
            err=True,
        )
        raise typer.Exit(1)
    except Exception as e:
        if debug:
            raise
        typer.echo(f"\nError: {e}", err=True)
        typer.echo(
            "\nRun with --debug for full details, or report the issue:\n"
            "  https://github.com/diegojramirezs7/devpack/issues",
            err=True,
        )
        raise typer.Exit(1)
