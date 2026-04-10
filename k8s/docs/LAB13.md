# Kubernetes Lab 13 - GitOps with ArgoCD

I reused the existing Docker-backed `minikube` profile and built Lab 13 on top of the running Lab 11/12 environment instead of resetting the cluster. ArgoCD was installed from the official Helm chart as `argo/argo-cd 9.5.0` with app version `v3.3.6`, and the GitOps source for every `Application` in this lab is `https://github.com/LocalT0aster/DevOps-Core-S26.git` on branch `lab13`. Screenshots were intentionally deferred in this run, so the UI access path is verified here but the actual browser captures are listed separately at the end.

## Current Cluster Context

<details>
<summary><code>kubectl config current-context</code>, <code>minikube status</code>, <code>kubectl get nodes -o wide</code>, <code>helm list -A</code>, <code>kubectl get pods -A</code></summary>

```text
$ kubectl config current-context
minikube
$ minikube status -p minikube
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured

$ kubectl get nodes -o wide
NAME       STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION      CONTAINER-RUNTIME
minikube   Ready    control-plane   12h   v1.35.1   192.168.49.2   <none>        Debian GNU/Linux 12 (bookworm)   6.19.11-1-cachyos   docker://29.2.1

$ helm list -A
NAME                NAMESPACE  REVISION  STATUS    CHART               APP VERSION
lab11-devops-app-py default    2         deployed  devops-app-py-0.3.0 1.9
lab12-devops-app-py default    4         deployed  devops-app-py-0.4.0 1.12.0
vault               vault      1         deployed  vault-0.32.0        1.21.2
```

</details>

## Task 1 - ArgoCD Installation and Access

The local `argocd` CLI was already installed as `v3.3.3+unknown`, so I only needed to add the official Helm repo, pin the chart version, install ArgoCD into namespace `argocd`, and log in over a local TLS port-forward. I exposed `svc/argocd-server` on `https://127.0.0.1:8080`, confirmed the UI returned the login HTML over HTTPS, retrieved the initial admin password in redacted form, and verified CLI access with `argocd app list`.

Because screenshots were deferred, I did not claim browser interaction beyond confirming the UI endpoint was reachable. The missing browser captures are listed in `Screenshots Still Required`.

<details>
<summary><code>helm repo add argo</code>, <code>helm search repo argo/argo-cd --versions</code>, and Helm install</summary>

```bash
$ helm repo add argo https://argoproj.github.io/argo-helm
"argo" has been added to your repositories
$ helm repo update
...Successfully got an update from the "argo" chart repository
$ helm search repo argo/argo-cd --versions | head -n 3
NAME         CHART VERSION  APP VERSION  DESCRIPTION
argo/argo-cd 9.5.0          v3.3.6       A Helm chart for Argo CD, a declarative, GitOps...

$ helm upgrade --install argocd argo/argo-cd --namespace argocd --create-namespace --version 9.5.0 --wait --timeout 10m
NAME: argocd
NAMESPACE: argocd
STATUS: deployed

$ kubectl get pods -n argocd
NAME                                                READY   STATUS      RESTARTS   AGE
argocd-application-controller-0                     1/1     Running     0          30s
argocd-applicationset-controller-58c9647667-wcw95   1/1     Running     0          30s
argocd-dex-server-d68bfd4b7-9ln57                   1/1     Running     0          30s
argocd-notifications-controller-58f8fcd889-9x4nq    1/1     Running     0          30s
argocd-redis-5d5bb8d56b-qjwdl                       1/1     Running     0          30s
argocd-repo-server-5d5755cbb-fstsd                  1/1     Running     0          30s
argocd-server-5964cdf9fb-rd62w                      1/1     Running     0          30s
```

</details>

<details>
<summary><code>kubectl port-forward svc/argocd-server -n argocd 8080:443</code>, <code>argocd admin initial-password</code>, and CLI login</summary>

```bash
$ kubectl port-forward service/argocd-server -n argocd 8080:443
Running in a separate terminal session for this verification step.
$ curl -kI https://127.0.0.1:8080
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

$ argocd admin initial-password -n argocd
[REDACTED]
$ argocd login 127.0.0.1:8080 --insecure --username admin --password [REDACTED]
'admin:login' logged in successfully
Context '127.0.0.1:8080' updated
$ argocd app list
NAME  CLUSTER  NAMESPACE  PROJECT  STATUS  HEALTH  SYNCPOLICY  CONDITIONS  REPO  PATH  TARGET
```

