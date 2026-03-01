import warnings
from pathlib import Path

import pytest

from devpack.matcher import load_installed_skills, load_skills, match_skills
from devpack.models import CLAUDE_CODE, CURSOR, DetectedTechnology, Skill

STARTERPACK = Path(__file__).parent.parent / "src" / "devpack" / "starterpack"


# --- load_skills ---

def test_load_skills_returns_all_skills():
    skills = load_skills(STARTERPACK)
    assert len(skills) > 0


def test_load_skills_parses_name_and_description():
    skills = load_skills(STARTERPACK)
    for skill in skills:
        assert skill.name, f"{skill.id} is missing a name"
        assert skill.description, f"{skill.id} is missing a description"


def test_load_skills_sets_correct_path():
    skills = load_skills(STARTERPACK)
    for skill in skills:
        assert skill.path.is_dir()
        assert (skill.path / "SKILL.md").exists()


def test_load_skills_skips_dirs_without_skill_md(tmp_path: Path):
    (tmp_path / "agent-skills" / "broken-skill").mkdir(parents=True)
    # No SKILL.md inside — should be silently skipped.
    skills = load_skills(tmp_path)
    assert skills == []


def test_load_skills_skips_malformed_frontmatter(tmp_path: Path):
    skill_dir = tmp_path / "agent-skills" / "bad-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("no frontmatter here\n")
    with warnings.catch_warnings(record=True):
        skills = load_skills(tmp_path)
    assert skills == []


# --- match_skills ---

def _make_skill(id: str, tags: list[str] | None = None) -> Skill:
    return Skill(id=id, name=id, description="", path=Path("/fake"), tags=tags or [])


def _make_tech(id: str, name: str = "", is_frontend: bool = False) -> DetectedTechnology:
    return DetectedTechnology(id=id, name=name or id.title(), is_frontend=is_frontend)


class TestMatchSkillsWithRealSkills:
    def setup_method(self):
        self.all_skills = load_skills(STARTERPACK)

    def _ids(self, stack):
        return {s.id for s in match_skills(self.all_skills, stack)}

    def test_django_stack_includes_django_skills(self):
        stack = [_make_tech("python"), _make_tech("django")]
        result = self._ids(stack)
        assert "django-best-practices" in result

    def test_django_stack_excludes_react_skills(self):
        stack = [_make_tech("python"), _make_tech("django")]
        result = self._ids(stack)
        assert "react-best-practices" not in result

    def test_feature_implementation_plan_always_included(self):
        for stack in [
            [],
            [_make_tech("python"), _make_tech("django")],
            [_make_tech("react", is_frontend=True)],
        ]:
            result = self._ids(stack)
            assert "feature-implementation-plan" in result

    def test_react_stack_includes_frontend_skills(self):
        stack = [_make_tech("react", is_frontend=True), _make_tech("typescript", is_frontend=True)]
        result = self._ids(stack)
        assert "react-best-practices" in result
        assert "optimize-lighthouse-metrics" in result
        assert "accessibility-best-practices" in result

    def test_pure_django_stack_excludes_lighthouse(self):
        stack = [_make_tech("python"), _make_tech("django")]
        result = self._ids(stack)
        assert "optimize-lighthouse-metrics" not in result

    def test_empty_stack_returns_all_skills(self):
        result = match_skills(self.all_skills, [])
        assert len(result) == len(self.all_skills)


# --- load_installed_skills ---

def _install_skill(repo: Path, ide, skill_id: str, name: str = "", description: str = "") -> None:
    skill_dir = repo / ide.skill_path / skill_id
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name or skill_id}\ndescription: {description or 'A skill.'}\n---\n"
    )


class TestLoadInstalledSkills:
    def test_empty_when_no_ide_dir(self, tmp_path: Path):
        assert load_installed_skills(tmp_path, CLAUDE_CODE) == []

    def test_returns_installed_skills(self, tmp_path: Path):
        _install_skill(tmp_path, CLAUDE_CODE, "my-skill", "My Skill", "Does stuff.")
        skills = load_installed_skills(tmp_path, CLAUDE_CODE)
        assert len(skills) == 1
        assert skills[0].id == "my-skill"
        assert skills[0].name == "My Skill"
        assert skills[0].description == "Does stuff."

    def test_path_points_to_installed_copy(self, tmp_path: Path):
        _install_skill(tmp_path, CLAUDE_CODE, "my-skill")
        skills = load_installed_skills(tmp_path, CLAUDE_CODE)
        assert skills[0].path == tmp_path / CLAUDE_CODE.skill_path / "my-skill"

    def test_scoped_to_ide(self, tmp_path: Path):
        _install_skill(tmp_path, CLAUDE_CODE, "skill-a")
        _install_skill(tmp_path, CURSOR, "skill-b")
        assert {s.id for s in load_installed_skills(tmp_path, CLAUDE_CODE)} == {"skill-a"}
        assert {s.id for s in load_installed_skills(tmp_path, CURSOR)} == {"skill-b"}

    def test_skips_dirs_without_skill_md(self, tmp_path: Path):
        (tmp_path / CLAUDE_CODE.skill_path / "orphan").mkdir(parents=True)
        assert load_installed_skills(tmp_path, CLAUDE_CODE) == []

    def test_multiple_skills_returned(self, tmp_path: Path):
        for skill_id in ["alpha", "beta", "gamma"]:
            _install_skill(tmp_path, CLAUDE_CODE, skill_id)
        skills = load_installed_skills(tmp_path, CLAUDE_CODE)
        assert {s.id for s in skills} == {"alpha", "beta", "gamma"}


class TestMatchSkillsLogic:
    def test_matches_by_tech_tag(self):
        skills = [_make_skill("django-best-practices", tags=["django"])]
        stack = [_make_tech("django")]
        assert match_skills(skills, stack) == skills

    def test_matches_by_frontend_tag(self):
        skills = [_make_skill("my-skill", tags=["frontend"])]
        stack = [_make_tech("react", is_frontend=True)]
        assert match_skills(skills, stack) == skills

    def test_frontend_tag_not_matched_without_frontend_tech(self):
        skills = [_make_skill("my-skill", tags=["frontend"])]
        stack = [_make_tech("django")]
        assert match_skills(skills, stack) == []

    def test_general_tag_always_included(self):
        skills = [_make_skill("any-skill", tags=["general"])]
        stack = [_make_tech("rust")]
        assert match_skills(skills, stack) == skills

    def test_no_tags_excluded(self):
        skills = [_make_skill("ruby-style-guide")]
        stack = [_make_tech("python")]
        assert match_skills(skills, stack) == []
