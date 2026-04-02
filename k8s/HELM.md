# Helm Notes

This file exists to satisfy the Lab 10 requirement for a dedicated Helm document without forcing the entire Kubernetes module back into a flat documentation layout.

## Lab 10 Documentation

The full Helm lab write-up, command transcripts, and verification logs are kept in [docs/LAB10.md](docs/LAB10.md). The Task 5 documentation section that covers chart overview, configuration, hooks, operations, and validation is here: [docs/LAB10.md#task-5-documentation](docs/LAB10.md#task-5-documentation).

## Why This Structure Is Better

- `k8s/README.md` stays short and works as the module entry point instead of becoming a 50 kB transcript dump.
- `k8s/docs/LAB09.md` and `k8s/docs/LAB10.md` keep each lab self-contained, which scales better as more Kubernetes labs are added.
- Raw manifests and Helm chart files remain easy to find because documentation is separated from implementation files.
- `k8s/HELM.md` provides the explicit Helm-facing document name the lab expects, while the detailed content stays in the more maintainable `docs/` hierarchy.

In short, `HELM.md` is the compatibility layer, and `k8s/docs/` is the maintainable structure.