</details>

## Task 2 - Application Deployment with Manual Sync

I created `k8s/argocd/application.yaml` as a manual-sync `Application` pointing to `k8s/devops-app-py` on branch `lab13`, with `helm.releaseName: devops-app-py` and `valueFiles: [values.yaml]`. The chart was updated for GitOps use at the same time: chart version `0.5.0`, `service.type: ClusterIP` across default/dev/prod, and `values-prod.yaml` now uses `replicaCount: 2`.

After applying the `Application`, I manually synced it, verified the release in `default`, and reached it through `kubectl port-forward svc/devops-app-py-service -n default 18080:80`. To test the GitOps loop, I committed and pushed a change from `values.yaml` `replicaCount: 1` to `2`; ArgoCD eventually marked the app `OutOfSync`, and a manual sync brought the Deployment to `2/2` ready replicas. Once that evidence was captured, I deleted the temporary in-cluster `devops-app-py` application and its resources so the final ArgoCD state only contains `dev` and `prod`.

The relevant commits for Task 2 were:

- `9cab12c feat(k8s): add argocd applications`
- `2e2fdcc chore(k8s): scale default argocd demo`

<details>
<summary><code>kubectl apply -f k8s/argocd/application.yaml</code> and the first manual sync</summary>

```bash
$ kubectl apply -f k8s/argocd/application.yaml
application.argoproj.io/devops-app-py created
$ argocd app sync devops-app-py
...
2026-04-10T14:09:34+03:00  batch  Job  default  devops-app-py-post-install  Succeeded  Synced  PostSync  Reached expected number of succeeded pods

$ argocd app wait devops-app-py --health --sync --timeout 300
Sync Status:        Synced to lab13 (9cab12c)
Health Status:      Healthy

$ kubectl get deploy,svc,pvc,pods -n default -l app.kubernetes.io/instance=devops-app-py
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/devops-app-py   1/1     1            1           36s

NAME                            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
service/devops-app-py-service   ClusterIP   10.109.114.177   <none>        80/TCP    36s

NAME                                       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/devops-app-py-data   Bound    pvc-9fac4c4d-8f73-4765-9bee-2430d7331618   100Mi      RWO            standard       36s
```

</details>

<details>
<summary><code>kubectl port-forward svc/devops-app-py-service -n default 18080:80</code> and application check</summary>

```bash
$ curl -fsSL http://127.0.0.1:18080/ready | jq .
{
  "status": "ready",
  "timestamp": "2026-04-10T11:09:49.814083+00:00",
  "uptime_seconds": 22
}
$ curl -fsSL http://127.0.0.1:18080/ | jq .service
{
  "description": "DevOps course info service",
  "framework": "Flask",
  "name": "devops-info-service",
  "version": "1.12.0"
}
$ curl -fsSL http://127.0.0.1:18080/visits | jq .
{
  "visits": 1
}
```

</details>

<details>
<summary><code>git push</code> after changing <code>values.yaml</code> replicas, ArgoCD drift detection, and manual resync</summary>

```bash
$ git push origin lab13
To https://github.com/LocalT0aster/DevOps-Core-S26.git
   9cab12c..2e2fdcc  lab13 -> lab13

$ while true; do date -Is; argocd app get devops-app-py -o json | jq -r "[.status.sync.status, .status.health.status, .status.sync.revision] | @tsv"; done
2026-04-10T14:10:18+03:00  Synced     Healthy  9cab12c53df7e8679c7736388f4bf0e65ac01bbf
...
2026-04-10T14:14:09+03:00  OutOfSync  Healthy  2e2fdccdcfb43bc659aa5c6a7d30f54c21b87d76

$ argocd app sync devops-app-py
$ argocd app wait devops-app-py --health --sync --timeout 300
Sync Status:        Synced to lab13 (2e2fdcc)
Health Status:      Healthy

$ kubectl get deployment devops-app-py -n default
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
devops-app-py   2/2     2            2           5m40s
```

</details>

## Task 3 - Multi-Environment Deployment

