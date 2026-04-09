"""Unit tests for HTTP endpoints and error handling."""

from datetime import datetime
from unittest.mock import Mock

import src.router as router


def _raise_runtime_error() -> None:
    raise RuntimeError("simulated failure")


def test_index_returns_expected_json_structure_and_types(client):
    """GET / should return the expected nested schema with stable field types."""
    response = client.get(
        "/",
        headers={"User-Agent": "pytest-suite/1.0"},
        environ_overrides={"REMOTE_ADDR": "203.0.113.7"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None

    assert {"service", "system", "runtime", "request", "endpoints"} <= payload.keys()

    service = payload["service"]
    assert service["name"] == "devops-info-service"
    assert service["framework"] == "Flask"
    assert isinstance(service["version"], str)
    assert isinstance(service["description"], str)

    system = payload["system"]
    assert isinstance(system["hostname"], str)
    assert system["hostname"]
    assert isinstance(system["platform"], str)
    assert isinstance(system["platform_version"], str)
    assert isinstance(system["architecture"], str)
    assert isinstance(system["cpu_count"], int)
    assert system["cpu_count"] >= 1
    assert isinstance(system["python_version"], str)

    runtime = payload["runtime"]
    assert isinstance(runtime["seconds"], int)
    assert runtime["seconds"] >= 0
    assert isinstance(runtime["human"], str)

    request = payload["request"]
    assert request["client_ip"] == "203.0.113.7"
    assert request["user_agent"] == "pytest-suite/1.0"
    assert request["method"] == "GET"
    assert request["path"] == "/"

    endpoints = payload["endpoints"]
    assert isinstance(endpoints, list)
    assert endpoints
    for endpoint in endpoints:
        assert {"path", "method", "description"} <= endpoint.keys()
        assert isinstance(endpoint["path"], str)
        assert isinstance(endpoint["method"], str)
        assert isinstance(endpoint["description"], str)

    route_index = {(endpoint["method"], endpoint["path"]) for endpoint in endpoints}
    assert ("GET", "/") in route_index
    assert ("GET", "/visits") in route_index
    assert ("GET", "/health") in route_index
    assert ("GET", "/ready") in route_index
    assert ("GET", "/metrics") in route_index


def test_visits_defaults_to_zero_when_counter_file_is_missing(client, tmp_path, monkeypatch):
    """GET /visits should bootstrap from zero when the counter file is absent."""
    visits_file = tmp_path / "visits"
    monkeypatch.setattr(router, "VISITS_FILE", visits_file)

    response = client.get("/visits")

    assert response.status_code == 200
    assert response.get_json() == {"visits": 0}
    assert not visits_file.exists()


def test_index_increments_and_persists_visits_count(client, tmp_path, monkeypatch):
    """GET / should increment the counter and persist the new value."""
    visits_file = tmp_path / "visits"
    monkeypatch.setattr(router, "VISITS_FILE", visits_file)

    first_response = client.get("/")
    second_response = client.get("/")
    visits_response = client.get("/visits")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert visits_response.status_code == 200
    assert visits_response.get_json() == {"visits": 2}
    assert visits_file.read_text(encoding="utf-8") == "2\n"


def test_visits_returns_persisted_count(client, tmp_path, monkeypatch):
    """GET /visits should return the current persisted counter value."""
    visits_file = tmp_path / "visits"
    visits_file.write_text("7\n", encoding="utf-8")
    monkeypatch.setattr(router, "VISITS_FILE", visits_file)

    response = client.get("/visits")

    assert response.status_code == 200
    assert response.get_json() == {"visits": 7}


def test_visits_falls_back_to_zero_when_counter_file_is_malformed(
    client,
    tmp_path,
    monkeypatch,
):
    """GET /visits should warn and recover when the counter file is malformed."""
    visits_file = tmp_path / "visits"
    visits_file.write_text("definitely-not-an-integer\n", encoding="utf-8")
    warning_mock = Mock()
    monkeypatch.setattr(router, "VISITS_FILE", visits_file)
    monkeypatch.setattr(router.logger, "warning", warning_mock)

    response = client.get("/visits")

    assert response.status_code == 200
    assert response.get_json() == {"visits": 0}
    warning_mock.assert_called()


def test_health_returns_expected_json_structure_and_types(client):
    """GET /health should report healthy status and typed runtime metadata."""
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None

    assert {"status", "timestamp", "uptime_seconds"} <= payload.keys()
    assert payload["status"] == "healthy"
    assert isinstance(payload["uptime_seconds"], int)
    assert payload["uptime_seconds"] >= 0

    parsed_timestamp = datetime.fromisoformat(payload["timestamp"])
    assert parsed_timestamp.tzinfo is not None


def test_ready_returns_expected_json_structure_and_types(client):
    """GET /ready should report ready status and typed runtime metadata."""
    response = client.get("/ready")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None

    assert {"status", "timestamp", "uptime_seconds"} <= payload.keys()
    assert payload["status"] == "ready"
    assert isinstance(payload["uptime_seconds"], int)
    assert payload["uptime_seconds"] >= 0

    parsed_timestamp = datetime.fromisoformat(payload["timestamp"])
    assert parsed_timestamp.tzinfo is not None


def test_unknown_endpoint_returns_json_404(client):
    """Unknown routes should be handled by JSON 404 error handler."""
    response = client.get("/definitely-does-not-exist")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Not Found",
        "message": "Endpoint does not exist",
    }


def test_index_returns_json_500_when_platform_probe_fails(client, monkeypatch):
    """GET / should return JSON 500 when an internal helper crashes."""
    monkeypatch.setattr(router, "get_platform_info", _raise_runtime_error)

    response = client.get("/")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
    }


def test_health_returns_json_500_when_uptime_probe_fails(client, monkeypatch):
    """GET /health should return JSON 500 when uptime collection crashes."""
    monkeypatch.setattr(router, "get_uptime", _raise_runtime_error)

    response = client.get("/health")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
    }


def test_ready_returns_json_500_when_uptime_probe_fails(client, monkeypatch):
    """GET /ready should return JSON 500 when uptime collection crashes."""
    monkeypatch.setattr(router, "get_uptime", _raise_runtime_error)

    response = client.get("/ready")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
    }
