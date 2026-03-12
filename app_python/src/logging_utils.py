"""Shared JSON logging helpers for the Python service."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import os
import sys
from typing import Any

_RESERVED_RECORD_FIELDS = frozenset(
    vars(logging.LogRecord("", logging.INFO, "", 0, "", (), None)).keys()
) | {"message", "asctime"}


def _to_jsonable(value: Any) -> Any:
    """Convert values into JSON-safe representations."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(item) for item in value]
    return str(value)


class JSONFormatter(logging.Formatter):
    """Format log records as a single JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key in _RESERVED_RECORD_FIELDS or key.startswith("_"):
                continue
            payload[key] = _to_jsonable(value)

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(payload, separators=(",", ":"))


def get_log_level() -> int:
    """Return the configured application log level."""
    raw_level = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, raw_level, logging.INFO)


def configure_json_logger(name: str) -> logging.Logger:
    """Create a stdout logger that emits JSON records."""
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(get_log_level())
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger
