# Kubernetes Lab 9

## Task 1 - Local Kubernetes Setup

I used `minikube` because it was in Arch Linux extra repo (`kind` is only in AUR), integrates cleanly with the Docker driver, and has more features.

<details>
<summary>Cluster setup verification output</summary>

```text
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
minikube   Ready    control-plane   2m45s   v1.35.1   192.168.49.2   <none>        Debian GNU/Linux 12 (bookworm)   6.19.10-1-cachyos   docker://29.2.1

$ kubectl get namespaces
NAME              STATUS   AGE
default           Active   3m9s
kube-node-lease   Active   3m9s
kube-public       Active   3m9s
kube-system       Active   3m9s
```

</details>
