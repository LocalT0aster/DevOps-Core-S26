# Argo Rollouts Notes

This file exists to satisfy the Lab 14 requirement for a dedicated Argo Rollouts document without flattening the Kubernetes module back into one large documentation directory.

## Lab 14 Documentation

The full Lab 14 write-up, Rollout-enabled Helm chart changes, canary and blue-green values files, automated analysis notes, command transcripts, and screenshot references are kept in [docs/LAB14.md](docs/LAB14.md).

## Why This Structure Is Better

- `k8s/README.md` stays short and useful as the Kubernetes module entry point.
- `k8s/docs/LAB09.md`, [docs/LAB10.md](docs/LAB10.md), [docs/LAB11.md](docs/LAB11.md), [docs/LAB12.md](docs/LAB12.md), [docs/LAB13.md](docs/LAB13.md), and [docs/LAB14.md](docs/LAB14.md) keep each Kubernetes lab self-contained.
- Raw manifests, Helm chart files, ArgoCD applications, Rollout values, and documentation stay separated.
- `k8s/ROLLOUTS.md` provides the compatibility filename the lab expects while the actual report remains in the `docs/` hierarchy.

In short, `ROLLOUTS.md` is the compatibility layer, and `k8s/docs/` remains the maintainable long-term structure.