I created `dev` and `prod` namespaces, then added `k8s/argocd/application-dev.yaml` and `k8s/argocd/application-prod.yaml`. Both point to the same chart and branch, but `values-dev.yaml` keeps one replica and lighter resources while `values-prod.yaml` keeps two replicas and higher limits. The dev app uses `automated.prune: true` plus `selfHeal: true`, while prod stays manual.

Both environments were deployed successfully and verified through port-forwards on `18081` and `18082`. To demonstrate the policy difference, I committed the same harmless pod annotation into both env values files. Dev auto-synced itself to revision `0bb803c`, while prod became `OutOfSync` and stayed there until I ran a manual sync.

During that work I found a chart bug in the Helm hook jobs: the hook pod templates reused the same selector labels as the main app pods, so the service could temporarily select the post-install smoke-test pod. I fixed that in commit `8f1d087 fix(k8s): exclude hook pods from service endpoints` by removing the release-instance label from the hook pod templates, revalidated the chart, pushed the fix, and left both environments synced to `8f1d087`.

<details>
<summary><code>kubectl apply -f k8s/argocd/application-dev.yaml</code>, <code>kubectl apply -f k8s/argocd/application-prod.yaml</code>, and initial syncs</summary>

```bash
$ kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -
namespace/dev created
$ kubectl create namespace prod --dry-run=client -o yaml | kubectl apply -f -
namespace/prod created
$ kubectl apply -f k8s/argocd/application-dev.yaml
application.argoproj.io/devops-app-py-dev created
$ kubectl apply -f k8s/argocd/application-prod.yaml
application.argoproj.io/devops-app-py-prod created

$ argocd app list
NAME                       CLUSTER                         NAMESPACE  PROJECT  STATUS  HEALTH  SYNCPOLICY
argocd/devops-app-py-dev   https://kubernetes.default.svc  dev        default                  Auto-Prune
argocd/devops-app-py-prod  https://kubernetes.default.svc  prod       default                  Manual

$ argocd app wait devops-app-py-dev --health --sync --timeout 300
Sync Status:        Synced to lab13 (2e2fdcc)
Health Status:      Healthy

$ argocd app wait devops-app-py-prod --health --sync --timeout 300
Sync Status:        Synced to lab13 (2e2fdcc)
Health Status:      Healthy

$ kubectl get deploy,svc,pods -n dev -l app.kubernetes.io/instance=devops-app-py-dev
deployment.apps/devops-app-py-dev   1/1
service/devops-app-py-dev-service   ClusterIP
pod/devops-app-py-dev-85d85556b7-7j6c8   1/1 Running

$ kubectl get deploy,svc,pods -n prod -l app.kubernetes.io/instance=devops-app-py-prod
deployment.apps/devops-app-py-prod   2/2
service/devops-app-py-prod-service   ClusterIP
pod/devops-app-py-prod-b8fbf58ff-7rzpc   1/1 Running
pod/devops-app-py-prod-b8fbf58ff-xfnls   1/1 Running
```

</details>

<details>
<summary><code>kubectl port-forward</code> checks for <code>dev</code> and <code>prod</code></summary>

```bash
$ curl -fsSL http://127.0.0.1:18081/ready | jq .
{
  "status": "ready",
  "timestamp": "2026-04-10T11:16:28.441384+00:00",
  "uptime_seconds": 30
}
$ curl -fsSL http://127.0.0.1:18081/ | jq .service,.system.hostname
{
  "description": "DevOps course info service",
  "framework": "Flask",
  "name": "devops-info-service",
  "version": "1.12.0"
}
"devops-app-py-dev-85d85556b7-7j6c8"

$ curl -fsSL http://127.0.0.1:18082/ready | jq .
{
  "status": "ready",
  "timestamp": "2026-04-10T11:16:28.502495+00:00",
  "uptime_seconds": 36
}
$ curl -fsSL http://127.0.0.1:18082/ | jq .service,.system.hostname
{
  "description": "DevOps course info service",
  "framework": "Flask",
  "name": "devops-info-service",
  "version": "1.12.0"
}
"devops-app-py-prod-b8fbf58ff-xfnls"
```

</details>

<details>
<summary><code>git push</code> for the shared env-values change and dev/prod sync-policy difference</summary>

