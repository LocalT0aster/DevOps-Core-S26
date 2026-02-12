"""
DevOps Info Service
Application runtime entrypoint.
"""

import os

try:
    from .flask_instance import app, logger
    from . import router  # noqa: F401
except ImportError:  # pragma: no cover - allows `python src/main.py`
    from flask_instance import app, logger
    import router  # noqa: F401

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


def run() -> None:
    """Run development server."""
    logger.info("Application starting...")
    app.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == "__main__":  # pragma: no cover
    run()
