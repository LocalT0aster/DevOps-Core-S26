"""
DevOps Info Service
Main application module
"""

__version__ = "1.0.0"


from pydoc import describe
from flask import Flask, jsonify, request
from datetime import datetime, timezone
from multiprocessing import cpu_count
import time
import platform
import socket
import os
import logging
import inspect

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))


def get_service_info() -> dict[str, str]:
    """Collect info about service"""
    return {
        "name": "devops-info-service",
        "version": __version__,
        "description": "DevOps course info service",
        "framework": "Flask",
    }


def get_system_info() -> dict[str, str | int]:
    """Collect system information"""

    def _platform_version() -> str:
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
    """Get uptime info"""
    delta = datetime.now(tz=timezone.utc) - START_TIME
    up_seconds = int(delta.total_seconds())
    up_hours = up_seconds // 3600
    up_minutes = (up_seconds % 3600) // 60
    return {
        "seconds": up_seconds,
        "human": f"{up_hours} hours, {up_minutes} minutes",
    }


def get_runtime():
    up = get_uptime()
    return {
        "uptime_seconds": up["seconds"],
        "uptime_human": up["human"],
        "current_time": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timezone": "UTC",
    }


def get_request_info(request):
    """Returns request info"""
    return {
        "client_ip": request.remote_addr,  # Client IP
        "user_agent": request.headers.get("User-Agent"),  # User agent
        "method": request.method,  # HTTP method
        "path": request.path,  # Request path
    }


def list_routes() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: (r.rule, r.endpoint)):
        # Skip Flask's built-in static handler
        if rule.endpoint == "static":
            continue

        view = app.view_functions.get(rule.endpoint)

        # Description strategy: custom attribute first, otherwise docstring
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
            "system": get_system_info(),
            "runtime": get_uptime(),
            "request": get_request_info(request),
            "endpoints": list_routes(),
        }
    )


@app.route("/health")
def health():
    """Health check"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": get_uptime()["seconds"],
        }
    )


@app.errorhandler(404)
def not_found(error):
    logger.debug(f"Request: {request.method} {request.path}")
    return jsonify({"error": "Not Found", "message": "Endpoint does not exist"}), 404


@app.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


START_TIME = datetime.now(timezone.utc)  # Application start time
logger.info("Application starting...")

app.run(host=HOST, port=PORT)
