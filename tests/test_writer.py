from pathlib import Path

import pytest

from devpack.models import CLAUDE_CODE, CURSOR, Skill
from devpack.writer import write_skills
from devpack.readme_updater import update_readme

STARTERPACK = Path(__file__).parent.parent / "src" / "devpack" / "starterpack"


def _real_skill() -> Skill:
    """Return the django-best-practices skill from the real starterpack."""
    skill_path = STARTERPACK / "agent-skills" / "django-best-practices"
    return Skill(
        id="django-best-practices",
        name="Django Best Practices",
        description="Best practices for Django projects.",
        path=skill_path,
    )


def _fake_skill(tmp_path: Path, skill_id: str = "my-skill") -> Skill:
    skill_dir = tmp_path / "skills_source" / skill_id
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(f"---\nname: {skill_id}\ndescription: A skill.\n---\n")
    (skill_dir / "rules").mkdir()
    (skill_dir / "rules" / "rule-one.md").write_text("# Rule one\n")
    return Skill(id=skill_id, name=skill_id, description="A skill.", path=skill_dir)


# --- write_skills ---

class TestWriteSkills:
    def test_copies_skill_directory(self, tmp_path: Path):
        skill = _fake_skill(tmp_path)
        repo = tmp_path / "repo"
        repo.mkdir()

        write_skills([skill], repo, CLAUDE_CODE)

        dest = repo / ".claude" / "skills" / skill.id
        assert dest.is_dir()
        assert (dest / "SKILL.md").exists()

    def test_copies_subdirectories(self, tmp_path: Path):
        skill = _fake_skill(tmp_path)
        repo = tmp_path / "repo"
        repo.mkdir()

        write_skills([skill], repo, CLAUDE_CODE)

        dest = repo / ".claude" / "skills" / skill.id
        assert (dest / "rules" / "rule-one.md").exists()

    def test_ide_path_differs_per_target(self, tmp_path: Path):
        skill = _fake_skill(tmp_path)
        repo = tmp_path / "repo"
        repo.mkdir()

        write_skills([skill], repo, CURSOR)

        assert (repo / ".cursor" / "skills" / skill.id).is_dir()
        assert not (repo / ".claude" / "skills" / skill.id).exists()

    def test_returns_written_paths(self, tmp_path: Path):
        skill = _fake_skill(tmp_path)
        repo = tmp_path / "repo"
        repo.mkdir()

        result = write_skills([skill], repo, CLAUDE_CODE)

        assert len(result) == 1
        assert result[0] == repo / ".claude" / "skills" / skill.id

    def test_idempotent_second_run(self, tmp_path: Path):
        skill = _fake_skill(tmp_path)
        repo = tmp_path / "repo"
        repo.mkdir()

        write_skills([skill], repo, CLAUDE_CODE)
        write_skills([skill], repo, CLAUDE_CODE)  # Should not raise

        assert (repo / ".claude" / "skills" / skill.id / "SKILL.md").exists()

    def test_real_skill_copied_correctly(self, tmp_path: Path):
        skill = _real_skill()
        write_skills([skill], tmp_path, CLAUDE_CODE)

        dest = tmp_path / ".claude" / "skills" / "django-best-practices"
        assert dest.is_dir()
        assert (dest / "SKILL.md").exists()


# --- update_readme ---

class TestUpdateReadme:
    def test_appends_section_to_empty_readme(self, tmp_path: Path):
        skill = _fake_skill(tmp_path)
        update_readme(tmp_path, [skill], CLAUDE_CODE)

        content = (tmp_path / "README.md").read_text()
        assert "## Agent Skills" in content
        assert skill.name in content

    def test_appends_section_to_existing_readme(self, tmp_path: Path):
        (tmp_path / "README.md").write_text("# My Project\n\nSome content.\n")
        skill = _fake_skill(tmp_path)

        update_readme(tmp_path, [skill], CLAUDE_CODE)

        content = (tmp_path / "README.md").read_text()
        assert "# My Project" in content
        assert "## Agent Skills" in content

    def test_second_run_replaces_not_duplicates(self, tmp_path: Path):
        skill = _fake_skill(tmp_path)

        update_readme(tmp_path, [skill], CLAUDE_CODE)
        update_readme(tmp_path, [skill], CLAUDE_CODE)

        content = (tmp_path / "README.md").read_text()
        assert content.count("## Agent Skills") == 1

    def test_creates_readme_if_missing(self, tmp_path: Path):
        skill = _fake_skill(tmp_path)
        update_readme(tmp_path, [skill], CLAUDE_CODE)

        assert (tmp_path / "README.md").exists()

    def test_uses_existing_lowercase_readme(self, tmp_path: Path):
        (tmp_path / "readme.md").write_text("# Hello\n")
        skill = _fake_skill(tmp_path)

        update_readme(tmp_path, [skill], CLAUDE_CODE)

        # Existing content is preserved and the section is added exactly once.
        content = (tmp_path / "readme.md").read_text()
        assert "# Hello" in content
        assert content.count("## Agent Skills") == 1

    def test_claude_code_invoke_hint(self, tmp_path: Path):
        skill = _fake_skill(tmp_path, "my-skill")
        update_readme(tmp_path, [skill], CLAUDE_CODE)

        content = (tmp_path / "README.md").read_text()
        assert "/my-skill" in content

    def test_cursor_invoke_hint(self, tmp_path: Path):
        skill = _fake_skill(tmp_path, "my-skill")
        update_readme(tmp_path, [skill], CURSOR)

        content = (tmp_path / "README.md").read_text()
        assert "@my-skill" in content
