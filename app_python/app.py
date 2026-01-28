"""
DevOps Info Service
Main application module
"""

__version__ = "1.0.0"

# Basics
import os
from datetime import datetime, timezone
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Metadata gathering
from multiprocessing import cpu_count
import platform
import inspect

# Web
import socket

from flask import Flask, jsonify, request

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

app = Flask(__name__)


def get_service_info() -> dict[str, str]:
    """Collect info about service"""
    return {
        "name": "devops-info-service",
        "version": __version__,
        "description": "DevOps course info service",
        "framework": "Flask",
    }


def get_platform_info() -> dict[str, str | int]:
    """Collect system information"""

    def _platform_version() -> str:
        """Return a human-friendly OS version string."""
        match (platform.system().lower()):
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


def get_uptime():
    """Return uptime in seconds and a simple human string."""
    delta = datetime.now(tz=timezone.utc) - START_TIME
    up_seconds = int(delta.total_seconds())
    up_hours = up_seconds // 3600
    up_minutes = (up_seconds % 3600) // 60
    return {
        "seconds": up_seconds,
        "human": f"{up_hours} hours, {up_minutes} minutes",
    }


def get_runtime():
    """Return current runtime metadata (uptime + UTC timestamp)."""
    up = get_uptime()
    return {
        "uptime_seconds": up["seconds"],
        "uptime_human": up["human"],
        "current_time": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timezone": "UTC",
    }


def get_request_info(request):
    """Return basic request metadata for debugging/telemetry."""
    return {
        "client_ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent"),
        "method": request.method,
        "path": request.path,
    }


def list_routes() -> list[dict[str, str]]:
    """Return a flat list of route + method + description."""
    out: list[dict[str, str]] = []

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: (r.rule, r.endpoint)):
        # Skip Flask's built-in static handler
        if rule.endpoint == "static":
            continue

        view = app.view_functions.get(rule.endpoint)

        # Description is pulled from docstring's brief (first line)
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
    """Service information"""
    logger.debug(f"Request: {request.method} {request.path}")
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
    """Health check"""
    logger.debug(f"Request: {request.method} {request.path}")
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": get_uptime()["seconds"],
        }
    )


@app.errorhandler(404)
def not_found(error):
    """Return a JSON 404 payload."""
    logger.debug(f"Request: {request.method} {request.path}")
    return jsonify({"error": "Not Found", "message": "Endpoint does not exist"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Return a JSON 500 payload."""
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


START_TIME = datetime.now(timezone.utc)  # Application start time (UTC).
logger.info("Application starting...")

# TODO use WSGI in production.
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
