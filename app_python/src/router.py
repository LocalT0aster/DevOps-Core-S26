"""
Route handlers and response helpers.
"""

from datetime import datetime, timezone
import inspect
from multiprocessing import cpu_count
import platform
import socket

from flask import jsonify, request

try:
    from .flask_instance import START_TIME, app, logger
    from .metrics import (
        DEVOPS_INFO_SYSTEM_INFO_DURATION_SECONDS,
        generate_metrics_response,
        record_endpoint_call,
    )
except ImportError:  # pragma: no cover - allows `python src/main.py`
    from flask_instance import START_TIME, app, logger
    from metrics import (
        DEVOPS_INFO_SYSTEM_INFO_DURATION_SECONDS,
        generate_metrics_response,
        record_endpoint_call,
    )

__version__ = "1.10.0"


def get_service_info() -> dict[str, str]:
    """Collect info about service."""
    return {
        "name": "devops-info-service",
        "version": __version__,
        "description": "DevOps course info service",
        "framework": "Flask",
    }


@DEVOPS_INFO_SYSTEM_INFO_DURATION_SECONDS.time()
def get_platform_info() -> dict[str, str | int]:
    """Collect system information."""

    def _platform_version() -> str:
        """Return a human-friendly OS version string."""
        match platform.system().lower():
            case "linux":
                return platform.freedesktop_os_release()["PRETTY_NAME"]
            case "windows":
                return f"{platform.system()} {platform.win32_ver()[1]}"
            case _:
                return platform.version()

    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_version": _platform_version(),
        "architecture": platform.machine(),
        "cpu_count": cpu_count(),
        "python_version": platform.python_version(),
    }


def get_uptime() -> dict[str, str | int]:
    """Return uptime in seconds and a simple human string."""
    delta = datetime.now(tz=timezone.utc) - START_TIME
    up_seconds = int(delta.total_seconds())
    up_hours = up_seconds // 3600
    up_minutes = (up_seconds % 3600) // 60
    return {
        "seconds": up_seconds,
        "human": f"{up_hours} hours, {up_minutes} minutes",
    }


def get_runtime() -> dict[str, str | int]:
    """Return current runtime metadata (uptime + UTC timestamp)."""
    up = get_uptime()
    return {
        "uptime_seconds": up["seconds"],
        "uptime_human": up["human"],
        "current_time": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timezone": "UTC",
    }


def get_request_info(req) -> dict[str, str | None]:
    """Return basic request metadata for debugging/telemetry."""
    return {
        "client_ip": req.remote_addr,
        "user_agent": req.headers.get("User-Agent"),
        "method": req.method,
        "path": req.path,
    }


def get_request_log_context(req, status_code: int) -> dict[str, str | int | None]:
    """Return request metadata suitable for structured logs."""
    context = get_request_info(req)
    context["status_code"] = status_code
    return context


def list_routes() -> list[dict[str, str]]:
    """Return a flat list of route + method + description."""
    out: list[dict[str, str]] = []

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: (r.rule, r.endpoint)):
        if rule.endpoint == "static":
            continue

        view = app.view_functions.get(rule.endpoint)

        desc = ""
        if view is not None:
            desc = inspect.getdoc(view) or ""
            desc = desc.splitlines()[0].strip() or ""

        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            out.append(
                {
                    "path": rule.rule,
                    "method": method,
                    "description": desc,
                }
            )
    return out


@app.route("/")
def index():
    """Service information."""
    record_endpoint_call("/")
    return jsonify(
        {
            "service": get_service_info(),
            "system": get_platform_info(),
            "runtime": get_uptime(),
            "request": get_request_info(request),
            "endpoints": list_routes(),
        }
    )


@app.route("/health")
def health():
    """Health check."""
    record_endpoint_call("/health")
    return _status_response("healthy")


@app.route("/ready")
def readiness():
    """Readiness check."""
    record_endpoint_call("/ready")
    return _status_response("ready")


def _status_response(status: str):
    """Return a shared JSON payload for health-style endpoints."""
    return jsonify(
        {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": get_uptime()["seconds"],
        }
    )


@app.route("/metrics")
def metrics():
    """Prometheus metrics."""
    record_endpoint_call("/metrics")
    return generate_metrics_response()


@app.errorhandler(404)
def not_found(error):  # noqa: ARG001
    """Return a JSON 404 payload."""
    logger.warning(
        "request returned not found",
        extra=get_request_log_context(request, status_code=404),
    )
    return jsonify({"error": "Not Found", "message": "Endpoint does not exist"}), 404


@app.errorhandler(500)
def internal_error(error):  # noqa: ARG001
    """Return a JSON 500 payload."""
    original_error = getattr(error, "original_exception", None) or error
    logger.error(
        "request failed",
        extra={
            **get_request_log_context(request, status_code=500),
            "error_type": type(original_error).__name__,
            "error": str(original_error),
        },
    )
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )
