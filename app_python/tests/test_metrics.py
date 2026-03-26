"""Tests for Prometheus metrics exposure and labels."""

from collections.abc import Mapping

from prometheus_client.parser import text_string_to_metric_families

import src.router as router


def _raise_runtime_error() -> None:
    raise RuntimeError("simulated failure")


def _metric_value(
    metrics_text: str,
    sample_name: str,
    labels: Mapping[str, str] | None = None,
) -> float | None:
    expected_labels = labels or {}

    for family in text_string_to_metric_families(metrics_text):
        for sample in family.samples:
            if sample.name != sample_name:
                continue
            if all(
                sample.labels.get(key) == value
                for key, value in expected_labels.items()
            ):
                return float(sample.value)
    return None


def _metrics_text(client) -> str:
    response = client.get("/metrics")
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_metrics_endpoint_exposes_http_and_application_metrics(client):
    """Metrics endpoint should expose HTTP RED data and app-specific metrics."""
    client.get("/")
    client.get("/health")
    client.get("/does-not-exist")

    response = client.get("/metrics")
    metrics_text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.content_type.startswith("text/plain")

    root_total = _metric_value(
        metrics_text,
        "http_requests_total",
        {"method": "GET", "endpoint": "/", "status_code": "200"},
    )
    health_total = _metric_value(
        metrics_text,
        "http_requests_total",
        {"method": "GET", "endpoint": "/health", "status_code": "200"},
    )
    unmatched_total = _metric_value(
        metrics_text,
        "http_requests_total",
        {"method": "GET", "endpoint": "unmatched", "status_code": "404"},
    )
    root_duration_count = _metric_value(
        metrics_text,
        "http_request_duration_seconds_count",
        {"method": "GET", "endpoint": "/", "status_code": "200"},
    )
    root_in_progress = _metric_value(
        metrics_text,
        "http_requests_in_progress",
        {"method": "GET", "endpoint": "/"},
    )
    endpoint_calls = _metric_value(
        metrics_text,
        "devops_info_endpoint_calls_total",
        {"endpoint": "/"},
    )
    system_info_count = _metric_value(
        metrics_text,
        "devops_info_system_info_duration_seconds_count",
    )

    assert root_total is not None and root_total >= 1.0
    assert health_total is not None and health_total >= 1.0
    assert unmatched_total is not None and unmatched_total >= 1.0
    assert root_duration_count is not None and root_duration_count >= 1.0
    assert root_in_progress == 0.0
    assert endpoint_calls is not None and endpoint_calls >= 1.0
    assert system_info_count is not None and system_info_count >= 1.0


def test_metrics_count_internal_server_errors_with_status_labels(client, monkeypatch):
    """Failed requests should still be counted with a 500 status code label."""
    labels = {"method": "GET", "endpoint": "/", "status_code": "500"}
    before = _metric_value(_metrics_text(client), "http_requests_total", labels) or 0.0

    monkeypatch.setattr(router, "get_platform_info", _raise_runtime_error)

    response = client.get("/")
    after = _metric_value(_metrics_text(client), "http_requests_total", labels)

    assert response.status_code == 500
    assert after == before + 1.0
