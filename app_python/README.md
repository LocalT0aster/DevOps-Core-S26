# DevOps Info Service

## Overview

Small Flask web service that reports service metadata, system information, runtime uptime, and basic request details. Includes a simple health check endpoint for monitoring.

## Prerequisites

- Python 3.14
- Dependencies from `requirements.txt`

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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

## Running the Application

```bash
python app.py
# Or with custom config
PORT=8080 HOST=127.0.0.1 python app.py
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
