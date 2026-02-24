from pathlib import Path

import pytest

from devpack.ai_config_writer import (
    _IGNORE_BASELINE,
    _DEVPACK_COMMENT,
    _IDE_IGNORE_FILE,
    write_ignore_files,
    write_agents_md,
)
from devpack.models import CLAUDE_CODE, CURSOR, VSCODE, DetectedTechnology, SetupCommands, ProjectContext, Skill


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_context(**kwargs) -> ProjectContext:
    defaults = dict(
        technologies=[DetectedTechnology(id="django", name="Django")],
        summary="A Django web app.",
        directory_structure="src/\n  app/\n    models.py",
        setup_commands=SetupCommands(
            install="pip install -r requirements.txt",
            dev="python manage.py runserver",
            test="pytest",
            build=None,
        ),
        runtime_versions={"python": "3.11"},
    )
    defaults.update(kwargs)
    return ProjectContext(**defaults)


def _skill(id: str = "my-skill", description: str = "Does things.") -> Skill:
    return Skill(id=id, name=id, description=description, path=Path("/fake"))


# ---------------------------------------------------------------------------
# write_ignore_files
# ---------------------------------------------------------------------------

class TestWriteIgnoreFiles:
    def test_creates_correct_file_for_each_ide(self, tmp_path: Path):
        for ide, filename in [(CLAUDE_CODE, ".claudeignore"), (CURSOR, ".cursorignore"), (VSCODE, ".copilotignore")]:
            repo = tmp_path / ide.id
            repo.mkdir()
            results = write_ignore_files(repo, ide)
            assert len(results) == 1
            assert results[0] == (filename, "created")
            assert (repo / filename).exists()

    def test_does_not_create_other_ide_files(self, tmp_path: Path):
        write_ignore_files(tmp_path, CLAUDE_CODE)
        assert not (tmp_path / ".cursorignore").exists()
        assert not (tmp_path / ".copilotignore").exists()

    def test_created_file_contains_baseline_entries(self, tmp_path: Path):
        write_ignore_files(tmp_path, CLAUDE_CODE)
        content = (tmp_path / ".claudeignore").read_text()
        for entry in _IGNORE_BASELINE:
            assert entry in content

    def test_skips_when_all_entries_present(self, tmp_path: Path):
        (tmp_path / ".claudeignore").write_text("\n".join(_IGNORE_BASELINE) + "\n")
        results = write_ignore_files(tmp_path, CLAUDE_CODE)
        assert results == [(".claudeignore", "skipped")]

    def test_appends_missing_entries_under_comment(self, tmp_path: Path):
        (tmp_path / ".claudeignore").write_text(".env\n*.key\n")
        results = dict(write_ignore_files(tmp_path, CLAUDE_CODE))
        assert results[".claudeignore"] == "updated"

        content = (tmp_path / ".claudeignore").read_text()
        assert _DEVPACK_COMMENT in content
        assert ".env.*" in content
        assert ".env" in content  # original preserved

    def test_does_not_duplicate_existing_entries(self, tmp_path: Path):
        (tmp_path / ".claudeignore").write_text("\n".join(_IGNORE_BASELINE) + "\nextra-entry\n")
        results = dict(write_ignore_files(tmp_path, CLAUDE_CODE))
        assert results[".claudeignore"] == "skipped"

        lines = [l.strip() for l in (tmp_path / ".claudeignore").read_text().splitlines() if l.strip()]
        for entry in _IGNORE_BASELINE:
            assert lines.count(entry) == 1, f"entry '{entry}' duplicated in output"


# ---------------------------------------------------------------------------
# write_agents_md
# ---------------------------------------------------------------------------

class TestWriteAgentsMd:
    def test_creates_file_when_absent(self, tmp_path: Path):
        ctx = _make_context()
        path, action = write_agents_md(tmp_path, ctx, [_skill()])

        assert action == "created"
        assert path.exists()

    def test_skips_when_file_exists(self, tmp_path: Path):
        (tmp_path / "agents.md").write_text("# existing\n")
        ctx = _make_context()
        _, action = write_agents_md(tmp_path, ctx, [_skill()])

        assert action == "skipped"
        # Original content untouched
        assert (tmp_path / "agents.md").read_text() == "# existing\n"

    def test_contains_summary(self, tmp_path: Path):
        ctx = _make_context(summary="This is a special Django project.")
        write_agents_md(tmp_path, ctx, [])

        content = (tmp_path / "agents.md").read_text()
        assert "This is a special Django project." in content

    def test_contains_directory_structure(self, tmp_path: Path):
        ctx = _make_context(directory_structure="src/\n  main.py")
        write_agents_md(tmp_path, ctx, [])

        content = (tmp_path / "agents.md").read_text()
        assert "src/" in content
        assert "main.py" in content

    def test_contains_setup_commands(self, tmp_path: Path):
        ctx = _make_context()
        write_agents_md(tmp_path, ctx, [])

        content = (tmp_path / "agents.md").read_text()
        assert "pip install -r requirements.txt" in content
        assert "python manage.py runserver" in content
        assert "pytest" in content

    def test_omits_build_when_none(self, tmp_path: Path):
        ctx = _make_context(
            setup_commands=SetupCommands(install=None, dev=None, test=None, build=None)
        )
        write_agents_md(tmp_path, ctx, [])

        content = (tmp_path / "agents.md").read_text()
        assert "Key Commands" not in content

    def test_contains_installed_skills(self, tmp_path: Path):
        ctx = _make_context()
        skills = [_skill("refine-feature", "Refines feature specs.")]
        write_agents_md(tmp_path, ctx, skills)

        content = (tmp_path / "agents.md").read_text()
        assert "refine-feature" in content
        assert "Refines feature specs." in content

    def test_empty_skills_list_omits_section(self, tmp_path: Path):
        ctx = _make_context()
        write_agents_md(tmp_path, ctx, [])

        content = (tmp_path / "agents.md").read_text()
        assert "Installed Skills" not in content
