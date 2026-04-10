# Kubernetes Lab 12 - ConfigMaps and Persistent Volumes

I reused the existing Docker-backed `minikube` cluster instead of tearing it down. The starting state already contained the Lab 11 app release and Vault, so this lab was added on top of that environment with a new Helm release name, `lab12-devops-app-py`, to avoid clobbering the earlier work. All usernames and passwords are redacted in this write-up.

## Current Cluster Context

<details>
<summary><code>kubectl config current-context</code>, <code>kubectl cluster-info</code>, <code>kubectl get nodes -o wide</code>, <code>kubectl get storageclass</code>, <code>helm list -A</code></summary>

```text
$ kubectl config current-context
minikube
$ kubectl cluster-info
Kubernetes control plane is running at https://192.168.49.2:8443
CoreDNS is running at https://192.168.49.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
$ kubectl get nodes -o wide
NAME       STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION      CONTAINER-RUNTIME
minikube   Ready    control-plane   52m   v1.35.1   192.168.49.2   <none>        Debian GNU/Linux 12 (bookworm)   6.19.11-1-cachyos   docker://29.2.1
$ kubectl get storageclass
NAME                 PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
standard (default)   k8s.io/minikube-hostpath   Delete          Immediate           false                  52m
$ helm list -A
NAME               	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART              	APP VERSION
lab11-devops-app-py	default  	2       	2026-04-10 02:04:56.679295263 +0300 +03	deployed	devops-app-py-0.3.0	1.9
vault              	vault    	1       	2026-04-10 02:02:00.558749873 +0300 +03	deployed	vault-0.32.0       	1.21.2
```

</details>

## Task 1 - Application Persistence Upgrade

I implemented the same file-backed visits counter in both `app_python` and `app_go`. Both services now store the counter in `/data/visits`, increment it on every `GET /`, expose `GET /visits`, default to `0` when the file is missing, and recover from malformed content by treating it as `0`. The Python runtime version and `pyproject.toml` version both moved to `1.12.0`, and the Go runtime version moved to `1.12.0`.

<details>
<summary><code>./.venv/bin/pytest</code>, <code>go test ./...</code>, and separate app commits</summary>

```bash
$ ./.venv/bin/pytest
============================= test session starts ==============================
platform linux -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /home/t0ast/Repos/DevOps-Core-S26/app_python
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.1.0
collected 19 items

tests/test_endpoints.py ...........                                      [ 57%]
tests/test_logging_utils.py .                                            [ 63%]
tests/test_metrics.py ..                                                 [ 73%]
tests/test_unit_helpers.py .....                                         [100%]

============================== 19 passed in 0.11s ==============================

$ go test ./...
ok  	example.com/devops-info-service	0.005s

$ git log --oneline -2
3ebf11e feat(app_go): add persistent visits endpoint
ceaf67d feat(app_python): add persistent visits endpoint
```

</details>

<details>
<summary><code>docker compose -f monitoring/docker-compose.yml config | sed -n "/app-go:/,/grafana:/p"</code></summary>

```text
$ docker compose -f monitoring/docker-compose.yml config | sed -n /app-go:/,/grafana:/p
  app-go:
    environment:
      HOST: 0.0.0.0
      PORT: "8001"
    image: localt0aster/devops-app-go:1.12-dev
    ports:
      - mode: ingress
        target: 8001
        published: "8001"
        protocol: tcp
    volumes:
      - type: bind
        source: /home/t0ast/Repos/DevOps-Core-S26/monitoring/data/app-go
        target: /data
        bind: {}
  app-python:
    environment:
      HOST: 0.0.0.0
      PORT: "8000"
    image: localt0aster/devops-app-py:1.12-dev
    ports:
      - mode: ingress
        target: 8000
        published: "8000"
        protocol: tcp
    volumes:
      - type: bind
        source: /home/t0ast/Repos/DevOps-Core-S26/monitoring/data/app-python
        target: /data
        bind: {}
```

</details>

<details>
<summary><code>docker compose up</code> and local visits persistence proof for both apps</summary>

