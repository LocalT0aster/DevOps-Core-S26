# Lab 07 - Task 1

## Stack

- `grafana/loki:3.0.0` on `http://localhost:3100`
- `grafana/promtail:3.0.0` on `http://localhost:9080`
- `grafana/grafana:12.3.1` on `http://localhost:3000`

## Local deployment

```bash
cd monitoring
docker compose up -d
docker compose ps
curl -fSsL localhost:3100/ready
curl -fSsL localhost:9080/targets
curl -fSsL localhost:3000/api/health
```

Grafana provisions Loki automatically as the default datasource, so logs are available immediately in **Explore**.

## Task 2

Start the applications inside the same stack:

```bash
cd monitoring
docker compose up -d
for i in $(seq 1 10); do
  curl -fsSL localhost:8000/ >/dev/null
  curl -fsSL localhost:8000/health >/dev/null
  curl -fsSL localhost:8001/ >/dev/null
  curl -fsSL localhost:8001/health >/dev/null
done
curl -fsSL localhost:8000/do404 >/dev/null
curl -fsSL localhost:8001/do404 >/dev/null
```

LogQL queries:

```logql
{job="docker", app=~"devops-python|devops-go"}
```

![](img/task2_apps.png)

```logql
{app=~"devops-python|devops-go"} | json | method="GET"
```

![](img/task2_get.png)

```logql
{app=~"devops-python|devops-go"} |= "WARN"
```

![](img/task2_warn.png)
