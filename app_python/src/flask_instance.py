"""
Flask app instance and shared process-level state.
"""

from datetime import datetime, timezone
import logging

from flask import Flask

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask("DevOps Info Service")
START_TIME = datetime.now(timezone.utc)  # Application start time (UTC).