```bash
$ docker compose -f monitoring/docker-compose.yml up -d --pull always app-python app-go app-go-healthcheck
...
$ docker compose -f monitoring/docker-compose.yml ps app-python app-go app-go-healthcheck
NAME                              IMAGE                               COMMAND                  SERVICE              CREATED        STATUS                                     PORTS
monitoring-app-go-1               localt0aster/devops-app-go:1.12-dev   "/devops-info-servic…"   app-go               1 second ago   Up Less than a second                      0.0.0.0:8001->8001/tcp, [::]:8001->8001/tcp
monitoring-app-go-healthcheck-1   curlimages/curl:8.18.0              "/entrypoint.sh sh -…"   app-go-healthcheck   1 second ago   Up Less than a second (health: starting)
monitoring-app-python-1           localt0aster/devops-app-py:1.12-dev   "sh -c 'gunicorn --c…"   app-python           1 second ago   Up Less than a second (health: starting)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp

$ curl -sS http://127.0.0.1:8000/visits | jq .
{
  "visits": 0
}
$ curl -sS http://127.0.0.1:8000/ >/dev/null
$ curl -sS http://127.0.0.1:8000/ >/dev/null
$ curl -sS http://127.0.0.1:8000/visits | jq .
{
  "visits": 2
}
$ cat monitoring/data/app-python/visits
2

$ curl -sS http://127.0.0.1:8001/visits | jq .
{
  "visits": 0
}
$ curl -sS http://127.0.0.1:8001/ >/dev/null
$ curl -sS http://127.0.0.1:8001/ >/dev/null
$ curl -sS http://127.0.0.1:8001/visits | jq .
{
  "visits": 2
}
$ cat monitoring/data/app-go/visits
2

$ docker compose -f monitoring/docker-compose.yml restart app-python app-go
...
$ curl -sS http://127.0.0.1:8000/visits | jq .
{
  "visits": 2
}
$ curl -sS http://127.0.0.1:8001/visits | jq .
{
  "visits": 2
}
$ cat monitoring/data/app-python/visits
2
$ cat monitoring/data/app-go/visits
2
```

</details>

## Task 2 - ConfigMaps

I extended the existing Helm chart instead of writing one-off manifests. The chart now contains:

- `files/config.json` as the file-backed application config source
- `templates/configmap.yaml` rendering both a file ConfigMap and an env ConfigMap
- `templates/pvc.yaml` for the visits counter volume
- checksum annotations on the Pod template so chart-managed config changes trigger a rollout

I also changed the chart defaults for Lab 12 correctness: `replicaCount` is now `1`, the chart version is `0.4.0`, the app version is `1.12.0`, and the dev NodePort moved to `30082` so it does not collide with the existing Lab 11 release on `30081`.

<details>
<summary><code>helm lint</code> and rendered manifest excerpts</summary>

```bash
$ helm lint k8s/devops-app-py
==> Linting k8s/devops-app-py
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

```yaml
# Source: devops-app-py/templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: lab12-devops-app-py-config
data:
  config.json: |-
    {
      "application": {
        "name": "devops-info-service",
        "environment": "development",
        "version": "1.12-dev"
      },
      "featureFlags": {
        "visitsCounter": true,
        "metrics": true,
        "configReloadDemo": true
      },
      "settings": {
        "configPath": "/config/config.json",
        "visitsFile": "/data/visits",
        "reloadStrategy": "checksum-rollout"
      }
    }
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: lab12-devops-app-py-env
data:
  APP_CONFIG_PATH: /config/config.json
  APP_ENV: development
  APP_NAME: devops-info-service
  APP_VISITS_PATH: /data/visits
  LOG_LEVEL: debug
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: lab12-devops-app-py-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lab12-devops-app-py
spec:
  replicas: 1
  template:
    metadata:
      annotations:
        checksum/config-file: "75d068a2b686d100b01ef7eb95c683ff78dc01f7103131c74502cd3dba657e95"
        checksum/config-env: "ade0526aff038f694a130dfce92e2748879ea4cd4e9a802b692762639b4851bf"
    spec:
      containers:
        - name: devops-app-py
          image: "localt0aster/devops-app-py:1.12-dev"
          volumeMounts:
            - name: config-volume
              mountPath: "/config"
              readOnly: true
            - name: data-volume
              mountPath: "/data"
          envFrom:
            - configMapRef:
                name: lab12-devops-app-py-env
            - secretRef:
                name: lab12-devops-app-py-secret
      volumes:
        - name: config-volume
          configMap:
            name: lab12-devops-app-py-config
        - name: data-volume
          persistentVolumeClaim:
            claimName: lab12-devops-app-py-data
