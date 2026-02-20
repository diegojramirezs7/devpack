from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from devpack.detector import detect_stack
from devpack.models import DetectedTechnology, StackDetectionResult

FIXTURES = Path(__file__).parent / "fixtures"


def _make_result(*tech_ids: str) -> StackDetectionResult:
    technologies = [
        DetectedTechnology(id=tid, name=tid.title(), is_frontend=tid in {"react", "javascript", "typescript"})
        for tid in tech_ids
    ]
    return StackDetectionResult(technologies=technologies, summary="Test stack.")


# --- Unit tests (mocked) ---

@patch("devpack.detector.detect_tech_stack", new_callable=AsyncMock)
def test_detect_stack_returns_technologies(mock_detect, tmp_path):
    mock_detect.return_value = _make_result("python", "django")
    result = detect_stack(tmp_path)
    assert {t.id for t in result} == {"python", "django"}


@patch("devpack.detector.detect_tech_stack", new_callable=AsyncMock)
def test_detect_stack_empty_result(mock_detect, tmp_path):
    mock_detect.return_value = _make_result()
    result = detect_stack(tmp_path)
    assert result == []


@patch("devpack.detector.detect_tech_stack", new_callable=AsyncMock)
def test_detect_stack_passes_repo_path(mock_detect, tmp_path):
    mock_detect.return_value = _make_result("python")
    detect_stack(tmp_path)
    mock_detect.assert_called_once_with(tmp_path)


@patch("devpack.detector.detect_tech_stack", new_callable=AsyncMock)
def test_detect_stack_returns_detected_technology_instances(mock_detect, tmp_path):
    mock_detect.return_value = _make_result("react")
    result = detect_stack(tmp_path)
    assert all(isinstance(t, DetectedTechnology) for t in result)


@patch("devpack.detector.detect_tech_stack", new_callable=AsyncMock)
def test_detect_stack_frontend_flag_preserved(mock_detect, tmp_path):
    mock_detect.return_value = _make_result("react", "python")
    result = detect_stack(tmp_path)
    by_id = {t.id: t for t in result}
    assert by_id["react"].is_frontend is True
    assert by_id["python"].is_frontend is False


# --- Integration tests (require ANTHROPIC_API_KEY; skipped in CI) ---

@pytest.mark.integration
def test_django_repo_detects_python_and_django():
    result = {t.id for t in detect_stack(FIXTURES / "django_repo")}
    assert "python" in result
    assert "django" in result


@pytest.mark.integration
def test_django_repo_detects_postgres():
    result = {t.id for t in detect_stack(FIXTURES / "django_repo")}
    assert "postgres" in result


@pytest.mark.integration
def test_react_repo_detects_react_and_typescript():
    result = {t.id for t in detect_stack(FIXTURES / "react_repo")}
    assert "react" in result
    assert "typescript" in result


@pytest.mark.integration
def test_react_repo_does_not_detect_django():
    result = {t.id for t in detect_stack(FIXTURES / "react_repo")}
    assert "django" not in result


@pytest.mark.integration
def test_node_repo_detects_typescript():
    result = {t.id for t in detect_stack(FIXTURES / "node_repo")}
    assert "typescript" in result


@pytest.mark.integration
def test_empty_repo_detects_nothing():
    result = detect_stack(FIXTURES / "empty_repo")
    assert result == []
