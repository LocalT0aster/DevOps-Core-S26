# Kubernetes Lab 10 - Helm Package Manager

## Task 1 - Helm Fundamentals

Helm is a package manager for Kubernetes. In practical terms, a chart bundles templates, defaults, and metadata so the same application can be installed as reusable releases instead of copying raw YAML by hand. Repositories distribute those charts, and `values.yaml` provides the layer where environment-specific settings are changed without rewriting templates.

For the fundamentals task, I verified the local Helm installation, refreshed public repositories, searched available Prometheus-related charts, inspected the metadata of the public `prometheus-community/prometheus` chart, and pulled it locally to review the typical chart structure. The public chart layout confirmed the core Helm pattern: `Chart.yaml` for metadata, `values.yaml` and `values.schema.json` for configuration, `_helpers.tpl` for naming/label helpers, and `templates/` for rendered Kubernetes manifests.

<details>
<summary>Task 1 command output</summary>

```bash
$ helm version
version.BuildInfo{Version:"v4.1.3", GitCommit:"c94d381b03be117e7e57908edbf642104e00eb8f", GitTreeState:"", GoVersion:"go1.26.1-X:nodwarf5", KubeClientVersion:"v1.35"}

$ helm repo add bitnami https://charts.bitnami.com/bitnami
"bitnami" has been added to your repositories

$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "prometheus-community" chart repository
...Successfully got an update from the "bitnami" chart repository
Update Complete. ⎈Happy Helming!⎈

$ helm search repo prometheus
NAME                                              	CHART VERSION	APP VERSION	DESCRIPTION
bitnami/kube-prometheus                           	11.3.10      	0.85.0     	Prometheus Operator provides easy monitoring de...
bitnami/prometheus                                	2.1.23       	3.5.0      	Prometheus is an open source monitoring and ale...
bitnami/wavefront-prometheus-storage-adapter      	2.3.3        	1.0.7      	DEPRECATED Wavefront Storage Adapter is a Prome...
prometheus-community/kube-prometheus-stack        	82.16.1      	v0.89.0    	kube-prometheus-stack collects Kubernetes manif...
prometheus-community/prometheus                   	28.15.0      	v3.11.0    	Prometheus is a monitoring system and time seri...
prometheus-community/prometheus-adapter           	5.3.0        	v0.12.0    	A Helm chart for k8s prometheus adapter
prometheus-community/prometheus-blackbox-exporter 	11.9.1       	v0.28.0    	Prometheus Blackbox Exporter
prometheus-community/prometheus-cloudwatch-expo...	0.28.1       	0.16.0     	A Helm chart for prometheus cloudwatch-exporter
prometheus-community/prometheus-conntrack-stats...	0.5.35       	v0.4.42    	A Helm chart for conntrack-stats-exporter
prometheus-community/prometheus-consul-exporter   	1.1.1        	v0.13.0    	A Helm chart for the Prometheus Consul Exporter
prometheus-community/prometheus-couchdb-exporter  	1.0.1        	1.0        	A Helm chart to export the metrics from couchdb...
prometheus-community/prometheus-druid-exporter    	1.2.0        	v0.11.0    	Druid exporter to monitor druid metrics with Pr...
prometheus-community/prometheus-elasticsearch-e...	7.2.1        	v1.10.0    	Elasticsearch stats exporter for Prometheus
prometheus-community/prometheus-fastly-exporter   	0.11.0       	v10.2.0    	A Helm chart for the Prometheus Fastly Exporter
prometheus-community/prometheus-ipmi-exporter     	0.8.0        	v1.10.1    	This is an IPMI exporter for Prometheus.
prometheus-community/prometheus-json-exporter     	0.19.2       	v0.7.0     	Install prometheus-json-exporter
prometheus-community/prometheus-kafka-exporter    	3.0.1        	v1.9.0     	A Helm chart to export metrics from Kafka in Pr...
prometheus-community/prometheus-memcached-exporter	0.4.5        	v0.15.5    	Prometheus exporter for Memcached metrics
prometheus-community/prometheus-modbus-exporter   	0.1.4        	0.4.1      	A Helm chart for prometheus-modbus-exporter
prometheus-community/prometheus-mongodb-exporter  	3.18.0       	0.49.0     	A Prometheus exporter for MongoDB metrics
prometheus-community/prometheus-mysql-exporter    	2.13.0       	v0.19.0    	A Helm chart for prometheus mysql exporter with...
prometheus-community/prometheus-nats-exporter     	2.22.1       	0.19.2     	A Helm chart for prometheus-nats-exporter
prometheus-community/prometheus-nginx-exporter    	1.20.8       	1.5.1      	A Helm chart for NGINX Prometheus Exporter
prometheus-community/prometheus-node-exporter     	4.52.2       	1.10.2     	A Helm chart for prometheus node-exporter
prometheus-community/prometheus-opencost-exporter 	0.1.2        	1.108.0    	Prometheus OpenCost Exporter
prometheus-community/prometheus-operator          	9.3.2        	0.38.1     	DEPRECATED - This chart will be renamed. See ht...
prometheus-community/prometheus-operator-admiss...	0.38.0       	0.90.1     	Prometheus Operator Admission Webhook
prometheus-community/prometheus-operator-crds     	28.0.1       	v0.90.1    	A Helm chart that collects custom resource defi...
prometheus-community/prometheus-pgbouncer-exporter	0.10.0       	v0.12.0    	A Helm chart for prometheus pgbouncer-exporter
prometheus-community/prometheus-pingdom-exporter  	3.4.2        	v0.5.6     	A Helm chart for Prometheus Pingdom Exporter
prometheus-community/prometheus-pingmesh-exporter 	0.4.3        	v1.2.2     	Prometheus Pingmesh Exporter
prometheus-community/prometheus-postgres-exporter 	7.5.2        	v0.19.1    	A Helm chart for prometheus postgres-exporter
prometheus-community/prometheus-pushgateway       	3.6.0        	v1.11.2    	A Helm chart for prometheus pushgateway
prometheus-community/prometheus-rabbitmq-exporter 	2.1.2        	1.0.0      	Rabbitmq metrics exporter for prometheus
prometheus-community/prometheus-redis-exporter    	6.22.0       	v1.82.0    	Prometheus exporter for Redis metrics
prometheus-community/prometheus-smartctl-exporter 	0.16.0       	v0.14.0    	A Helm chart for Kubernetes
prometheus-community/prometheus-snmp-exporter     	9.13.1       	v0.30.1    	Prometheus SNMP Exporter
prometheus-community/prometheus-sql-exporter      	0.5.0        	v0.8       	Prometheus SQL Exporter
prometheus-community/prometheus-stackdriver-exp...	4.12.2       	v0.18.0    	Stackdriver exporter for Prometheus
prometheus-community/prometheus-statsd-exporter   	1.0.0        	v0.28.0    	A Helm chart for prometheus stats-exporter
prometheus-community/prometheus-systemd-exporter  	0.5.2        	0.7.0      	A Helm chart for prometheus systemd-exporter
prometheus-community/prometheus-to-sd             	0.5.1        	v0.9.2     	Scrape metrics stored in prometheus format and ...
prometheus-community/prometheus-windows-exporter  	0.12.6       	0.31.6     	A Helm chart for prometheus windows-exporter
prometheus-community/prometheus-yet-another-clo...	0.43.0       	v0.64.0    	Yace - Yet Another CloudWatch Exporter
prometheus-community/alertmanager                 	1.34.0       	v0.31.1    	The Alertmanager handles alerts sent by client ...
prometheus-community/alertmanager-snmp-notifier   	2.1.0        	v2.1.0     	The SNMP Notifier handles alerts coming from Pr...
prometheus-community/jiralert                     	1.8.2        	v1.3.0     	A Helm chart for Kubernetes to install jiralert
prometheus-community/kube-state-metrics           	7.2.2        	2.18.0     	Install kube-state-metrics to generate and expo...
prometheus-community/prom-label-proxy             	0.18.0       	v0.12.1    	A proxy that enforces a given label in a given ...
prometheus-community/yet-another-cloudwatch-exp...	0.39.1       	v0.62.1    	Yace - Yet Another CloudWatch Exporter
bitnami/grafana-alloy                             	1.0.7        	1.10.2     	Grafana Alloy is an open source OpenTelemetry C...
bitnami/grafana-mimir                             	3.0.18       	2.17.0     	Grafana Mimir is an open source, horizontally s...
bitnami/node-exporter                             	4.5.19       	1.9.1      	Prometheus exporter for hardware and OS metrics...
bitnami/thanos                                    	17.3.1       	0.39.2     	Thanos is a highly available metrics system tha...
bitnami/victoriametrics                           	0.1.31       	1.124.0    	VictoriaMetrics is a fast, cost-effective, and ...
bitnami/kube-state-metrics                        	5.1.0        	2.16.0     	kube-state-metrics is a simple service that lis...
bitnami/mariadb                                   	25.0.6       	12.2.2     	MariaDB is an open source, community-developed ...
bitnami/mariadb-galera                            	16.0.1       	12.0.2     	MariaDB Galera is a multi-primary database clus...

$ helm show chart prometheus-community/prometheus
annotations:
  artifacthub.io/license: Apache-2.0
  artifacthub.io/links: |
    - name: Chart Source
      url: https://github.com/prometheus-community/helm-charts
    - name: Upstream Project
      url: https://github.com/prometheus/prometheus
apiVersion: v2
appVersion: v3.11.0
dependencies:
- condition: alertmanager.enabled
  name: alertmanager
  repository: https://prometheus-community.github.io/helm-charts
  version: 1.34.*
- condition: kube-state-metrics.enabled
  name: kube-state-metrics
  repository: https://prometheus-community.github.io/helm-charts
  version: 7.2.*
- condition: prometheus-node-exporter.enabled
  name: prometheus-node-exporter
  repository: https://prometheus-community.github.io/helm-charts
  version: 4.52.*
- condition: prometheus-pushgateway.enabled
  name: prometheus-pushgateway
  repository: https://prometheus-community.github.io/helm-charts
  version: 3.6.*
description: Prometheus is a monitoring system and time series database.
home: https://prometheus.io/
icon: https://raw.githubusercontent.com/prometheus/prometheus.github.io/master/assets/prometheus_logo-cb55bb5c346.png
keywords:
- monitoring
- prometheus
kubeVersion: '>=1.19.0-0'
maintainers:
- email: gianrubio@gmail.com
  name: gianrubio
  url: https://github.com/gianrubio
- email: zanhsieh@gmail.com
  name: zanhsieh
  url: https://github.com/zanhsieh
- email: miroslav.hadzhiev@gmail.com
  name: Xtigyro
  url: https://github.com/Xtigyro
- email: naseem@transit.app
  name: naseemkullah
  url: https://github.com/naseemkullah
- email: rootsandtrees@posteo.de
  name: zeritti
  url: https://github.com/zeritti
name: prometheus
sources:
- https://github.com/prometheus/alertmanager
- https://github.com/prometheus/prometheus
- https://github.com/prometheus/pushgateway
- https://github.com/prometheus/node_exporter
- https://github.com/kubernetes/kube-state-metrics
type: application
version: 28.15.0


$ helm pull prometheus-community/prometheus --untar --untardir /tmp/lab10-public-chart

$ find /tmp/lab10-public-chart/prometheus -maxdepth 2 -type f
/tmp/lab10-public-chart/prometheus/README.md
/tmp/lab10-public-chart/prometheus/.helmignore
/tmp/lab10-public-chart/prometheus/templates/vpa.yaml
/tmp/lab10-public-chart/prometheus/templates/serviceaccount.yaml
/tmp/lab10-public-chart/prometheus/templates/service.yaml
/tmp/lab10-public-chart/prometheus/templates/rolebinding.yaml
/tmp/lab10-public-chart/prometheus/templates/pvc.yaml
/tmp/lab10-public-chart/prometheus/templates/pdb.yaml
/tmp/lab10-public-chart/prometheus/templates/network-policy.yaml
/tmp/lab10-public-chart/prometheus/templates/ingress.yaml
/tmp/lab10-public-chart/prometheus/templates/httproute.yaml
/tmp/lab10-public-chart/prometheus/templates/headless-svc.yaml
/tmp/lab10-public-chart/prometheus/templates/extra-manifests.yaml
/tmp/lab10-public-chart/prometheus/templates/deploy.yaml
/tmp/lab10-public-chart/prometheus/templates/cm.yaml
/tmp/lab10-public-chart/prometheus/templates/clusterrolebinding.yaml
/tmp/lab10-public-chart/prometheus/templates/clusterrole.yaml
/tmp/lab10-public-chart/prometheus/templates/_helpers.tpl
/tmp/lab10-public-chart/prometheus/templates/NOTES.txt
/tmp/lab10-public-chart/prometheus/values.schema.json
/tmp/lab10-public-chart/prometheus/values.yaml
/tmp/lab10-public-chart/prometheus/Chart.lock
/tmp/lab10-public-chart/prometheus/Chart.yaml
```