```

</details>

## Task 3 - Persistent Volumes

I installed the updated chart as a new release named `lab12-devops-app-py`, verified the rendered ConfigMaps and PVC in-cluster, then proved that the application could read `/config/config.json`, receive the env ConfigMap via `envFrom`, write `/data/visits`, and survive a Pod replacement without losing the counter.

One useful operational detail from `kubectl describe pod` is that Kubernetes shows the env var sources as `ConfigMap` and `Secret` references instead of dumping the actual values. That keeps Pod inspection safer while still proving where the data comes from.

<details>
<summary><code>helm upgrade --install lab12-devops-app-py ...</code> and initial resource state</summary>

```bash
$ helm upgrade --install lab12-devops-app-py k8s/devops-app-py -n default -f k8s/devops-app-py/values-dev.yaml --wait --wait-for-jobs --timeout 300s
Release "lab12-devops-app-py" does not exist. Installing it now.
NAME: lab12-devops-app-py
LAST DEPLOYED: Fri Apr 10 03:02:03 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
```

```text
$ kubectl get deploy,svc,pod,configmap,pvc -n default -l app.kubernetes.io/instance=lab12-devops-app-py -o wide
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS      IMAGES                              SELECTOR
deployment.apps/lab12-devops-app-py   1/1     1            1           61s   devops-app-py   localt0aster/devops-app-py:1.12-dev   app.kubernetes.io/instance=lab12-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                  TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/lab12-devops-app-py-service   NodePort   10.101.70.46   <none>        80:30082/TCP   61s   app.kubernetes.io/instance=lab12-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                       READY   STATUS    RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
pod/lab12-devops-app-py-5f6df94f6d-5wxtq   1/1     Running   0          61s   10.244.0.10   minikube   <none>           <none>

NAME                                   DATA   AGE
configmap/lab12-devops-app-py-config   1      61s
configmap/lab12-devops-app-py-env      5      61s

NAME                                             STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE   VOLUMEMODE
persistentvolumeclaim/lab12-devops-app-py-data   Bound    pvc-d04d328c-f6f3-44f7-8347-d8724a16b744   100Mi      RWO            standard       <unset>                 61s   Filesystem
```

</details>

<details>
<summary><code>kubectl exec</code> for mounted <code>/config/config.json</code>, env vars, and Pod description</summary>

```bash
$ kubectl exec -n default lab12-devops-app-py-5f6df94f6d-5wxtq -- cat /config/config.json | jq .
{
  "application": {
    "name": "devops-info-service",
    "environment": "development",
    "version": "1.12-dev"
  },
  "featureFlags": {
    "visitsCounter": true,
    "metrics": true,
    "configReloadDemo": true
  },
  "settings": {
    "configPath": "/config/config.json",
    "visitsFile": "/data/visits",
    "reloadStrategy": "checksum-rollout"
  }
}

$ kubectl exec -n default lab12-devops-app-py-5f6df94f6d-5wxtq -- printenv | grep -E "^(APP_|LOG_LEVEL)"
APP_ENV=development
LOG_LEVEL=debug
APP_CONFIG_PATH=/config/config.json
APP_NAME=devops-info-service
APP_VISITS_PATH=/data/visits
APP_PASSWORD=[REDACTED]
APP_USERNAME=[REDACTED]
```

```text
$ kubectl describe pod -n default lab12-devops-app-py-5f6df94f6d-bkwfx
...
Environment Variables from:
  lab12-devops-app-py-env     ConfigMap  Optional: false
  lab12-devops-app-py-secret  Secret     Optional: false
Environment:
  HOST:  0.0.0.0
  PORT:  5000
Mounts:
  /config from config-volume (ro)
  /data from data-volume (rw)
