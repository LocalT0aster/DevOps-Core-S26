# LAB08 - Metrics and Monitoring (Task 1)

## 1. Overview

Prometheus instrumentation was added to the Flask service using `prometheus-client==0.23.1`.

Implemented metrics:

- `http_requests_total` counter with `method`, `endpoint`, and `status_code`
- `http_request_duration_seconds` histogram with `method`, `endpoint`, and `status_code`
- `http_requests_in_progress` gauge with `method` and `endpoint`
- `devops_info_endpoint_calls_total` counter for application endpoint usage
- `devops_info_system_info_duration_seconds` histogram for system-info collection latency

Labeling choice:

- Matched routes use normalized Flask rules such as `/`, `/health`, and `/metrics`
- Unmatched requests are grouped under `endpoint="unmatched"` to keep label cardinality low
- The in-progress gauge does not include `status_code` because that value does not exist until a response is produced

## 2. Verification

Install and run with the project-local Poetry binary:

```bash
cd app_python
.venv/bin/poetry install --with dev
.venv/bin/poetry run pytest
.venv/bin/poetry run gunicorn --config gunicorn.conf.py src.main:app
```

Generate a few requests, then inspect metrics:

```bash
curl -fSsL http://127.0.0.1:5000/ | jq
curl -fSsL http://127.0.0.1:5000/health | jq
curl -fSsL http://127.0.0.1:5000/metrics
```

<details>
<summary><code>/metrics</code> output</summary>

```text
$ curl -fSsL http://127.0.0.1:5000/metrics
# HELP http_requests_total Total HTTP requests handled by the service.
# TYPE http_requests_total counter
http_requests_total{endpoint="/",method="GET",status_code="200"} 6.0
http_requests_total{endpoint="/health",method="GET",status_code="200"} 6.0
# HELP http_requests_created Total HTTP requests handled by the service.
# TYPE http_requests_created gauge
http_requests_created{endpoint="/",method="GET",status_code="200"} 1.7739616481696362e+09
http_requests_created{endpoint="/health",method="GET",status_code="200"} 1.7739616482041702e+09
# HELP http_request_duration_seconds HTTP request duration in seconds.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/",le="0.005",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="0.01",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="0.025",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="0.05",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="0.075",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="0.1",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="0.25",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="0.5",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="0.75",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="1.0",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="2.5",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="5.0",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="7.5",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="10.0",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/",le="+Inf",method="GET",status_code="200"} 6.0
http_request_duration_seconds_count{endpoint="/",method="GET",status_code="200"} 6.0
http_request_duration_seconds_sum{endpoint="/",method="GET",status_code="200"} 0.0015464909993170295
http_request_duration_seconds_bucket{endpoint="/health",le="0.005",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.01",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.025",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.05",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.075",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.1",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.25",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.5",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.75",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="1.0",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="2.5",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="5.0",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="7.5",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="10.0",method="GET",status_code="200"} 6.0
http_request_duration_seconds_bucket{endpoint="/health",le="+Inf",method="GET",status_code="200"} 6.0
http_request_duration_seconds_count{endpoint="/health",method="GET",status_code="200"} 6.0
http_request_duration_seconds_sum{endpoint="/health",method="GET",status_code="200"} 0.0019912700008717366
# HELP http_request_duration_seconds_created HTTP request duration in seconds.
# TYPE http_request_duration_seconds_created gauge
http_request_duration_seconds_created{endpoint="/",method="GET",status_code="200"} 1.7739616481696527e+09
http_request_duration_seconds_created{endpoint="/health",method="GET",status_code="200"} 1.7739616482041845e+09
# HELP http_requests_in_progress HTTP requests currently being processed.
# TYPE http_requests_in_progress gauge
http_requests_in_progress{endpoint="/",method="GET"} 0.0
http_requests_in_progress{endpoint="/health",method="GET"} 0.0
http_requests_in_progress{endpoint="/metrics",method="GET"} 1.0
# HELP devops_info_endpoint_calls_total Total calls to application endpoints.
# TYPE devops_info_endpoint_calls_total counter
devops_info_endpoint_calls_total{endpoint="/"} 6.0
devops_info_endpoint_calls_total{endpoint="/health"} 6.0
devops_info_endpoint_calls_total{endpoint="/metrics"} 1.0
# HELP devops_info_endpoint_calls_created Total calls to application endpoints.
# TYPE devops_info_endpoint_calls_created gauge
devops_info_endpoint_calls_created{endpoint="/"} 1.773961648169205e+09
devops_info_endpoint_calls_created{endpoint="/health"} 1.7739616482040732e+09
devops_info_endpoint_calls_created{endpoint="/metrics"} 1.7739616631203315e+09
# HELP devops_info_system_info_duration_seconds Time spent collecting system information.
# TYPE devops_info_system_info_duration_seconds histogram
devops_info_system_info_duration_seconds_bucket{le="0.005"} 6.0
devops_info_system_info_duration_seconds_bucket{le="0.01"} 6.0
devops_info_system_info_duration_seconds_bucket{le="0.025"} 6.0
devops_info_system_info_duration_seconds_bucket{le="0.05"} 6.0
devops_info_system_info_duration_seconds_bucket{le="0.075"} 6.0
devops_info_system_info_duration_seconds_bucket{le="0.1"} 6.0
devops_info_system_info_duration_seconds_bucket{le="0.25"} 6.0
devops_info_system_info_duration_seconds_bucket{le="0.5"} 6.0
devops_info_system_info_duration_seconds_bucket{le="0.75"} 6.0
devops_info_system_info_duration_seconds_bucket{le="1.0"} 6.0
devops_info_system_info_duration_seconds_bucket{le="2.5"} 6.0
devops_info_system_info_duration_seconds_bucket{le="5.0"} 6.0
devops_info_system_info_duration_seconds_bucket{le="7.5"} 6.0
devops_info_system_info_duration_seconds_bucket{le="10.0"} 6.0
devops_info_system_info_duration_seconds_bucket{le="+Inf"} 6.0
devops_info_system_info_duration_seconds_count 6.0
devops_info_system_info_duration_seconds_sum 0.00042895499973383266
# HELP devops_info_system_info_duration_seconds_created Time spent collecting system information.
# TYPE devops_info_system_info_duration_seconds_created gauge
devops_info_system_info_duration_seconds_created 1.7739616389214125e+09
```

</details>

## 3. Notes

- HTTP metrics are captured with Flask request hooks so 2xx, 4xx, and 5xx responses are all measured consistently.
- Application-specific metrics are recorded in route handlers and around system-info collection.
- Automated tests cover `/metrics` exposure plus label handling for `200`, `404`, and `500` responses.
