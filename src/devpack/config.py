import os
import re
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

_CONFIG_DIR = Path.home() / ".config" / "devpack"
_CONFIG_ENV = _CONFIG_DIR / ".env"


def load_api_key() -> str | None:
    """Load ANTHROPIC_API_KEY using a priority chain:
    1. Already in the process environment.
    2. .env in cwd             (project-specific override).
    3. ~/.config/devpack/.env  (user-global fallback).
    """
    if key := os.getenv("ANTHROPIC_API_KEY"):
        return key

    load_dotenv(find_dotenv(usecwd=True), override=False)
    if key := os.getenv("ANTHROPIC_API_KEY"):
        return key

    if _CONFIG_ENV.exists():
        load_dotenv(_CONFIG_ENV, override=False)
    return os.getenv("ANTHROPIC_API_KEY")


def save_to_config_file(key: str) -> Path:
    """Save API key to ~/.config/devpack/.env with secure permissions."""
    _CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    _CONFIG_ENV.write_text(f"ANTHROPIC_API_KEY={key}\n")
    _CONFIG_ENV.chmod(0o600)
    return _CONFIG_ENV


def api_key_source() -> str | None:
    """Return a human-readable description of where ANTHROPIC_API_KEY is configured.

    Checks sources in the same priority order as load_api_key(), but without
    mutating the process environment. Returns None if the key is not found anywhere.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return "environment variable"

    def _has_key(path: Path) -> bool:
        return bool(
            re.search(r"^\s*ANTHROPIC_API_KEY\s*=", path.read_text(), re.MULTILINE)
        )

    local_env = find_dotenv(usecwd=True)
    if local_env and _has_key(Path(local_env)):
        return f".env ({local_env})"

    if _CONFIG_ENV.exists() and _has_key(_CONFIG_ENV):
        return str(_CONFIG_ENV)

    return None


def append_to_shell_rc(key: str, rc_file: Path) -> None:
    """Append an export statement for the API key to a shell rc file."""
    with rc_file.open("a") as f:
        f.write(f'\nexport ANTHROPIC_API_KEY="{key}"\n')