...
```

</details>

<details>
<summary><code>curl</code> through the NodePort and PVC persistence across pod deletion</summary>

```bash
$ minikube ip
192.168.49.2
$ curl -sS http://192.168.49.2:30082/visits | jq .
{
  "visits": 0
}
$ curl -sS http://192.168.49.2:30082/ >/dev/null
$ curl -sS http://192.168.49.2:30082/ >/dev/null
$ curl -sS http://192.168.49.2:30082/visits | jq .
{
  "visits": 2
}
$ kubectl exec -n default lab12-devops-app-py-5f6df94f6d-5wxtq -- cat /data/visits
2

$ kubectl delete pod -n default lab12-devops-app-py-5f6df94f6d-5wxtq
pod "lab12-devops-app-py-5f6df94f6d-5wxtq" deleted from default namespace
$ kubectl wait -n default --for=condition=Ready pod -l app.kubernetes.io/instance=lab12-devops-app-py --timeout=180s
pod/lab12-devops-app-py-5f6df94f6d-bkwfx condition met
old_pod=lab12-devops-app-py-5f6df94f6d-5wxtq
new_pod=lab12-devops-app-py-5f6df94f6d-bkwfx
$ curl -sS http://192.168.49.2:30082/visits | jq .
{
  "visits": 2
}
$ kubectl exec -n default lab12-devops-app-py-5f6df94f6d-bkwfx -- cat /data/visits
2
```

</details>

## Bonus - ConfigMap Update Behavior

I deliberately mounted the ConfigMap as a directory (`/config`) instead of using `subPath`. The reason is simple: `subPath` mounts are bind mounts to a fixed inode, so they do not receive projected ConfigMap updates. For a live file update demonstration, the whole projected directory mount is the correct pattern.

I tested three distinct behaviors:

1. A manual `kubectl patch` against the file ConfigMap updated the mounted `/config/config.json` inside the running Pod after roughly 11 seconds.
2. A manual patch against the env ConfigMap did not change `APP_ENV` inside the already-running process, which confirms that `envFrom` variables are fixed at container start.
3. A chart-managed config change updated the checksum annotations and rolled the Deployment to a new Pod, which then saw the new file content and the new env vars.

One practical wrinkle showed up during this: after I used `kubectl patch` on Helm-managed ConfigMaps, the next `helm upgrade` hit server-side-apply field ownership conflicts on the same keys. I repaired that by reapplying the rendered ConfigMaps with `kubectl apply --server-side --force-conflicts --field-manager=helm`, then reran a new chart-managed config change successfully.

<details>
<summary><code>kubectl patch configmap lab12-devops-app-py-config</code> and mounted-file update delay</summary>

```bash
$ jq . <<< "$PATCH"
{
  "data": {
    "config.json": "{\n  \"application\": {\n    \"name\": \"devops-info-service\",\n    \"environment\": \"manual-edit\",\n    \"version\": \"1.12-dev\"\n  },\n  \"featureFlags\": {\n    \"visitsCounter\": true,\n    \"metrics\": true,\n    \"configReloadDemo\": true\n  },\n  \"settings\": {\n    \"configPath\": \"/config/config.json\",\n    \"visitsFile\": \"/data/visits\",\n    \"reloadStrategy\": \"checksum-rollout\"\n  }\n}"
  }
}
$ kubectl patch configmap -n default lab12-devops-app-py-config --type merge -p "$PATCH"
configmap/lab12-devops-app-py-config patched
$ wait for mounted /config/config.json to show environment=manual-edit
delay_seconds=11
$ kubectl exec -n default lab12-devops-app-py-5f6df94f6d-bkwfx -- cat /config/config.json | jq .application.environment
"manual-edit"
```

</details>

<details>
<summary><code>kubectl patch configmap lab12-devops-app-py-env</code> and proof that <code>envFrom</code> does not hot-reload</summary>

```bash
$ jq . <<< "$PATCH"
{
  "data": {
    "APP_ENV": "manual-edit"
  }
}
$ kubectl patch configmap -n default lab12-devops-app-py-env --type merge -p "$PATCH"
configmap/lab12-devops-app-py-env patched
$ kubectl exec -n default lab12-devops-app-py-5f6df94f6d-bkwfx -- printenv APP_ENV
development
```

</details>

<details>
<summary><code>kubectl apply --server-side --force-conflicts --field-manager=helm</code> to repair Helm ownership</summary>

```bash
$ helm template lab12-devops-app-py k8s/devops-app-py -n default -f k8s/devops-app-py/values-dev.yaml --set config.file.environment=chart-rollout --set config.env.data.APP_ENV=chart-rollout --show-only templates/configmap.yaml > /tmp/lab12/52-rendered-configmaps.yaml
$ kubectl apply --server-side --force-conflicts --field-manager=helm -f /tmp/lab12/52-rendered-configmaps.yaml
configmap/lab12-devops-app-py-config serverside-applied
configmap/lab12-devops-app-py-env serverside-applied
$ kubectl get configmap lab12-devops-app-py-config -n default -o json | jq -r .data["config.json"] | jq .application.environment
"chart-rollout"
$ kubectl get configmap lab12-devops-app-py-env -n default -o json | jq -r .data.APP_ENV
chart-rollout
```

</details>

<details>
<summary><code>helm upgrade ... --set config.file.environment=chart-rollout-fixed --set config.env.data.APP_ENV=chart-rollout-fixed</code></summary>

```bash
$ helm upgrade lab12-devops-app-py k8s/devops-app-py -n default -f k8s/devops-app-py/values-dev.yaml --set config.file.environment=chart-rollout-fixed --set config.env.data.APP_ENV=chart-rollout-fixed --wait --wait-for-jobs --timeout 300s
Release "lab12-devops-app-py" has been upgraded. Happy Helming!
NAME: lab12-devops-app-py
LAST DEPLOYED: Fri Apr 10 03:07:15 2026
NAMESPACE: default
STATUS: deployed
REVISION: 4
DESCRIPTION: Upgrade complete
old_pod=lab12-devops-app-py-6b4d4cff8d-wbcnz
new_pod=lab12-devops-app-py-7bb96994f8-n6269
$ kubectl get deployment -n default lab12-devops-app-py -o json | jq .spec.template.metadata.annotations
{
  "checksum/config-env": "e34c4bf455ae82b7283e96127fcffbd6fe96332325a9e8953204033ec6ade5f5",
  "checksum/config-file": "8d6ed3c72ff6122928a1d3e148717df696ff7cb1f6f203fcc8934903da9669a7"
}
$ kubectl exec -n default lab12-devops-app-py-7bb96994f8-n6269 -- cat /config/config.json | jq .application.environment
"chart-rollout-fixed"
$ kubectl exec -n default lab12-devops-app-py-7bb96994f8-n6269 -- printenv APP_ENV
chart-rollout-fixed
```

</details>

<details>
<summary><code>curl</code> end-state service check after the final rollout</summary>

```bash
$ curl -sS http://192.168.49.2:30082/health | jq .
{
  "status": "healthy",
  "timestamp": "2026-04-10T00:07:47.059488+00:00",
  "uptime_seconds": 14
}
$ curl -sS http://192.168.49.2:30082/ready | jq .
{
  "status": "ready",
  "timestamp": "2026-04-10T00:07:47.079301+00:00",
  "uptime_seconds": 14
}
$ curl -sS http://192.168.49.2:30082/visits | jq .
{
  "visits": 2
}
```

</details>

## ConfigMap vs Secret

- Use a `ConfigMap` for non-sensitive application configuration such as environment names, feature flags, log levels, file paths, and JSON app settings.
- Use a `Secret` for credentials or tokens. In this repo the chart still keeps `APP_USERNAME` and `APP_PASSWORD` in a separate Secret and only references them via `envFrom`.
- `ConfigMap` data is meant to be readable operational config. `Secret` data is still only base64-encoded unless cluster-side at-rest encryption and RBAC are configured properly.
- Mounted ConfigMap files can update in place when the whole projected directory is mounted. Environment variables injected from either `ConfigMap` or `Secret` do not update inside an already-running container.

## Task 4 - Documentation

This file is the full Lab 12 report. The compatibility filename required by the lab lives at [../CONFIGMAPS.md](../CONFIGMAPS.md) and points back here so the module root does not turn into one large transcript dump.
