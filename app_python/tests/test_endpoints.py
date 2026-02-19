"""Unit tests for HTTP endpoints and error handling."""

from datetime import datetime

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
    assert ("GET", "/health") in route_index


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