```bash
$ git push origin lab13
To https://github.com/LocalT0aster/DevOps-Core-S26.git
   2e2fdcc..0bb803c  lab13 -> lab13

$ while true; do date -Is; argocd app get devops-app-py-dev -o json; argocd app get devops-app-py-prod -o json; done
2026-04-10T14:19:45+03:00  dev   Synced     Healthy      2e2fdccdcfb43bc659aa5c6a7d30f54c21b87d76
2026-04-10T14:19:45+03:00  prod  OutOfSync  Healthy      0bb803c97b1785269b5408533f98b1222f264f6d
2026-04-10T14:20:01+03:00  dev   Synced     Progressing  0bb803c97b1785269b5408533f98b1222f264f6d
2026-04-10T14:20:01+03:00  prod  OutOfSync  Healthy      0bb803c97b1785269b5408533f98b1222f264f6d

$ argocd app get devops-app-py-prod
Sync Policy:        Manual
Sync Status:        OutOfSync from lab13 (0bb803c)
Health Status:      Healthy

$ argocd app sync devops-app-py-prod
$ argocd app wait devops-app-py-prod --health --sync --timeout 300
Sync Status:        Synced to lab13 (0bb803c)
Health Status:      Healthy
```

</details>

<details>
<summary><code>fix(k8s): exclude hook pods from service endpoints</code> and final app state</summary>

```bash
$ helm template devops-app-py-prod k8s/devops-app-py -f k8s/devops-app-py/values-prod.yaml | sed -n '/^# Source: devops-app-py\/templates\/hooks\/post-install-job.yaml/,/^---$/p'
apiVersion: batch/v1
kind: Job
metadata:
  name: devops-app-py-prod-post-install
...
spec:
  template:
    metadata:
      labels:
        app.kubernetes.io/name: devops-app-py
        app.kubernetes.io/component: hook

$ argocd app list
NAME                       CLUSTER                         NAMESPACE  PROJECT  STATUS  HEALTH   SYNCPOLICY
argocd/devops-app-py-dev   https://kubernetes.default.svc  dev        default  Synced  Healthy  Auto-Prune
argocd/devops-app-py-prod  https://kubernetes.default.svc  prod       default  Synced  Healthy  Manual
```

</details>

## Task 4 - Self-Healing and Drift Behavior

Replica drift behaved exactly as expected for an auto-sync app: scaling the dev deployment from `1` to `5` replicas made the app `OutOfSync`, and ArgoCD pulled it back to `1` within the next few polling samples. Pod deletion was different: when I deleted the only dev pod, the Deployment/ReplicaSet controller recreated it while ArgoCD stayed `Synced`; that recovery is Kubernetes self-healing, not GitOps reconciliation.

For config drift, I tried extra Deployment labels first because the lab suggests labels as an example. In this environment, extra labels on either the Deployment metadata or the pod template were not surfaced as `OutOfSync` even after a manual refresh, so they were not a reliable self-heal demonstration. I switched to an image-field drift instead by changing the live dev deployment image from `1.12-dev` to `1.12`; ArgoCD restored the desired image back to `1.12-dev` within 5 seconds. Afterward I manually removed the temporary label experiments and verified the dev app was back to `Synced/Healthy`.

The official docs say the application reconciliation timeout defaults to `120s` plus up to `60s` jitter, and automated self-heal retries after `5s`. In this run, repo-driven drift detection still took several minutes to show up in ArgoCD, so I relied on the actual timestamps captured below instead of assuming the documented minimum.

<details>
<summary><code>kubectl scale deployment devops-app-py-dev -n dev --replicas=5</code> and ArgoCD self-heal</summary>

```bash
$ kubectl scale deployment devops-app-py-dev -n dev --replicas=5
deployment.apps/devops-app-py-dev scaled
2026-04-10T14:25:10+03:00  deploy  5  1  1
2026-04-10T14:25:10+03:00  app     OutOfSync  Progressing  8f1d0879c728e15141a5bf3c317282da040154da
2026-04-10T14:25:16+03:00  deploy  5  1  1
2026-04-10T14:25:16+03:00  app     OutOfSync  Progressing  8f1d0879c728e15141a5bf3c317282da040154da
2026-04-10T14:25:21+03:00  deploy  1  1  1
2026-04-10T14:25:21+03:00  app     Synced     Healthy      8f1d0879c728e15141a5bf3c317282da040154da
```

