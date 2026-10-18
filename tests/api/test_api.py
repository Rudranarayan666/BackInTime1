import json
from pathlib import Path

from fastapi.testclient import TestClient

from backintime.api.app import create_app
from backintime.core.config import ConfigStore


def _client(config_path: Path) -> TestClient:
    return TestClient(create_app(config_store=ConfigStore(config_path)))


def test_health_returns_version_and_request_id(tmp_path: Path) -> None:
    response = _client(tmp_path / "config.json").get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-request-id"]


def test_system_info_reports_runtime_capabilities(tmp_path: Path) -> None:
    response = _client(tmp_path / "config.json").get("/api/v1/system/info")

    assert response.status_code == 200
    assert set(response.json()) == {"platform", "python_version", "rsync_available"}


def test_profiles_are_loaded_from_core_config_store(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "version": 1,
                "profiles": [
                    {
                        "profile_id": "work",
                        "name": "Work",
                        "sources": [str(tmp_path / "source")],
                        "target": str(tmp_path / "target"),
                        "excludes": ["*.tmp"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    response = _client(config_path).get("/api/v1/profiles")

    assert response.status_code == 200
    assert response.json() == {
        "profiles": [
            {
                "profile_id": "work",
                "name": "Work",
                "sources": [str(tmp_path / "source")],
                "target": str(tmp_path / "target"),
                "excludes": ["*.tmp"],
            }
        ]
    }


def test_profile_detail_returns_configured_profile(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "version": 1,
                "profiles": [
                    {
                        "profile_id": "work",
                        "name": "Work",
                        "sources": [str(tmp_path / "source")],
                        "target": str(tmp_path / "target"),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    response = _client(config_path).get("/api/v1/profiles/work")

    assert response.status_code == 200
    assert response.json() == {
        "profile_id": "work",
        "name": "Work",
        "sources": [str(tmp_path / "source")],
        "target": str(tmp_path / "target"),
        "excludes": [],
    }
    assert response.headers["x-request-id"]


def test_profile_detail_returns_404_for_unknown_profile(tmp_path: Path) -> None:
    response = _client(tmp_path / "missing.json").get("/api/v1/profiles/not-configured")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROFILE_NOT_FOUND"
    assert response.headers["x-request-id"] == response.json()["error"]["request_id"]


def test_invalid_config_returns_structured_error(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{broken", encoding="utf-8")

    response = _client(config_path).get("/api/v1/profiles")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "CONFIGURATION_INVALID"
    assert response.json()["error"]["message"] == (
        "The application configuration could not be loaded or validated."
    )
    assert str(config_path) not in response.text
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_semantically_invalid_config_returns_structured_error(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "version": 1,
                "profiles": [
                    {
                        "profile_id": "work",
                        "name": "Work",
                        "sources": ["relative/source"],
                        "target": str(tmp_path / "target"),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    response = _client(config_path).get("/api/v1/profiles")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "CONFIGURATION_INVALID"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]
    assert "relative/source" not in response.text


def test_invalid_profile_id_is_not_interpreted_as_a_path(tmp_path: Path) -> None:
    response = _client(tmp_path / "missing.json").get("/api/v1/profiles/%2e%2e%2fsecrets")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