</details>

## Task 2 - Create Your Helm Chart

I created the application chart in `k8s/devops-app-py` with the standard Helm structure and converted the existing Lab 9 Deployment and Service into templates. The chart keeps the same application behavior while moving the changeable parts into values: image repository and tag, replica count, rollout strategy, environment variables, resource requests and limits, service settings, and both probes. Naming and labels are centralized in `_helpers.tpl` so the Deployment and Service stay consistent across installs.

The chart was deliberately trimmed to what the lab actually uses. I removed the default scaffold templates for ingress, autoscaling, service accounts, test hooks, and HTTPRoute because they were noise for this app and would have made the chart look more generic than intentional. One practical detail mattered during real installation: the raw Lab 9 service was still occupying `30080`, so I kept the chart default at `30080` but installed the Lab 10 release with `--set service.nodePort=30081` to avoid a collision while preserving the chart defaults required by the lab.

<details>
<summary>Task 2 command output</summary>

```bash
$ helm lint k8s/devops-app-py
==> Linting k8s/devops-app-py
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed

$ helm template devops-app-py k8s/devops-app-py
---
# Source: devops-app-py/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: devops-app-py-service
  labels:
    helm.sh/chart: devops-app-py-0.1.0
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: devops-app-py
    app.kubernetes.io/version: "1.9"
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/part-of: devops-core-s26
spec:
  type: NodePort
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: 5000
      nodePort: 30080
  selector:
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: devops-app-py
---
# Source: devops-app-py/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devops-app-py
  labels:
    helm.sh/chart: devops-app-py-0.1.0
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: devops-app-py
    app.kubernetes.io/version: "1.9"
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/part-of: devops-core-s26
spec:
  replicas: 5
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: devops-app-py
      app.kubernetes.io/instance: devops-app-py
  template:
    metadata:
      labels:
        app.kubernetes.io/name: devops-app-py
        app.kubernetes.io/instance: devops-app-py
        app.kubernetes.io/part-of: devops-core-s26
    spec:
      containers:
        - name: devops-app-py
          image: "localt0aster/devops-app-py:1.9"
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 5000
              protocol: TCP
          env:
            - name: HOST
              value: "0.0.0.0"
            - name: PORT
              value: "5000"
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 2
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 2
          resources:
            limits:
              cpu: 250m
              memory: 256Mi
            requests:
              cpu: 100m
              memory: 128Mi

$ helm install --dry-run --debug test-release k8s/devops-app-py --set service.nodePort=30081
level=WARN msg="--dry-run is deprecated and should be replaced with '--dry-run=client'"
level=DEBUG msg="Original chart version" version=""
level=DEBUG msg="Chart path" path=/home/t0ast/Repos/DevOps-Core-S26/k8s/devops-app-py
level=DEBUG msg="number of dependencies in the chart" chart=devops-app-py dependencies=0
NAME: test-release
LAST DEPLOYED: Thu Apr  2 23:09:12 2026
NAMESPACE: default
STATUS: pending-install
REVISION: 1
DESCRIPTION: Dry run complete
TEST SUITE: None
USER-SUPPLIED VALUES:
service:
  nodePort: 30081

COMPUTED VALUES:
containerPort: 5000
deployment:
  revisionHistoryLimit: 5
  strategy:
    maxSurge: 1
    maxUnavailable: 0
env:
- name: HOST
  value: 0.0.0.0
- name: PORT
  value: "5000"
fullnameOverride: ""
image:
  pullPolicy: IfNotPresent
  repository: localt0aster/devops-app-py
  tag: 1.9
livenessProbe:
  failureThreshold: 3
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 2
nameOverride: ""
partOf: devops-core-s26
podAnnotations: {}
podLabels: {}
readinessProbe:
  failureThreshold: 3
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 2
replicaCount: 5
resources:
  limits:
    cpu: 250m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
service:
  nodePort: 30081
  port: 80
  targetPort: 5000
  type: NodePort

HOOKS:
MANIFEST:
---
# Source: devops-app-py/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: test-release-devops-app-py-service
  labels:
    helm.sh/chart: devops-app-py-0.1.0
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: test-release
    app.kubernetes.io/version: "1.9"
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/part-of: devops-core-s26
spec:
  type: NodePort
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: 5000
      nodePort: 30081
  selector:
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: test-release
---
# Source: devops-app-py/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-release-devops-app-py
  labels:
    helm.sh/chart: devops-app-py-0.1.0
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: test-release
    app.kubernetes.io/version: "1.9"
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/part-of: devops-core-s26
spec:
  replicas: 5
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: devops-app-py
      app.kubernetes.io/instance: test-release
  template:
    metadata:
      labels:
        app.kubernetes.io/name: devops-app-py
        app.kubernetes.io/instance: test-release
        app.kubernetes.io/part-of: devops-core-s26
    spec:
      containers:
        - name: devops-app-py
          image: "localt0aster/devops-app-py:1.9"
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 5000
              protocol: TCP
          env:
            - name: HOST
              value: "0.0.0.0"
            - name: PORT
              value: "5000"
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 2
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 2
          resources:
            limits:
              cpu: 250m
              memory: 256Mi
            requests:
              cpu: 100m
              memory: 128Mi

NOTES:
1. Review the release:
  helm status test-release -n default

2. Forward the service locally:
  kubectl port-forward svc/test-release-devops-app-py-service 8080:80 -n default

3. Verify the application:
  curl -fsSL http://127.0.0.1:8080/health
  curl -fsSL http://127.0.0.1:8080/ready

$ helm install lab10-devops-app-py k8s/devops-app-py --set service.nodePort=30081
NAME: lab10-devops-app-py
LAST DEPLOYED: Thu Apr  2 23:09:12 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
1. Review the release:
  helm status lab10-devops-app-py -n default

2. Forward the service locally:
  kubectl port-forward svc/lab10-devops-app-py-service 8080:80 -n default

3. Verify the application:
  curl -fsSL http://127.0.0.1:8080/health
  curl -fsSL http://127.0.0.1:8080/ready

$ kubectl rollout status deployment/lab10-devops-app-py --timeout=240s
Waiting for deployment "lab10-devops-app-py" rollout to finish: 0 of 5 updated replicas are available...
Waiting for deployment "lab10-devops-app-py" rollout to finish: 1 of 5 updated replicas are available...
Waiting for deployment "lab10-devops-app-py" rollout to finish: 2 of 5 updated replicas are available...
Waiting for deployment "lab10-devops-app-py" rollout to finish: 3 of 5 updated replicas are available...
Waiting for deployment "lab10-devops-app-py" rollout to finish: 4 of 5 updated replicas are available...
deployment "lab10-devops-app-py" successfully rolled out

$ helm list -A
NAME               	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART              	APP VERSION
lab10-devops-app-py	default  	1       	2026-04-02 23:09:12.132768347 +0300 +03	deployed	devops-app-py-0.1.0	1.9

$ kubectl get deploy,svc,pods -l app.kubernetes.io/instance=lab10-devops-app-py -o wide
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS      IMAGES                               SELECTOR
deployment.apps/lab10-devops-app-py   5/5     5            5           7s    devops-app-py   localt0aster/devops-app-py:1.9   app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                  TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/lab10-devops-app-py-service   NodePort   10.96.60.48   <none>        80:30081/TCP   7s    app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                       READY   STATUS    RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
pod/lab10-devops-app-py-7b7dbf4648-6k55b   1/1     Running   0          7s    10.244.0.60   minikube   <none>           <none>
pod/lab10-devops-app-py-7b7dbf4648-fz8j2   1/1     Running   0          7s    10.244.0.58   minikube   <none>           <none>
pod/lab10-devops-app-py-7b7dbf4648-l5fdj   1/1     Running   0          7s    10.244.0.56   minikube   <none>           <none>
pod/lab10-devops-app-py-7b7dbf4648-sdklz   1/1     Running   0          7s    10.244.0.57   minikube   <none>           <none>
pod/lab10-devops-app-py-7b7dbf4648-zp9dt   1/1     Running   0          7s    10.244.0.59   minikube   <none>           <none>

$ kubectl port-forward svc/lab10-devops-app-py-service 18082:80
Forwarding from 127.0.0.1:18082 -> 5000
Forwarding from [::1]:18082 -> 5000

$ curl -fsSL http://127.0.0.1:18082 | jq .
{
  "endpoints": [
    {
      "description": "Service information.",
      "method": "GET",
      "path": "/"
    },
    {
      "description": "Health check.",
      "method": "GET",
      "path": "/health"
    },
    {
      "description": "Prometheus metrics.",
      "method": "GET",
      "path": "/metrics"
    },
    {
      "description": "Readiness check.",
      "method": "GET",
      "path": "/ready"
    }
  ],
  "request": {
    "client_ip": "127.0.0.1",
    "method": "GET",
    "path": "/",
    "user_agent": "curl/8.19.0"
  },
  "runtime": {
    "human": "0 hours, 0 minutes",
    "seconds": 12
  },
  "service": {
    "description": "DevOps course info service",
    "framework": "Flask",
    "name": "devops-info-service",
    "version": "1.8.0"
  },
  "system": {
    "architecture": "x86_64",
    "cpu_count": 8,
    "hostname": "lab10-devops-app-py-7b7dbf4648-6k55b",
    "platform": "Linux",
    "platform_version": "Alpine Linux v3.23",
    "python_version": "3.14.3"
  }
}

$ curl -fsSL http://127.0.0.1:18082/health | jq .
{
  "status": "healthy",
  "timestamp": "2026-04-02T20:09:31.062442+00:00",
  "uptime_seconds": 12
}

$ curl -fsSL http://127.0.0.1:18082/ready | jq .
{
  "status": "ready",
  "timestamp": "2026-04-02T20:09:31.100199+00:00",
  "uptime_seconds": 13
}
```

