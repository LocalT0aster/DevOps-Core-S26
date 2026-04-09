# Kubernetes Lab 11 - Kubernetes Secrets and HashiCorp Vault

I started by hard-resetting the local Kubernetes setup and recreating the cluster with `minikube` on the Docker driver. I did not document the pre-cleanup leftovers because this lab run was intentionally destructive and the goal was to produce evidence only from the fresh environment. All usernames, passwords, API keys, Vault tokens, JWTs, and base64 secret payloads are redacted in this write-up.

## Fresh Cluster Baseline

<details>
<summary><code>Fresh cluster bootstrap</code></summary>

```text
$ kubectl config current-context
minikube

$ minikube status
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured


$ kubectl cluster-info
Kubernetes control plane is running at https://192.168.49.2:8443
CoreDNS is running at https://192.168.49.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.

$ kubectl get nodes -o wide
NAME       STATUS   ROLES           AGE     VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION      CONTAINER-RUNTIME
minikube   Ready    control-plane   2m14s   v1.35.1   192.168.49.2   <none>        Debian GNU/Linux 12 (bookworm)   6.19.11-1-cachyos   docker://29.2.1

$ kubectl get node minikube -o jsonpath="{.status.nodeInfo.containerRuntimeVersion}{\"\\n\"}"
docker://29.2.1
```

</details>

## Task 1 - Kubernetes Secrets Fundamentals

I created `app-credentials` imperatively with `kubectl create secret generic`, then verified the stored object and decoded both keys. The important security point is that Kubernetes Secrets are base64-encoded for transport and manifest representation, but base64 is not encryption. Anyone who can read the Secret object can decode it immediately.

By default, Kubernetes does not give Secrets meaningful confidentiality at rest unless the cluster administrator enables etcd encryption at rest. In production I would combine three controls: enable etcd encryption, restrict Secret access with RBAC, and use an external secret manager when credentials need centralized policy, auditing, or rotation.

<details>
<summary><code>kubectl create secret generic app-credentials</code></summary>

```bash
$ kubectl create secret generic app-credentials --from-literal=username="$LAB11_DEMO_USERNAME" --from-literal=password="$LAB11_DEMO_PASSWORD"
secret/app-credentials created
```

</details>

<details>
<summary><code>kubectl get secret app-credentials -o yaml</code> (redacted)</summary>

```yaml
apiVersion: v1
data:
  password: <redacted-base64>
  username: <redacted-base64>
kind: Secret
metadata:
  creationTimestamp: "2026-04-09T22:59:08Z"
  name: app-credentials
  namespace: default
  resourceVersion: "511"
  uid: a02c09dd-5ff9-4eba-b431-57ce64edb215
type: Opaque
```

</details>

<details>
<summary><code>base64 -d</code> proof for both keys</summary>

```text
$ kubectl get secret app-credentials -o jsonpath="{.data.username}" | base64 -d
username=<redacted>

$ kubectl get secret app-credentials -o jsonpath="{.data.password}" | base64 -d
password=<redacted>
```

</details>

## Task 2 - Helm-Managed Secrets

I extended the Lab 10 chart instead of bolting on one-off manifests. The chart now has a dedicated `templates/secrets.yaml` and `templates/serviceaccount.yaml`, plus new values blocks for `secrets`, `serviceAccount`, and `vault`. Real demo values were supplied from untracked files under `/tmp/lab11/`; tracked YAML keeps placeholder defaults only.

I also preserved the resource management from Lab 10. Requests reserve the minimum capacity the Pod needs to be scheduled predictably, while limits cap runaway usage. For the dev profile I kept `50m` CPU and `64Mi` memory requests with `100m` CPU and `128Mi` memory limits, which is appropriate for a single-replica local Flask/Gunicorn deployment in `minikube`.

For the bonus DRY requirement, I moved the plain environment variable list into a named helper (`devops-app-py.envVars`) and added a second helper (`devops-app-py.vaultAnnotations`) so the Deployment template stays readable when Vault injection is enabled.

