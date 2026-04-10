# ConfigMap Notes

This file exists to satisfy the Lab 12 requirement for a dedicated ConfigMap document without flattening the Kubernetes module back into one large documentation directory.

## Lab 12 Documentation

The full Lab 12 write-up, command transcripts, Docker persistence proof, Kubernetes verification, and hot-reload notes are kept in [docs/LAB12.md](docs/LAB12.md).

## Why This Structure Is Better

- `k8s/README.md` stays short and usable as the module entry point.
- `k8s/docs/LAB09.md`, [docs/LAB10.md](docs/LAB10.md), [docs/LAB11.md](docs/LAB11.md), and [docs/LAB12.md](docs/LAB12.md) keep each Kubernetes lab self-contained.
- Raw manifests, Helm chart files, and documentation stay separated, which makes the implementation files easier to navigate.
- `k8s/CONFIGMAPS.md` provides the compatibility filename the lab expects while the actual report remains in the `docs/` hierarchy.

In short, `CONFIGMAPS.md` is the compatibility layer, and `k8s/docs/` remains the maintainable long-term structure.
