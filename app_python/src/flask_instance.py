"""Flask app instance and shared process-level state."""

from datetime import datetime, timezone
import os

from flask import Flask

try:
    from .logging_utils import configure_json_logger
except ImportError:  # pragma: no cover - allows `python src/main.py`
    from logging_utils import configure_json_logger

app = Flask("DevOps Info Service")
START_TIME = datetime.now(timezone.utc)  # Application start time (UTC).
logger = configure_json_logger("devops_info_service")

app.logger.handlers = list(logger.handlers)
app.logger.setLevel(logger.level)
app.logger.propagate = False

logger.info(
    "application initialized",
    extra={
        "event": "startup",
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", 5000)),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
    },
)