</details>

## Task 3 - Multi-Environment Support

I added two environment-specific values files to the chart: `values-dev.yaml` for a lightweight local deployment and `values-prod.yaml` for a more production-shaped configuration. The dev profile uses a single replica, smaller CPU and memory reservations, `APP_ENV=development`, and the `localt0aster/devops-app-py:1.9-dev` image on a `NodePort` service. The prod profile raises the deployment to 3 replicas, increases resource requests and limits, switches `APP_ENV=production`, uses the `localt0aster/devops-app-py:1.9` image, and changes the service type to `LoadBalancer`.

I tested the environment flow on the real release instead of only rendering templates. First I reinstalled `lab10-devops-app-py` with the dev values, verified the single-replica `1.9-dev` deployment, and then upgraded the same release with the prod values. The service type changed to `LoadBalancer` and the Deployment converged to 3 ready Pods. In this minikube setup the external IP stayed `<pending>`, which is expected without cloud load-balancer integration, so I verified the upgraded release with `kubectl port-forward` and `curl ... | jq .` against `/ready`.

<details>
<summary>Task 3 command output</summary>

```bash
$ helm uninstall lab10-devops-app-py
release "lab10-devops-app-py" uninstalled

$ helm install lab10-devops-app-py k8s/devops-app-py -f k8s/devops-app-py/values-dev.yaml --wait=watcher --wait-for-jobs --timeout 240s
NAME: lab10-devops-app-py
LAST DEPLOYED: Fri Apr  3 01:40:19 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
1. Review the release:
  helm status lab10-devops-app-py -n default

2. Forward the service locally:
  kubectl port-forward svc/lab10-devops-app-py-service 8080:80 -n default

3. Verify the application:
  curl -fsSL http://127.0.0.1:8080/health | jq
  curl -fsSL http://127.0.0.1:8080/ready | jq

$ helm get values lab10-devops-app-py --all
COMPUTED VALUES:
containerPort: 5000
deployment:
  revisionHistoryLimit: 2
  strategy:
    maxSurge: 1
    maxUnavailable: 0
env:
- name: HOST
  value: 0.0.0.0
- name: PORT
  value: "5000"
- name: APP_ENV
  value: development
fullnameOverride: ""
hooks:
  postInstall:
    deletePolicy: before-hook-creation,hook-succeeded
    enabled: true
    image:
      pullPolicy: IfNotPresent
      repository: curlimages/curl
      tag: 8.12.1
    maxAttempts: 20
    retryIntervalSeconds: 3
    weight: 5
  preInstall:
    deletePolicy: before-hook-creation,hook-succeeded
    enabled: true
    image:
      pullPolicy: IfNotPresent
      repository: busybox
      tag: 1.37.0
    weight: -5
image:
  pullPolicy: IfNotPresent
  repository: localt0aster/devops-app-py
  tag: 1.9-dev
livenessProbe:
  failureThreshold: 3
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
nameOverride: ""
partOf: devops-core-s26
podAnnotations: {}
podLabels:
  environment: dev
readinessProbe:
  failureThreshold: 3
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 3
  periodSeconds: 5
  timeoutSeconds: 2
replicaCount: 1
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi
service:
  nodePort: 30081
  port: 80
  targetPort: 5000
  type: NodePort

$ kubectl get deploy,svc,pods -l app.kubernetes.io/instance=lab10-devops-app-py -o wide
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS      IMAGES                               SELECTOR
deployment.apps/lab10-devops-app-py   1/1     1            1           23s   devops-app-py   localt0aster/devops-app-py:1.9-dev   app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                  TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/lab10-devops-app-py-service   NodePort   10.102.64.255   <none>        80:30081/TCP   23s   app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                       READY   STATUS    RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
pod/lab10-devops-app-py-7fd54dc44b-5lndl   1/1     Running   0          23s   10.244.0.62   minikube   <none>           <none>

$ helm upgrade lab10-devops-app-py k8s/devops-app-py -f k8s/devops-app-py/values-prod.yaml --wait=watcher --timeout 240s
Release "lab10-devops-app-py" has been upgraded. Happy Helming!
NAME: lab10-devops-app-py
LAST DEPLOYED: Fri Apr  3 01:40:53 2026
NAMESPACE: default
STATUS: deployed
REVISION: 2
DESCRIPTION: Upgrade complete
TEST SUITE: None
NOTES:
1. Review the release:
  helm status lab10-devops-app-py -n default

2. Forward the service locally:
  kubectl port-forward svc/lab10-devops-app-py-service 8080:80 -n default

3. Verify the application:
  curl -fsSL http://127.0.0.1:8080/health | jq
  curl -fsSL http://127.0.0.1:8080/ready | jq

$ kubectl rollout status deployment/lab10-devops-app-py --timeout=240s
deployment "lab10-devops-app-py" successfully rolled out

$ helm get values lab10-devops-app-py --all
COMPUTED VALUES:
containerPort: 5000
deployment:
  revisionHistoryLimit: 10
  strategy:
    maxSurge: 1
    maxUnavailable: 0
env:
- name: HOST
  value: 0.0.0.0
- name: PORT
  value: "5000"
- name: APP_ENV
  value: production
fullnameOverride: ""
hooks:
  postInstall:
    deletePolicy: before-hook-creation,hook-succeeded
    enabled: true
    image:
      pullPolicy: IfNotPresent
      repository: curlimages/curl
      tag: 8.12.1
    maxAttempts: 20
    retryIntervalSeconds: 3
    weight: 5
  preInstall:
    deletePolicy: before-hook-creation,hook-succeeded
    enabled: true
    image:
      pullPolicy: IfNotPresent
      repository: busybox
      tag: 1.37.0
    weight: -5
image:
  pullPolicy: IfNotPresent
  repository: localt0aster/devops-app-py
  tag: "1.9"
livenessProbe:
  failureThreshold: 3
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 5
  timeoutSeconds: 2
nameOverride: ""
partOf: devops-core-s26
podAnnotations: {}
podLabels:
  environment: prod
readinessProbe:
  failureThreshold: 3
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 10
  periodSeconds: 3
  timeoutSeconds: 2
replicaCount: 3
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi
service:
  nodePort: 30081
  port: 80
  targetPort: 5000
  type: LoadBalancer

$ kubectl get deploy,svc,pods -l app.kubernetes.io/instance=lab10-devops-app-py -o wide
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS      IMAGES                           SELECTOR
deployment.apps/lab10-devops-app-py   3/3     3            3           65s   devops-app-py   localt0aster/devops-app-py:1.9   app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                  TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/lab10-devops-app-py-service   LoadBalancer   10.102.64.255   <pending>     80:30081/TCP   65s   app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                       READY   STATUS        RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
pod/lab10-devops-app-py-67694d9f5c-57h24   1/1     Running       0          22s   10.244.0.67   minikube   <none>           <none>
pod/lab10-devops-app-py-67694d9f5c-7scvn   1/1     Running       0          41s   10.244.0.64   minikube   <none>           <none>
pod/lab10-devops-app-py-67694d9f5c-tk2kt   1/1     Running       0          11s   10.244.0.68   minikube   <none>           <none>
pod/lab10-devops-app-py-7fd54dc44b-5lndl   1/1     Terminating   0          65s   10.244.0.62   minikube   <none>           <none>

$ kubectl port-forward svc/lab10-devops-app-py-service 18083:80
Forwarding from 127.0.0.1:18083 -> 5000
Forwarding from [::1]:18083 -> 5000

$ curl -fsSL http://127.0.0.1:18083/ready | jq .
{
  "status": "ready",
  "timestamp": "2026-04-02T22:41:38.602170+00:00",
  "uptime_seconds": 33
}
```

