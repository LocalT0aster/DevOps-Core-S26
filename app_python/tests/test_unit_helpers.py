"""Unit tests for helper functions and app entrypoint behavior."""

from datetime import datetime
from unittest.mock import Mock

from flask import request

from src.flask_instance import app
import src.main as main
import src.router as router


def test_run_calls_flask_app_with_configured_host_port_debug(monkeypatch):
    """main.run should log startup and pass module config into app.run."""
    run_mock = Mock()
    info_mock = Mock()

    monkeypatch.setattr(main, "HOST", "127.0.0.1")
    monkeypatch.setattr(main, "PORT", 5050)
    monkeypatch.setattr(main, "DEBUG", True)
    monkeypatch.setattr(main.app, "run", run_mock)
    monkeypatch.setattr(main.logger, "info", info_mock)

    main.run()

    info_mock.assert_called_once_with("Application starting...")
    run_mock.assert_called_once_with(host="127.0.0.1", port=5050, debug=True)


def test_get_runtime_maps_uptime_payload(monkeypatch):
    """get_runtime should map uptime fields and produce UTC timestamp text."""
    monkeypatch.setattr(
        router,
        "get_uptime",
        lambda: {"seconds": 42, "human": "0 hours, 0 minutes"},
    )

    runtime = router.get_runtime()

    assert runtime["uptime_seconds"] == 42
    assert runtime["uptime_human"] == "0 hours, 0 minutes"
    assert runtime["timezone"] == "UTC"
    assert runtime["current_time"].endswith("Z")
    datetime.strptime(runtime["current_time"], "%Y-%m-%dT%H:%M:%SZ")


def test_get_platform_info_windows_platform_version_branch(monkeypatch):
    """Windows branch should format platform_version from win32 metadata."""
    monkeypatch.setattr(router.platform, "system", lambda: "Windows")
    monkeypatch.setattr(router.platform, "win32_ver", lambda: ("", "11", "", ""))
    monkeypatch.setattr(router.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(router.platform, "python_version", lambda: "3.14.2")
    monkeypatch.setattr(router.socket, "gethostname", lambda: "test-host")
    monkeypatch.setattr(router, "cpu_count", lambda: 8)

    payload = router.get_platform_info()

    assert payload["platform"] == "Windows"
    assert payload["platform_version"] == "Windows 11"
    assert payload["hostname"] == "test-host"
    assert payload["cpu_count"] == 8


def test_get_platform_info_default_platform_version_branch(monkeypatch):
    """Non-Linux and non-Windows branch should use platform.version()."""
    monkeypatch.setattr(router.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(router.platform, "version", lambda: "Darwin Kernel 25.0")
    monkeypatch.setattr(router.platform, "machine", lambda: "arm64")
    monkeypatch.setattr(router.platform, "python_version", lambda: "3.14.2")
    monkeypatch.setattr(router.socket, "gethostname", lambda: "mac-host")
    monkeypatch.setattr(router, "cpu_count", lambda: 10)

    payload = router.get_platform_info()

    assert payload["platform"] == "Darwin"
    assert payload["platform_version"] == "Darwin Kernel 25.0"


def test_get_request_info_returns_none_when_user_agent_missing():
    """Missing User-Agent header should map to None without crashing."""
    with app.test_request_context(
        "/diagnostic",
        method="POST",
        environ_base={"REMOTE_ADDR": "198.51.100.9"},
    ):
        info = router.get_request_info(request)

    assert info == {
        "client_ip": "198.51.100.9",
        "user_agent": None,
        "method": "POST",
        "path": "/diagnostic",
    }
