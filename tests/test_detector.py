import json
from pathlib import Path

import pytest

from devpack.detector import detect_stack

FIXTURES = Path(__file__).parent / "fixtures"


def tech_ids(repo_path: Path) -> set[str]:
    return {t.id for t in detect_stack(repo_path)}


# --- Fixture-based tests ---

def test_django_repo_detects_python_and_django():
    result = tech_ids(FIXTURES / "django_repo")
    assert "python" in result
    assert "django" in result


def test_django_repo_detects_postgres():
    result = tech_ids(FIXTURES / "django_repo")
    assert "postgres" in result


def test_react_repo_detects_react_and_typescript():
    result = tech_ids(FIXTURES / "react_repo")
    assert "react" in result
    assert "typescript" in result
    assert "javascript" in result


def test_react_repo_does_not_detect_django():
    result = tech_ids(FIXTURES / "react_repo")
    assert "django" not in result


def test_node_repo_detects_typescript():
    result = tech_ids(FIXTURES / "node_repo")
    assert "typescript" in result
    assert "javascript" in result


def test_empty_repo_detects_nothing():
    result = tech_ids(FIXTURES / "empty_repo")
    assert result == set()


# --- tmp_path inline fixture tests ---

def test_detects_fastapi_from_requirements(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("fastapi>=0.100\nuvicorn\n")
    result = tech_ids(tmp_path)
    assert "fastapi" in result
    assert "python" in result


def test_detects_django_from_pyproject_toml(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["Django>=4.2", "psycopg2-binary"]\n'
    )
    result = tech_ids(tmp_path)
    assert "django" in result
    assert "postgres" in result


def test_detects_nextjs(tmp_path: Path):
    pkg = {"dependencies": {"next": "14.0.0", "react": "18.0.0"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    result = tech_ids(tmp_path)
    assert "nextjs" in result
    assert "react" in result


def test_detects_docker(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.13\n")
    result = tech_ids(tmp_path)
    assert "docker" in result


def test_detects_go(tmp_path: Path):
    (tmp_path / "go.mod").write_text("module example.com/myapp\n\ngo 1.21\n")
    result = tech_ids(tmp_path)
    assert "go" in result


def test_detects_rust(tmp_path: Path):
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "myapp"\nversion = "0.1.0"\n')
    result = tech_ids(tmp_path)
    assert "rust" in result
