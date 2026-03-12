"""Unit tests for JSON logging helpers."""

import json
import logging

from src.logging_utils import JSONFormatter


def test_json_formatter_serializes_message_and_extra_fields():
    """Formatter should emit a JSON line with standard and custom fields."""
    record = logging.LogRecord(
        name="devops_info_service",
        level=logging.INFO,
        pathname=__file__,
        lineno=12,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    record.client_ip = "203.0.113.7"
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200

    payload = json.loads(JSONFormatter().format(record))

    assert payload["logger"] == "devops_info_service"
    assert payload["level"] == "INFO"
    assert payload["message"] == "hello world"
    assert payload["client_ip"] == "203.0.113.7"
    assert payload["method"] == "GET"
    assert payload["path"] == "/health"
    assert payload["status_code"] == 200
    assert payload["timestamp"].endswith("Z")
