"""
DevOps Info Service
Application runtime entrypoint.
"""

import os

from flask_instance import app, logger
import router  # noqa: F401
logger.info("b")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


def run() -> None:
    """Run development server."""
    logger.info("Application starting...")
    app.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == "__main__":
    run()
