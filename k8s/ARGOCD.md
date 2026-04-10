# ArgoCD Notes

This file exists to satisfy the Lab 13 requirement for a dedicated ArgoCD document without flattening the Kubernetes module back into one large documentation directory.

## Lab 13 Documentation

The full Lab 13 write-up, GitOps manifests, ArgoCD command transcripts, sync-policy evidence, and self-healing notes are kept in [docs/LAB13.md](docs/LAB13.md).

## Why This Structure Is Better

- `k8s/README.md` stays short and usable as the module entry point.
- `k8s/docs/LAB09.md`, [docs/LAB10.md](docs/LAB10.md), [docs/LAB11.md](docs/LAB11.md), [docs/LAB12.md](docs/LAB12.md), and [docs/LAB13.md](docs/LAB13.md) keep each Kubernetes lab self-contained.
- Raw manifests, Helm chart files, and documentation stay separated, which makes the implementation files easier to navigate.
- `k8s/ARGOCD.md` provides the compatibility filename the lab expects while the actual report remains in the `docs/` hierarchy.

In short, `ARGOCD.md` is the compatibility layer, and `k8s/docs/` remains the maintainable long-term structure.
