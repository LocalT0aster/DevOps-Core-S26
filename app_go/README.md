# DevOps Info Service (Go)

## Overview
Simple Go web service that exposes system/runtime details, a file-backed visits counter, health and readiness checks, Prometheus metrics, and structured JSON logs.

## Prerequisites
- Go 1.25+

## Build
```bash
go build -o devops-info-service.out .
```

## Run
```bash
./devops-info-service.out
# Or with custom config
HOST=127.0.0.1 PORT=8080 ./devops-info-service.out
```

## Endpoints
- `GET /` - service + system + runtime + request info
- `GET /visits` - current visits counter stored in `/data/visits`
- `GET /health` - health check
- `GET /ready` - readiness check
- `GET /metrics` - Prometheus metrics exposition

## Visits Counter
- The root handler increments the counter on every `GET /`.
- The counter is persisted as plain text in `/data/visits`.
- If the file is missing, the service starts from `0`.
- If the file is malformed, the service logs a warning and treats the value as `0`.

## Local Docker Check
For Lab 12, run the monitoring stack with a writable `/data` volume for the Go container and verify that:
- repeated `GET /` calls increment the counter
- `GET /visits` returns the current count
- the counter survives a container restart because the backing file is persisted on the host

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Bind address for the server |
| `PORT` | `5000` | Port to listen on |