<details>
<summary><code>find k8s/devops-app-py -maxdepth 3 -type f | sort</code></summary>

```text
k8s/devops-app-py/.helmignore
k8s/devops-app-py/Chart.yaml
k8s/devops-app-py/templates/NOTES.txt
k8s/devops-app-py/templates/_helpers.tpl
k8s/devops-app-py/templates/deployment.yaml
k8s/devops-app-py/templates/hooks/post-install-job.yaml
k8s/devops-app-py/templates/hooks/pre-install-job.yaml
k8s/devops-app-py/templates/secrets.yaml
k8s/devops-app-py/templates/service.yaml
k8s/devops-app-py/templates/serviceaccount.yaml
k8s/devops-app-py/values-dev.yaml
k8s/devops-app-py/values-prod.yaml
k8s/devops-app-py/values.yaml
```

</details>

<details>
<summary><code>helm lint</code> and rendered manifest excerpts</summary>

```bash
==> Linting k8s/devops-app-py
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

```yaml
# Source: devops-app-py/templates/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: lab11-devops-app-py
  labels:
    helm.sh/chart: devops-app-py-0.3.0
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: lab11-devops-app-py
    app.kubernetes.io/version: "1.9-dev"
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/part-of: devops-core-s26
---

# Source: devops-app-py/templates/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: lab11-devops-app-py-secret
  labels:
    helm.sh/chart: devops-app-py-0.3.0
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: lab11-devops-app-py
    app.kubernetes.io/version: "1.9-dev"
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/part-of: devops-core-s26
type: Opaque
stringData:
  APP_USERNAME: "<redacted-username>"
  APP_PASSWORD: "<redacted-password>"
---

# Source: devops-app-py/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lab11-devops-app-py
  labels:
    helm.sh/chart: devops-app-py-0.3.0
    app.kubernetes.io/name: devops-app-py
    app.kubernetes.io/instance: lab11-devops-app-py
    app.kubernetes.io/version: "1.9-dev"
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/part-of: devops-core-s26
spec:
  replicas: 1
  revisionHistoryLimit: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: devops-app-py
      app.kubernetes.io/instance: lab11-devops-app-py
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "lab11-devops-app-py"
        vault.hashicorp.com/agent-inject-secret-config: "secret/data/lab11/devops-app-py"
        vault.hashicorp.com/agent-inject-file-config: "app-config.env"
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "secret/data/lab11/devops-app-py" -}}
          APP_USERNAME={{ .Data.data.APP_USERNAME }}
          APP_PASSWORD={{ .Data.data.APP_PASSWORD }}
          APP_API_KEY={{ .Data.data.APP_API_KEY }}
          {{- end }}
      labels:
        app.kubernetes.io/name: devops-app-py
        app.kubernetes.io/instance: lab11-devops-app-py
        app.kubernetes.io/part-of: devops-core-s26
        environment: dev
    spec:
      serviceAccountName: lab11-devops-app-py
      containers:
        - name: devops-app-py
          image: "localt0aster/devops-app-py:1.9-dev"
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 5000
              protocol: TCP
          envFrom:
            - secretRef:
                name: lab11-devops-app-py-secret
          env:
            - name: HOST
              value: "0.0.0.0"
            - name: PORT
              value: "5000"
            - name: APP_ENV
              value: "development"
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 2
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
            timeoutSeconds: 2
          resources:
            limits:
              cpu: 100m
              memory: 128Mi
            requests:
              cpu: 50m
              memory: 64Mi
---
```

</details>

<details>
<summary><code>helm upgrade --install lab11-devops-app-py ...</code></summary>

```bash
$ helm upgrade --install lab11-devops-app-py k8s/devops-app-py -f k8s/devops-app-py/values-dev.yaml -f /tmp/lab11/app-secrets.values.yaml --wait=watcher --wait-for-jobs --timeout 300s
Release "lab11-devops-app-py" does not exist. Installing it now.
NAME: lab11-devops-app-py
LAST DEPLOYED: Fri Apr 10 02:00:31 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
1. Review the release:
  helm status lab11-devops-app-py -n default

