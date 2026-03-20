# LAB08 - Metrics and Monitoring (Task 2)

## 1. Overview

Prometheus was added to the existing Lab 7 monitoring stack in [docker-compose.yml](/home/t0ast/Repos/DevOps-Core-S26/monitoring/docker-compose.yml) and configured in [prometheus/prometheus.yml](/home/t0ast/Repos/DevOps-Core-S26/monitoring/prometheus/prometheus.yml).

Key decisions:

- `prom/prometheus:v3.9.0` is exposed on `localhost:9090`
- metrics are stored in the `prometheus-data` named volume
- Prometheus scrapes every `15s`
- the Python app image was updated to `localt0aster/devops-app-py:1.8.806c77e` so the stack uses the branch build that already contains the Lab 8 `/metrics` endpoint
- scrape jobs cover `prometheus`, `app-python`, `loki`, and `grafana`

## 2. Commands Used

```bash
PS1="$ "
cd monitoring
docker compose up -d
docker compose ps | tee /tmp/lab08_task2_compose_ps.txt
curl -fSs http://127.0.0.1:9090/api/v1/targets \
  | jq '{status, data: {activeTargets: [.data.activeTargets[] | {labels, scrapeUrl, lastError, health}]}}' \
  | tee /tmp/lab08_task2_targets.json
curl -fSsG --data-urlencode 'query=up' http://127.0.0.1:9090/api/v1/query \
  | jq '{status, data: {resultType: .data.resultType, result: .data.result}}' \
  | tee /tmp/lab08_task2_up.json
```

## 3. Evidence

Screenshots captured:

![](img/lab08_task2_targets.png)
![](img/lab08_task2_up_query.png)

<details>
<summary><code>docker compose ps</code> output</summary>

```text
$ docker compose ps | tee /tmp/lab08_task2_compose_ps.txt
NAME                              IMAGE                                    COMMAND                  SERVICE              CREATED              STATUS                        PORTS
monitoring-app-go-1               localt0aster/devops-app-go:1.7.9a42ee5   "/devops-info-servic…"   app-go               23 minutes ago   Up 23 minutes             0.0.0.0:8001->8001/tcp, [::]:8001->8001/tcp
monitoring-app-go-healthcheck-1   curlimages/curl:8.18.0                   "/entrypoint.sh sh -…"   app-go-healthcheck   23 minutes ago   Up 23 minutes (healthy)
monitoring-app-python-1           localt0aster/devops-app-py:1.8.806c77e   "sh -c 'gunicorn --c…"   app-python           23 minutes ago   Up 23 minutes (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
monitoring-grafana-1              grafana/grafana:12.3.1                   "/run.sh"                grafana              23 minutes ago   Up 23 minutes (healthy)   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
monitoring-loki-1                 grafana/loki:3.0.0                       "/usr/bin/loki -conf…"   loki                 23 minutes ago   Up 23 minutes (healthy)   0.0.0.0:3100->3100/tcp, [::]:3100->3100/tcp
monitoring-prometheus-1           prom/prometheus:v3.9.0                   "/bin/prometheus --c…"   prometheus           23 minutes ago   Up 23 minutes             0.0.0.0:9090->9090/tcp, [::]:9090->9090/tcp
monitoring-promtail-1             grafana/promtail:3.0.0                   "/usr/bin/promtail -…"   promtail             23 minutes ago   Up 23 minutes             0.0.0.0:9080->9080/tcp, [::]:9080->9080/tcp
```

</details>

<details>
<summary><code>/api/v1/targets</code> output</summary>

```json
$ curl -fSs http://127.0.0.1:9090/api/v1/targets | jq '{status, data: {activeTargets: [.data.activeTargets[] | {labels, scrapeUrl, lastError, health}]}}' | tee /tmp/lab08_task2_targets.json
{
  "status": "success",
  "data": {
    "activeTargets": [
      {
        "labels": {
          "instance": "app-python:8000",
          "job": "app"
        },
        "scrapeUrl": "http://app-python:8000/metrics",
        "lastError": "",
        "health": "up"
      },
      {
        "labels": {
          "instance": "grafana:3000",
          "job": "grafana"
        },
        "scrapeUrl": "http://grafana:3000/metrics",
        "lastError": "",
        "health": "up"
      },
      {
        "labels": {
          "instance": "loki:3100",
          "job": "loki"
        },
        "scrapeUrl": "http://loki:3100/metrics",
        "lastError": "",
        "health": "up"
      },
      {
        "labels": {
          "instance": "localhost:9090",
          "job": "prometheus"
        },
        "scrapeUrl": "http://localhost:9090/metrics",
        "lastError": "",
        "health": "up"
      }
    ]
  }
}
```

</details>

<details>
<summary><code>query=up</code> output</summary>

```json
$ curl -fSsG --data-urlencode 'query=up' http://127.0.0.1:9090/api/v1/query | jq '{status, data: {resultType: .data.resultType, result: .data.result}}' | tee /tmp/lab08_task2_up.json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {
          "__name__": "up",
          "instance": "grafana:3000",
          "job": "grafana"
        },
        "value": [
          1773963907.906,
          "1"
        ]
      },
      {
        "metric": {
          "__name__": "up",
          "instance": "localhost:9090",
          "job": "prometheus"
        },
        "value": [
          1773963907.906,
          "1"
        ]
      },
      {
        "metric": {
          "__name__": "up",
          "instance": "app-python:8000",
          "job": "app"
        },
        "value": [
          1773963907.906,
          "1"
        ]
      },
      {
        "metric": {
          "__name__": "up",
          "instance": "loki:3100",
          "job": "loki"
        },
        "value": [
          1773963907.906,
          "1"
        ]
      }
    ]
  }
}
```

</details>

## 4. Notes

- Grafana reported `DOWN` on the very first Prometheus scrape because the container was still starting; it flipped to `UP` on the next 15-second scrape without any config change.
- The stack is currently running locally, so `http://localhost:9090/targets` and `http://localhost:9090/graph?g0.expr=up` can be opened directly for manual inspection.
