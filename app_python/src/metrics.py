"""Prometheus metrics and Flask request instrumentation."""

from time import perf_counter

from flask import Response, g, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

try:
    from .flask_instance import app
except ImportError:  # pragma: no cover - allows `python src/main.py`
    from flask_instance import app

METRICS_REGISTRY = CollectorRegistry()

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the service.",
    ["method", "endpoint", "status_code"],
    registry=METRICS_REGISTRY,
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "endpoint", "status_code"],
    registry=METRICS_REGISTRY,
)
HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed.",
    ["method", "endpoint"],
    registry=METRICS_REGISTRY,
)
DEVOPS_INFO_ENDPOINT_CALLS_TOTAL = Counter(
    "devops_info_endpoint_calls_total",
    "Total calls to application endpoints.",
    ["endpoint"],
    registry=METRICS_REGISTRY,
)
DEVOPS_INFO_SYSTEM_INFO_DURATION_SECONDS = Histogram(
    "devops_info_system_info_duration_seconds",
    "Time spent collecting system information.",
    registry=METRICS_REGISTRY,
)


def normalize_endpoint_label() -> str:
    """Return a low-cardinality endpoint label for the current request."""
    rule = getattr(request, "url_rule", None)
    if rule is not None:
        return rule.rule
    return "unmatched"


def record_endpoint_call(endpoint: str) -> None:
    """Increment the app-specific endpoint usage counter."""
    DEVOPS_INFO_ENDPOINT_CALLS_TOTAL.labels(endpoint=endpoint).inc()


def generate_metrics_response() -> Response:
    """Return the current Prometheus exposition payload."""
    return Response(
        generate_latest(METRICS_REGISTRY),
        content_type=CONTENT_TYPE_LATEST,
    )


@app.before_request
def start_http_request_metrics() -> None:
    """Capture request start time and increase the in-flight gauge."""
    endpoint = normalize_endpoint_label()
    g.metrics_method = request.method
    g.metrics_endpoint = endpoint
    g.metrics_start_time = perf_counter()
    g.metrics_in_progress = True
    HTTP_REQUESTS_IN_PROGRESS.labels(
        method=request.method,
        endpoint=endpoint,
    ).inc()


@app.after_request
def record_http_request_metrics(response: Response) -> Response:
    """Persist request counter and latency observations."""
    method = getattr(g, "metrics_method", request.method)
    endpoint = getattr(g, "metrics_endpoint", normalize_endpoint_label())
    start_time = getattr(g, "metrics_start_time", None)
    if start_time is None:
        return response

    labels = {
        "method": method,
        "endpoint": endpoint,
        "status_code": str(response.status_code),
    }
    HTTP_REQUESTS_TOTAL.labels(**labels).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(**labels).observe(
        perf_counter() - start_time
    )
    return response


@app.teardown_request
def finish_http_request_metrics(error: BaseException | None) -> None:  # noqa: ARG001
    """Decrease the in-flight gauge after the request finishes."""
    if not getattr(g, "metrics_in_progress", False):
        return

    HTTP_REQUESTS_IN_PROGRESS.labels(
        method=g.metrics_method,
        endpoint=g.metrics_endpoint,
    ).dec()
    g.metrics_in_progress = False
