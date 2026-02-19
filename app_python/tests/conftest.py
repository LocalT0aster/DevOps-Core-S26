"""Shared pytest fixtures for app endpoint tests."""

import pytest

from src.flask_instance import app
import src.router  # noqa: F401  # Ensure route decorators are loaded.


@pytest.fixture()
def client():
    """Return a Flask test client without starting a real HTTP server."""
    app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
    with app.test_client() as test_client:
        yield test_client