</details>

## Task 4 - Chart Hooks

I added two lifecycle hook Jobs under `templates/hooks/`. The pre-install hook is a small validation job based on `busybox`, and the post-install hook is a smoke test based on `curlimages/curl` that checks the release-local Service on `/ready`. Their weights are `-5` and `5` respectively, so the validation step runs first and the smoke test runs after the workload is installed. Both hooks use the deletion policy `before-hook-creation,hook-succeeded` so repeated installs do not accumulate stale Jobs.

Verification happened in two layers. First, a dry run showed both hook manifests rendering under Helm’s `HOOKS:` section with the expected annotations. Then the real dev installation produced the expected Kubernetes events for both Jobs, including `Completed` on pre-install and post-install. After completion, `kubectl get jobs -A` returned no resources and no hook pods remained, which confirmed the cleanup policy worked in practice.

<details>
<summary>Task 4 command output</summary>

```bash
$ helm lint k8s/devops-app-py
==> Linting k8s/devops-app-py
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed

$ helm install --dry-run=client --debug hook-preview k8s/devops-app-py -f k8s/devops-app-py/values-dev.yaml | rg -n -C 3 'Source: devops-app-py/templates/hooks|kind: Job|name: hook-preview-devops-app-py-(pre-install|post-install)|helm.sh/hook|helm.sh/hook-weight|helm.sh/hook-delete-policy'
124-
125-HOOKS:
126----
127:# Source: devops-app-py/templates/hooks/post-install-job.yaml
128-apiVersion: batch/v1
129:kind: Job
130-metadata:
131:  name: hook-preview-devops-app-py-post-install
132-  labels:
133-    helm.sh/chart: devops-app-py-0.2.0
134-    app.kubernetes.io/name: devops-app-py
--
138-    app.kubernetes.io/part-of: devops-core-s26
139-    app.kubernetes.io/component: hook
140-  annotations:
141:    "helm.sh/hook": post-install
142:    "helm.sh/hook-weight": "5"
143:    "helm.sh/hook-delete-policy": "before-hook-creation,hook-succeeded"
144-spec:
145-  backoffLimit: 0
146-  template:
--
177-              echo "Smoke test failed for ${url}"
178-              exit 1
179----
180:# Source: devops-app-py/templates/hooks/pre-install-job.yaml
181-apiVersion: batch/v1
182:kind: Job
183-metadata:
184:  name: hook-preview-devops-app-py-pre-install
185-  labels:
186-    helm.sh/chart: devops-app-py-0.2.0
187-    app.kubernetes.io/name: devops-app-py
--
191-    app.kubernetes.io/part-of: devops-core-s26
192-    app.kubernetes.io/component: hook
193-  annotations:
194:    "helm.sh/hook": pre-install
195:    "helm.sh/hook-weight": "-5"
196:    "helm.sh/hook-delete-policy": "before-hook-creation,hook-succeeded"
197-spec:
198-  backoffLimit: 0
199-  template:

$ kubectl get events -A --sort-by=.metadata.creationTimestamp | rg 'lab10-devops-app-py-(pre-install|post-install)|Job completed|Created pod: lab10-devops-app-py-(pre-install|post-install)'
default     112s        Normal    SuccessfulCreate    job/lab10-devops-app-py-pre-install          Created pod: lab10-devops-app-py-pre-install-gl882
default     111s        Normal    Scheduled           pod/lab10-devops-app-py-pre-install-gl882    Successfully assigned default/lab10-devops-app-py-pre-install-gl882 to minikube
default     111s        Normal    Pulling             pod/lab10-devops-app-py-pre-install-gl882    Pulling image "busybox:1.37.0"
default     107s        Normal    Pulled              pod/lab10-devops-app-py-pre-install-gl882    Successfully pulled image "busybox:1.37.0" in 4.711s (4.711s including waiting). Image size: 4421246 bytes.
default     107s        Normal    Created             pod/lab10-devops-app-py-pre-install-gl882    Container created
default     106s        Normal    Started             pod/lab10-devops-app-py-pre-install-gl882    Container started
default     101s        Normal    Completed           job/lab10-devops-app-py-pre-install          Job completed
default     84s         Normal    SuccessfulCreate    job/lab10-devops-app-py-post-install         Created pod: lab10-devops-app-py-post-install-9jpjt
default     83s         Normal    Scheduled           pod/lab10-devops-app-py-post-install-9jpjt   Successfully assigned default/lab10-devops-app-py-post-install-9jpjt to minikube
default     83s         Normal    Pulled              pod/lab10-devops-app-py-post-install-9jpjt   Container image "curlimages/curl:8.12.1" already present on machine and can be accessed by the pod
default     83s         Normal    Created             pod/lab10-devops-app-py-post-install-9jpjt   Container created
default     83s         Normal    Started             pod/lab10-devops-app-py-post-install-9jpjt   Container started
default     78s         Normal    Completed           job/lab10-devops-app-py-post-install         Job completed

$ kubectl get jobs -A 2>&1
No resources found

$ kubectl get pods -A | rg 'lab10-devops-app-py-(pre-install|post-install)' || true
```

