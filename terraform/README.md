# Lab04 Terraform (Local Docker Provider)

This Terraform project implements Lab04 with the local Docker provider instead of a cloud VM.

## What It Creates

- Docker network (`network/VPC` equivalent)
- Ubuntu 24.04 container (`VM/compute` equivalent) with startup bootstrap
  - installs and starts `openssh-server`
  - configures SSH authorized key
  - starts simple HTTP endpoints on ports `80` and `5000`
- Port mappings as firewall equivalents:
  - SSH: container `22` -> host `2222` (bound to `127.0.0.1`)
  - HTTP: container `80` -> host `8080`
  - App: container `5000` -> host `5000`

## Local Prerequisites

- Docker daemon running
- OpenTofu or Terraform CLI

## Quick Start (OpenTofu)

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# edit terraform.tfvars and set ssh_public_key

cd terraform
tofu init -plugin-dir="$HOME/.terraform.d/plugins"
tofu plan
tofu apply -auto-approve

# verify SSH
ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1 'echo SSH_OK'
```

If provider download is blocked, manually place provider binaries under:
`~/.terraform.d/plugins/registry.terraform.io/<namespace>/<name>/<version>/linux_amd64/`

## Destroy

```bash
cd terraform
tofu destroy -auto-approve
```
