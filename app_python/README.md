# DevOps Info Service

[![Python CI](https://github.com/LocalT0aster/DevOps-Core-S26/actions/workflows/python-ci.yml/badge.svg)](https://github.com/LocalT0aster/DevOps-Core-S26/actions/workflows/python-ci.yml)

## Overview

Small Flask web service that reports service metadata, system information, runtime uptime, and basic request details. Includes a simple health check endpoint for monitoring.

## Prerequisites

- Python 3.13+
- Poetry

## Installation

```bash
poetry install
```

### Docker

- Pull the container:
  ```bash
  docker pull localt0aster/devops-app-py
  ```
- OR build the container yourself:
  ```bash
  docker build -t localt0aster/devops-app-py .
  ```
  The Docker build installs dependencies with:
  ```bash
  poetry install --only main --no-root
  ```

## Running the Application

Production-style local run with Gunicorn:

```bash
poetry run gunicorn --bind 0.0.0.0:5000 src.flask_instance:app
# Or with custom config
HOST=127.0.0.1 PORT=8080 poetry run gunicorn --bind 127.0.0.1:8080 src.flask_instance:app
```

### Docker

- Run the container:
  ```bash
  docker run -p 5000:5000 -e HOST="0.0.0.0" -d localt0aster/devops-app-py
  ```

## API Endpoints

- `GET /` - Service and system information
- `GET /health` - Health check

## Configuration

| Variable | Default   | Description                              |
| -------- | --------- | ---------------------------------------- |
| `HOST`   | `0.0.0.0` | Bind address for the server              |
| `PORT`   | `5000`    | Port to listen on                        |
| `DEBUG`  | `False`   | Enable Flask debug mode (`true`/`false`) |

## Testing

The project uses `pytest` for unit tests.

```bash
poetry install --with dev
poetry run pytest --cov=src --cov-report=term-missing
```

## Linting

```bash
poetry run flake8 src tests
```

Current test coverage includes:

- `GET /` successful response schema and types
- `GET /health` successful response schema and types
- `404` JSON error handling for unknown routes
- `500` JSON error handling for simulated internal failures