2. Forward the service locally:
  kubectl port-forward svc/lab11-devops-app-py-service 8080:80 -n default

3. Verify the application:
  curl -fsSL http://127.0.0.1:8080/health | jq
  curl -fsSL http://127.0.0.1:8080/ready | jq

$ kubectl rollout status deployment/lab11-devops-app-py --timeout=300s
deployment "lab11-devops-app-py" successfully rolled out

$ kubectl get deploy,svc,pods,secret -l app.kubernetes.io/instance=lab11-devops-app-py -o wide
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS      IMAGES                               SELECTOR
deployment.apps/lab11-devops-app-py   1/1     1            1           38s   devops-app-py   localt0aster/devops-app-py:1.9-dev   app.kubernetes.io/instance=lab11-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                  TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/lab11-devops-app-py-service   NodePort   10.108.159.118   <none>        80:30081/TCP   38s   app.kubernetes.io/instance=lab11-devops-app-py,app.kubernetes.io/name=devops-app-py

NAME                                       READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
pod/lab11-devops-app-py-578786c7fb-f8zzz   1/1     Running   0          38s   10.244.0.4   minikube   <none>           <none>

NAME                                TYPE     DATA   AGE
secret/lab11-devops-app-py-secret   Opaque   2      38s
```

</details>

<details>
<summary><code>kubectl exec ... printenv</code> (redacted)</summary>

```text
$ kubectl exec "$POD_NAME" -- printenv | rg "^APP_(USERNAME|PASSWORD)=" | sed -E "s/=.*/=<redacted>/"
APP_USERNAME=<redacted>
APP_PASSWORD=<redacted>
```

</details>

<details>
<summary><code>kubectl describe pod</code> showing Secret reference instead of cleartext</summary>

```text
Name:             lab11-devops-app-py-578786c7fb-f8zzz
Namespace:        default
Priority:         0
Service Account:  lab11-devops-app-py
Node:             minikube/192.168.49.2
Start Time:       Fri, 10 Apr 2026 02:00:43 +0300
Labels:           app.kubernetes.io/instance=lab11-devops-app-py
                  app.kubernetes.io/name=devops-app-py
                  app.kubernetes.io/part-of=devops-core-s26
                  environment=dev
                  pod-template-hash=578786c7fb
Annotations:      <none>
Status:           Running
IP:               10.244.0.4
IPs:
  IP:           10.244.0.4
