import json
import tomllib
from pathlib import Path

from devpack.models import Technology


# --- Helpers ---

def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError):
        return ""


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _read_toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _package_json_deps(repo: Path) -> set[str]:
    data = _read_json(repo / "package.json")
    deps = set(data.get("dependencies", {}).keys())
    deps |= set(data.get("devDependencies", {}).keys())
    return deps


def _pyproject_deps(repo: Path) -> str:
    data = _read_toml(repo / "pyproject.toml")
    # PEP 517 / setuptools style
    deps = data.get("project", {}).get("dependencies", [])
    # Poetry style
    deps += list(data.get("tool", {}).get("poetry", {}).get("dependencies", {}).keys())
    return " ".join(deps).lower()


def _requirements_txt(repo: Path) -> str:
    return _read_text(repo / "requirements.txt")


# --- Technology definitions ---

TECHNOLOGIES: list[Technology] = [
    Technology(
        id="python",
        name="Python",
        indicators=[
            lambda r: (r / "pyproject.toml").exists(),
            lambda r: (r / "requirements.txt").exists(),
            lambda r: (r / "setup.py").exists(),
            lambda r: (r / "setup.cfg").exists(),
            lambda r: (r / "Pipfile").exists(),
        ],
    ),
    Technology(
        id="django",
        name="Django",
        indicators=[
            lambda r: "django" in _requirements_txt(r),
            lambda r: "django" in _pyproject_deps(r),
            lambda r: (r / "manage.py").exists(),
        ],
    ),
    Technology(
        id="fastapi",
        name="FastAPI",
        indicators=[
            lambda r: "fastapi" in _requirements_txt(r),
            lambda r: "fastapi" in _pyproject_deps(r),
        ],
    ),
    Technology(
        id="flask",
        name="Flask",
        indicators=[
            lambda r: "flask" in _requirements_txt(r),
            lambda r: "flask" in _pyproject_deps(r),
        ],
    ),
    Technology(
        id="javascript",
        name="JavaScript",
        is_frontend=True,
        indicators=[
            lambda r: (r / "package.json").exists(),
        ],
    ),
    Technology(
        id="typescript",
        name="TypeScript",
        is_frontend=True,
        indicators=[
            lambda r: (r / "tsconfig.json").exists(),
            lambda r: "typescript" in _package_json_deps(r),
        ],
    ),
    Technology(
        id="react",
        name="React",
        is_frontend=True,
        indicators=[
            lambda r: "react" in _package_json_deps(r),
        ],
    ),
    Technology(
        id="vue",
        name="Vue",
        is_frontend=True,
        indicators=[
            lambda r: "vue" in _package_json_deps(r),
        ],
    ),
    Technology(
        id="nextjs",
        name="Next.js",
        is_frontend=True,
        indicators=[
            lambda r: "next" in _package_json_deps(r),
        ],
    ),
    Technology(
        id="ruby",
        name="Ruby",
        indicators=[
            lambda r: (r / "Gemfile").exists(),
        ],
    ),
    Technology(
        id="rails",
        name="Ruby on Rails",
        indicators=[
            lambda r: "rails" in _read_text(r / "Gemfile"),
        ],
    ),
    Technology(
        id="go",
        name="Go",
        indicators=[
            lambda r: (r / "go.mod").exists(),
        ],
    ),
    Technology(
        id="rust",
        name="Rust",
        indicators=[
            lambda r: (r / "Cargo.toml").exists(),
        ],
    ),
    Technology(
        id="postgres",
        name="PostgreSQL",
        indicators=[
            lambda r: "psycopg" in _requirements_txt(r),
            lambda r: "psycopg" in _pyproject_deps(r),
            lambda r: "postgres" in _read_text(r / "docker-compose.yml"),
            lambda r: "postgres" in _read_text(r / "docker-compose.yaml"),
        ],
    ),
    Technology(
        id="docker",
        name="Docker",
        indicators=[
            lambda r: (r / "Dockerfile").exists(),
            lambda r: (r / "docker-compose.yml").exists(),
            lambda r: (r / "docker-compose.yaml").exists(),
        ],
    ),
]
