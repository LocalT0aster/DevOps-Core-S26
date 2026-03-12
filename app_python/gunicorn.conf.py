"""Gunicorn configuration for container deployment."""

from __future__ import annotations

import os

bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}"
workers = int(os.getenv("GUNICORN_WORKERS", "1"))
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = (
    '{"timestamp":"%(t)s","level":"INFO","logger":"gunicorn.access",'
    '"client_ip":"%(h)s","method":"%(m)s","path":"%(U)s","query":"%(q)s",'
    '"status_code":%(s)s,"response_bytes":"%(B)s","request_time_us":%(D)s,'
    '"user_agent":"%(a)s"}'
)