</details>

## Task 5 - Documentation

This section completes the documentation requirement for the Helm chart itself. The course asks for `k8s/HELM.md`; in this repo that file is kept as a compatibility entry point, while the detailed write-up lives here in `k8s/docs/LAB10.md` so the module root does not turn into a transcript dump.

### Chart Overview

The chart lives in `k8s/devops-app-py` and is split into a small set of focused files:

- `Chart.yaml`: chart metadata, chart version, and app version.
- `values.yaml`: common defaults shared by all environments.
- `values-dev.yaml`: local development override with `1` replica, smaller resources, `NodePort`, and `1.9-dev`.
- `values-prod.yaml`: production-shaped override with `3` replicas, larger resources, `LoadBalancer`, and `1.9`.
- `templates/_helpers.tpl`: shared naming and label helpers, including service and hook job names.
- `templates/deployment.yaml`: the main application Deployment template.
- `templates/service.yaml`: the Service template, supporting both `NodePort` and `LoadBalancer`.
- `templates/hooks/pre-install-job.yaml`: validation job that runs before install.
- `templates/hooks/post-install-job.yaml`: smoke test job that runs after install.
- `templates/NOTES.txt`: post-install usage hints.

The values strategy is layered: keep sensible defaults in `values.yaml`, then use environment overlays to change only what differs between dev and prod. That keeps templates stable and pushes configuration changes to values files instead of templating conditionals everywhere.

