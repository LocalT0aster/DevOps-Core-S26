# Secrets Notes

This file exists to satisfy the Lab 11 requirement for a dedicated secrets document without flattening the Kubernetes module back into one large documentation directory.

## Lab 11 Documentation

The full Lab 11 write-up, command transcripts, verification logs, and sanitized Vault evidence are kept in [docs/LAB11.md](docs/LAB11.md).

## Why This Structure Is Better

- `k8s/README.md` stays short and usable as the module entry point.
- `k8s/docs/LAB09.md`, [docs/LAB10.md](docs/LAB10.md), and [docs/LAB11.md](docs/LAB11.md) keep each Kubernetes lab self-contained.
- Raw manifests, Helm chart files, and documentation stay separated, which makes the implementation files easier to navigate.
- `k8s/SECRETS.md` provides the compatibility filename the lab expects while the actual report remains in the `docs/` hierarchy.

In short, `SECRETS.md` is the compatibility layer, and `k8s/docs/` remains the maintainable long-term structure.