</details>

<details>
<summary><code>kubectl delete pod -n dev ...</code> and Deployment/ReplicaSet recovery</summary>

```bash
$ kubectl delete pod -n dev devops-app-py-dev-79d7ddf98c-zxksq
pod "devops-app-py-dev-79d7ddf98c-zxksq" deleted from dev namespace
2026-04-10T14:26:13+03:00  app  Synced  Progressing
2026-04-10T14:26:13+03:00  pod  devops-app-py-dev-79d7ddf98c-bkc9l  Running  false
...
2026-04-10T14:26:31+03:00  app  Synced  Healthy
2026-04-10T14:26:31+03:00  pod  devops-app-py-dev-79d7ddf98c-bkc9l  Running  true
```

</details>

<details>
<summary><code>kubectl set image deployment/devops-app-py-dev -n dev devops-app-py=localt0aster/devops-app-py:1.12</code> and image drift self-heal</summary>

```bash
$ kubectl set image deployment/devops-app-py-dev -n dev devops-app-py=localt0aster/devops-app-py:1.12
deployment.apps/devops-app-py-dev image updated
2026-04-10T14:33:11+03:00  image  localt0aster/devops-app-py:1.12
2026-04-10T14:33:11+03:00  app    Synced  Progressing  8f1d0879c728e15141a5bf3c317282da040154da
2026-04-10T14:33:16+03:00  image  localt0aster/devops-app-py:1.12-dev
2026-04-10T14:33:16+03:00  app    Synced  Healthy      8f1d0879c728e15141a5bf3c317282da040154da
```

</details>

<details>
<summary><code>kubectl label ... lab13-drift-</code>, <code>kubectl patch ... /spec/template/metadata/labels/lab13-template-drift</code>, and final cleanup</summary>

```bash
$ kubectl label deployment devops-app-py-dev -n dev lab13-drift-
deployment.apps/devops-app-py-dev unlabeled
$ kubectl patch deployment devops-app-py-dev -n dev --type json -p '[{"op":"remove","path":"/spec/template/metadata/labels/lab13-template-drift"}]'
deployment.apps/devops-app-py-dev patched
$ kubectl rollout status deployment/devops-app-py-dev -n dev --timeout=300s
deployment "devops-app-py-dev" successfully rolled out
$ argocd app wait devops-app-py-dev --health --sync --timeout 300
Sync Status:        Synced to lab13 (8f1d087)
Health Status:      Healthy
```

</details>

## Screenshots Still Required

- ArgoCD UI overview showing both `devops-app-py-dev` and `devops-app-py-prod`.
- Application details page for either dev or prod, including sync status and health.
- Drift comparison state showing dev auto-syncing while prod remains `OutOfSync`.

## Final State

<details>
<summary><code>argocd app list</code> and final dev/prod resources</summary>

```text
$ argocd app list
NAME                       CLUSTER                         NAMESPACE  PROJECT  STATUS  HEALTH   SYNCPOLICY
argocd/devops-app-py-dev   https://kubernetes.default.svc  dev        default  Synced  Healthy  Auto-Prune
argocd/devops-app-py-prod  https://kubernetes.default.svc  prod       default  Synced  Healthy  Manual

$ kubectl get deploy,svc,pods -n dev
deployment.apps/devops-app-py-dev   1/1
service/devops-app-py-dev-service   ClusterIP
pod/devops-app-py-dev-79d7ddf98c-4fsgw   1/1 Running

$ kubectl get deploy,svc,pods -n prod
deployment.apps/devops-app-py-prod   2/2
service/devops-app-py-prod-service   ClusterIP
pod/devops-app-py-prod-764c4cdb7f-fqbqc   1/1 Running
pod/devops-app-py-prod-764c4cdb7f-qf2n5   1/1 Running
```

</details>

## References

- [ArgoCD Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/)
- [ArgoCD Declarative Setup](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/)
- [ArgoCD Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)
- [ArgoCD FAQ](https://argo-cd.readthedocs.io/en/latest/faq/)
- [Argo Helm Chart](https://github.com/argoproj/argo-helm/tree/main/charts/argo-cd)