### Configuration Guide

The most important values are:

- `replicaCount`: controls pod count for each environment.
- `image.repository` and `image.tag`: define which application image is deployed.
- `service.type`, `service.port`, `service.targetPort`, and `service.nodePort`: define exposure strategy.
- `resources.requests` and `resources.limits`: shape scheduling and runtime ceilings.
- `livenessProbe` and `readinessProbe`: keep health checks configurable without removing them.
- `env`: injects runtime environment variables like `HOST`, `PORT`, and `APP_ENV`.
- `hooks.preInstall.*` and `hooks.postInstall.*`: configure hook enablement, weight, deletion policy, image, and retry behavior.

Example usage:

```bash
# Development installation
helm install lab10-devops-app-py k8s/devops-app-py \
  -f k8s/devops-app-py/values-dev.yaml \
  --wait=watcher \
  --wait-for-jobs

# Upgrade the same release to the production profile
helm upgrade lab10-devops-app-py k8s/devops-app-py \
  -f k8s/devops-app-py/values-prod.yaml \
  --wait=watcher

# Override a specific value without editing files
helm upgrade lab10-devops-app-py k8s/devops-app-py \
  -f k8s/devops-app-py/values-prod.yaml \
  --set replicaCount=4
```

### Hook Implementation

Two hooks are implemented:

