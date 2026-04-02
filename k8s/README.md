# Kubernetes Module

This directory contains the Kubernetes deliverables for the course application. It includes the raw Kubernetes manifests used in Lab 9, the Helm chart created in Lab 10, and the lab write-ups moved into `k8s/docs/` so the module root stays readable.

The main deployment assets are:

- `deployment.yml`: baseline Kubernetes `Deployment` manifest for the Python app.
- `service.yml`: baseline Kubernetes `Service` manifest exposing the app inside the cluster and via `NodePort`.
- `devops-app-py/`: Helm chart version of the application deployment.
- `docs/`: lab documentation split by assignment.

## Documentation

- [Helm Notes](HELM.md)
- [Lab 09 - Kubernetes Basics](docs/LAB09.md)
- [Lab 10 - Helm Package Manager](docs/LAB10.md)