Controlled By:  ReplicaSet/lab11-devops-app-py-578786c7fb
Containers:
  devops-app-py:
    Container ID:   docker://c243351e2d85929b21b521a6cb6ad023801ceb1d4c608e5ebdbb836146ca47d2
    Image:          localt0aster/devops-app-py:1.9-dev
    Image ID:       docker-pullable://localt0aster/devops-app-py@sha256:2f3a987db91b7327ed30da86a6cfb8358cb720e2f968c7b326a031d31503f765
    Port:           5000/TCP (http)
    Host Port:      0/TCP (http)
    State:          Running
      Started:      Fri, 10 Apr 2026 02:00:53 +0300
    Ready:          True
    Restart Count:  0
    Limits:
      cpu:     100m
      memory:  128Mi
    Requests:
      cpu:      50m
      memory:   64Mi
    Liveness:   http-get http://:http/health delay=5s timeout=2s period=10s #success=1 #failure=3
    Readiness:  http-get http://:http/ready delay=3s timeout=2s period=5s #success=1 #failure=3
    Environment Variables from:
      lab11-devops-app-py-secret  Secret  Optional: false
    Environment:
      HOST:     0.0.0.0
      PORT:     5000
      APP_ENV:  development
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-zvfx6 (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
Volumes:
  kube-api-access-zvfx6:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   Burstable
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  52s                default-scheduler  Successfully assigned default/lab11-devops-app-py-578786c7fb-f8zzz to minikube
  Normal   Pulling    52s                kubelet            spec.containers{devops-app-py}: Pulling image "localt0aster/devops-app-py:1.9-dev"
  Normal   Pulled     43s                kubelet            spec.containers{devops-app-py}: Successfully pulled image "localt0aster/devops-app-py:1.9-dev" in 9.083s (9.083s including waiting). Image size: 138919242 bytes.
  Normal   Created    42s                kubelet            spec.containers{devops-app-py}: Container created
  Normal   Started    42s                kubelet            spec.containers{devops-app-py}: Container started
  Warning  Unhealthy  30s                kubelet            spec.containers{devops-app-py}: Liveness probe failed: Get "http://10.244.0.4:5000/health": context deadline exceeded (Client.Timeout exceeded while awaiting headers)
  Warning  Unhealthy  28s (x2 over 33s)  kubelet            spec.containers{devops-app-py}: Readiness probe failed: Get "http://10.244.0.4:5000/ready": context deadline exceeded (Client.Timeout exceeded while awaiting headers)
```

</details>

The key verification point is the difference between the two views: inside the container the variables exist and are usable, while `kubectl describe pod` only exposes the Secret reference (`Environment Variables from:`) rather than the cleartext values.

## Task 3 - HashiCorp Vault Integration

I installed Vault with the official Helm chart in dev mode, enabled the injector, then configured a KV v2 path for the application, Kubernetes auth, a read-only policy, and a role bound to the chart-created ServiceAccount. After that I upgraded the app release with Vault annotations enabled so the agent injected an `.env`-style file into `/vault/secrets/app-config.env`.

The sidecar injection pattern works by mutating the Pod at admission time. In the upgraded Pod there is a `vault-agent-init` init container that authenticates and pre-populates the secret file, plus a long-running `vault-agent` sidecar that can keep templates refreshed while the application container consumes the rendered file.

<details>
<summary><code>Vault Helm install</code></summary>

```bash
$ helm repo add --force-update hashicorp https://helm.releases.hashicorp.com
"hashicorp" has been added to your repositories

$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "hashicorp" chart repository
...Successfully got an update from the "prometheus-community" chart repository
...Successfully got an update from the "bitnami" chart repository
Update Complete. ⎈Happy Helming!⎈

$ helm upgrade --install vault hashicorp/vault --namespace vault --create-namespace --set server.dev.enabled=true --set injector.enabled=true --wait=watcher --timeout 300s
Release "vault" does not exist. Installing it now.
NAME: vault
LAST DEPLOYED: Fri Apr 10 02:02:00 2026
NAMESPACE: vault
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
NOTES:
Thank you for installing HashiCorp Vault!

Now that you have deployed Vault, you should look over the docs on using
Vault with Kubernetes available here:

https://developer.hashicorp.com/vault/docs


Your release is named vault. To learn more about the release, try:

  $ helm status vault
  $ helm get manifest vault

$ kubectl get pods -n vault -o wide
NAME                                   READY   STATUS              RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
vault-0                                0/1     ContainerCreating   0          15s   <none>       minikube   <none>           <none>
vault-agent-injector-8c76487db-wptvx   1/1     Running             0          16s   10.244.0.6   minikube   <none>           <none>
```

</details>

<details>
<summary><code>kubectl get pods -n vault -o wide</code> after readiness wait</summary>

```text
NAME                                   READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
vault-0                                1/1     Running   0          28s   10.244.0.7   minikube   <none>           <none>
vault-agent-injector-8c76487db-wptvx   1/1     Running   0          29s   10.244.0.6   minikube   <none>           <none>
```

</details>

<details>
<summary><code>kubectl exec -n vault vault-0 -- sh /tmp/vault-config.sh</code></summary>

```text
$ kubectl exec -n vault vault-0 -- sh /tmp/vault-config.sh
Checking secret engines
Path          Type         Accessor              Description
----          ----         --------              -----------
cubbyhole/    cubbyhole    cubbyhole_1e3be723    per-token private secret storage
identity/     identity     identity_2ffebb85     identity store
secret/       kv           kv_f9a64ce9           key/value secret storage
sys/          system       system_b73e780d       system endpoints used for control, policy and debugging
secret/ mount already present

Writing application secret metadata
 ========= Secret Path =========
secret/data/lab11/devops-app-py

 ======= Metadata =======
Key                Value
---                -----
created_time       2026-04-09T23:04:39.746883798Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            2

Checking auth methods
Path           Type          Accessor                    Description                Version
----           ----          --------                    -----------                -------
kubernetes/    kubernetes    auth_kubernetes_9526b481    n/a                        n/a
token/         token         auth_token_8763c414         token based credentials    n/a
kubernetes auth already enabled
Configured Kubernetes auth backend
Success! Uploaded policy: lab11-devops-app-py

Configuring role

Policy readback
path "secret/data/lab11/devops-app-py" {
  capabilities = ["read"]
}
```

</details>

<details>
<summary><code>auth/kubernetes/role/lab11-devops-app-py</code> readback</summary>

```json
{
  "data": {
    "bound_service_account_names": [
      "lab11-devops-app-py"
    ],
    "bound_service_account_namespaces": [
      "default"
    ],
    "policies": [
      "lab11-devops-app-py"
    ],
    "ttl": 86400
  }
}
```

</details>

<details>
<summary><code>helm upgrade ... -f /tmp/lab11/app-vault.values.yaml</code></summary>

```bash
$ helm upgrade lab11-devops-app-py k8s/devops-app-py -f k8s/devops-app-py/values-dev.yaml -f /tmp/lab11/app-secrets.values.yaml -f /tmp/lab11/app-vault.values.yaml --wait=watcher --wait-for-jobs --timeout 300s
Release "lab11-devops-app-py" has been upgraded. Happy Helming!
NAME: lab11-devops-app-py
LAST DEPLOYED: Fri Apr 10 02:04:56 2026
NAMESPACE: default
STATUS: deployed
REVISION: 2
DESCRIPTION: Upgrade complete
TEST SUITE: None
NOTES:
1. Review the release:
  helm status lab11-devops-app-py -n default

2. Forward the service locally:
  kubectl port-forward svc/lab11-devops-app-py-service 8080:80 -n default

3. Verify the application:
  curl -fsSL http://127.0.0.1:8080/health | jq
  curl -fsSL http://127.0.0.1:8080/ready | jq

$ kubectl rollout status deployment/lab11-devops-app-py --timeout=300s
deployment "lab11-devops-app-py" successfully rolled out

$ kubectl get pods -l app.kubernetes.io/instance=lab11-devops-app-py -o wide
NAME                                   READY   STATUS        RESTARTS   AGE     IP           NODE       NOMINATED NODE   READINESS GATES
lab11-devops-app-py-578786c7fb-f8zzz   1/1     Terminating   0          4m28s   10.244.0.4   minikube   <none>           <none>
lab11-devops-app-py-78488cd99-4297p    2/2     Running       0          15s     10.244.0.8   minikube   <none>           <none>
```

</details>

<details>
<summary>Injected Pod summary</summary>

```json
{
  "metadata": {
    "name": "lab11-devops-app-py-78488cd99-4297p",
    "annotations": {
      "agent_inject": "true",
      "role": "lab11-devops-app-py",
      "inject_secret_config": "secret/data/lab11/devops-app-py",
      "inject_file_config": "app-config.env"
    }
  },
  "spec": {
    "serviceAccountName": "lab11-devops-app-py",
    "initContainers": [
      "vault-agent-init"
    ],
    "containers": [
      "devops-app-py",
      "vault-agent"
    ]
  },
  "status": {
    "phase": "Running",
    "initContainerStatuses": [
      {
        "name": "vault-agent-init",
        "ready": true,
        "state": {
          "terminated": {
            "containerID": "docker://6ac0871513caf747c2af9fc895961f66f29a9e8a48dfb882b22529c93ad24558",
            "exitCode": 0,
            "finishedAt": "2026-04-09T23:04:57Z",
            "reason": "Completed",
            "startedAt": "2026-04-09T23:04:57Z"
          }
        }
      }
    ],
    "containerStatuses": [
      {
        "name": "devops-app-py",
        "ready": true,
        "restartCount": 0
      },
      {
        "name": "vault-agent",
        "ready": true,
        "restartCount": 0
      }
    ]
  }
}
```

</details>

<details>
<summary><code>ls -l /vault/secrets</code></summary>

```text
$ kubectl exec "$POD_NAME" -c devops-app-py -- ls -l /vault/secrets
total 4
-rw-r--r--    1 100      appgroup        89 Apr  9 23:04 app-config.env
```

</details>

<details>
<summary><code>cat /vault/secrets/app-config.env</code> (redacted)</summary>

```text
$ kubectl exec "$POD_NAME" -c devops-app-py -- cat /vault/secrets/app-config.env | sed -E "s/=.*/=<redacted>/"
APP_USERNAME=<redacted>
APP_PASSWORD=<redacted>
APP_API_KEY=<redacted>
```

</details>

<details>
<summary><code>/health</code> and <code>/ready</code> after Vault-enabled rollout</summary>

```bash
$ curl -fsSL http://127.0.0.1:18084/health | jq
{
  "status": "healthy",
  "timestamp": "2026-04-09T23:06:01.075863+00:00",
  "uptime_seconds": 51
}

$ curl -fsSL http://127.0.0.1:18084/ready | jq
{
  "status": "ready",
  "timestamp": "2026-04-09T23:06:01.102648+00:00",
  "uptime_seconds": 51
}
```

</details>

## Bonus - Vault Agent Templates

The bonus part is implemented in two places. First, the Pod annotations now include `vault.hashicorp.com/agent-inject-template-config`, which renders a single `.env`-style file containing `APP_USERNAME`, `APP_PASSWORD`, and `APP_API_KEY`. Second, the chart now uses named helpers in `_helpers.tpl` so the common environment list and the Vault annotation block are both reusable instead of repeated inline.

For secret refresh behavior, the important distinction is between renewable and non-renewable secrets. Vault Agent templates renew renewable leases when about two-thirds of the lease duration has elapsed. KV v2 values like the ones used in this lab are non-renewable static secrets, so the agent re-fetches and re-renders them on its static refresh interval rather than through lease renewal. The default interval for those static secrets is periodic rather than instantaneous, which is acceptable for this lab but important to remember in production.

`vault.hashicorp.com/agent-inject-command-<name>` is the annotation you would add if the application must run a command after a template is rendered or refreshed. The common use case is reloading a process after the file changes, for example a `kill -HUP` signal or a small wrapper script. I documented it rather than enabling it because this Flask/Gunicorn lab service already starts cleanly with the injected file and does not need an automatic config reload hook for the exercise.

## Security Analysis

Kubernetes Secrets are fine for simple cluster-local use cases where you only need to hand a small amount of sensitive data to workloads and you control RBAC tightly. They are still just Kubernetes API objects, though, so by themselves they do not solve centralized auditing, rotation workflows, or short-lived credentials. Base64 also does not protect them; it only serializes them.

Vault is the stronger choice once the environment needs policy-based access control, centralized secret management, auditable reads, multi-service reuse, or dynamic credentials. The tradeoff is operational complexity: you now need a Vault deployment, auth configuration, policies, roles, injector behavior, and an application consumption pattern that can tolerate file-based secret delivery and refresh.

For production I would not use Vault dev mode. I would run HA storage, TLS, explicit audiences on Kubernetes auth roles, short-lived or dynamic credentials where possible, etcd encryption at rest for any remaining Kubernetes Secrets, and strict RBAC so only the intended workloads and operators can read secret material.

## Task 4 - Documentation

This file is the full Lab 11 write-up. To keep the Kubernetes module maintainable, the course-facing compatibility document is `k8s/SECRETS.md`, which points back here in the same way `k8s/HELM.md` points to the Lab 10 report.