- Pre-install hook: a `busybox` validation job that records the release name, namespace, image tag, and replica count before installation proceeds.
- Post-install hook: a `curlimages/curl` smoke test job that polls `http://<service>/ready` until it gets HTTP `200` or times out.

Execution order is controlled by weights:

- `pre-install`: weight `-5`
- `post-install`: weight `5`

Deletion is handled by `before-hook-creation,hook-succeeded`, which means Helm removes old hook resources before recreating them and cleans up successful Jobs afterward. The cluster evidence below confirms that no hook Jobs remain after completion.

### Installation Evidence

<details>
<summary>Current chart and release evidence</summary>

```bash
$ find k8s/devops-app-py -maxdepth 3 -type f | sort
k8s/devops-app-py/.helmignore
k8s/devops-app-py/Chart.yaml
k8s/devops-app-py/templates/NOTES.txt
k8s/devops-app-py/templates/_helpers.tpl
k8s/devops-app-py/templates/deployment.yaml
k8s/devops-app-py/templates/hooks/post-install-job.yaml
k8s/devops-app-py/templates/hooks/pre-install-job.yaml
k8s/devops-app-py/templates/service.yaml
k8s/devops-app-py/values-dev.yaml
k8s/devops-app-py/values-prod.yaml
k8s/devops-app-py/values.yaml

$ helm list -A
NAME               	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART              	APP VERSION
lab10-devops-app-py	default  	2       	2026-04-03 01:40:53.968813438 +0300 +03	deployed	devops-app-py-0.2.0	1.9

$ helm history lab10-devops-app-py
REVISION	UPDATED                 	STATUS    	CHART              	APP VERSION	DESCRIPTION
1       	Fri Apr  3 01:40:19 2026	superseded	devops-app-py-0.2.0	1.9        	Install complete
2       	Fri Apr  3 01:40:53 2026	deployed  	devops-app-py-0.2.0	1.9        	Upgrade complete

$ kubectl get all -l app.kubernetes.io/instance=lab10-devops-app-py -o wide
NAME                                       READY   STATUS    RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
pod/lab10-devops-app-py-67694d9f5c-57h24   1/1     Running   0          14m   10.244.0.67   minikube   <none>           <none>
pod/lab10-devops-app-py-67694d9f5c-7scvn   1/1     Running   0          14m   10.244.0.64   minikube   <none>           <none>
pod/lab10-devops-app-py-67694d9f5c-tk2kt   1/1     Running   0          14m   10.244.0.68   minikube   <none>           <none>

NAME                                  TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/lab10-devops-app-py-service   LoadBalancer   10.102.64.255   <pending>     80:30081/TCP   15m   app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS      IMAGES                           SELECTOR
deployment.apps/lab10-devops-app-py   3/3     3            3           15m   devops-app-py   localt0aster/devops-app-py:1.9   app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                             DESIRED   CURRENT   READY   AGE   CONTAINERS      IMAGES                               SELECTOR
replicaset.apps/lab10-devops-app-py-67694d9f5c   3         3         3       14m   devops-app-py   localt0aster/devops-app-py:1.9       app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py,pod-template-hash=67694d9f5c
replicaset.apps/lab10-devops-app-py-7fd54dc44b   0         0         0       15m   devops-app-py   localt0aster/devops-app-py:1.9-dev   app.kubernetes.io/instance=lab10-devops-app-py,app.kubernetes.io/name=devops-app-py,pod-template-hash=7fd54dc44b

$ kubectl get jobs -A 2>&1
No resources found
```

