FROM python:3.14-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.3.2

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && addgroup appgroup \
    && adduser --disabled-password --gecos "" --no-create-home -s /bin/sh appuser -G appgroup

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

COPY src ./src

ENV PORT=5000
ENV HOST="0.0.0.0"

USER appuser
CMD ["sh", "-c", "gunicorn --bind ${HOST:-0.0.0.0}:${PORT:-5000} src.flask_instance:app"]