</details>

### Operations

1. Install the development profile:

   ```bash
   helm install lab10-devops-app-py k8s/devops-app-py \
     -f k8s/devops-app-py/values-dev.yaml \
     --wait=watcher \
     --wait-for-jobs \
     --timeout 240s
   ```

2. Upgrade to the production profile:

   ```bash
   helm upgrade lab10-devops-app-py k8s/devops-app-py \
     -f k8s/devops-app-py/values-prod.yaml \
     --wait=watcher \
     --timeout 240s
   ```

3. Inspect and troubleshoot the release:

   ```bash
   helm list -A
   helm history lab10-devops-app-py
   helm get values lab10-devops-app-py --all
   kubectl get all -l app.kubernetes.io/instance=lab10-devops-app-py -o wide
   ```

4. Roll back or remove the release:

   ```bash
   helm rollback lab10-devops-app-py 1
   helm uninstall lab10-devops-app-py
   ```

### Testing & Validation

Validation was performed at several levels:

- Static validation: `helm lint` passed with only the non-blocking `icon is recommended` note.
- Render validation: `helm template ... -f values-prod.yaml` showed `Service`, `Deployment`, and both hook `Job` resources, with `type: LoadBalancer`, `replicas: 3`, and the expected hook annotations.
- Dry-run validation: Task 4’s `helm install --dry-run=client --debug` output showed both hooks under the `HOOKS:` section before any cluster changes were applied.
- Runtime validation: Task 3 verified the dev install, the prod upgrade, and service accessibility via `kubectl port-forward` and `curl ... | jq .`.
- Hook validation: Task 4 confirmed both Jobs completed and were deleted afterward.

One limitation is specific to the local minikube environment: after the prod upgrade, the `LoadBalancer` service stayed at `EXTERNAL-IP <pending>`. That is expected on this cluster without an additional load-balancer implementation, so the authoritative accessibility check remained `kubectl port-forward` instead of a cloud-style public IP.
