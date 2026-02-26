# LAB04 - IaC with Local Docker Provider

## 1. Cloud Provider & Infrastructure

- Provider choice: local Docker (`kreuzwerker/docker` for OpenTofu/Terraform, `pulumi-docker` for Pulumi).
- Rationale: zero cloud cost, reproducible setup, no credential management.
- Context: I was unable to obtain a free cloud provider account, but I still wanted practical hands-on experience with Terraform and Pulumi, so I used the local Docker provider.
- VM equivalent: one `ubuntu:24.04` container (`lab04-local-vm`).
- Network/VPC equivalent: one user-defined Docker network (`lab04-local-net`).
- Security group/firewall equivalent: published ports on the VM container:
  - SSH: host `127.0.0.1:2222` -> container `22`
  - HTTP: host `0.0.0.0:8080` -> container `80`
  - App: host `0.0.0.0:5000` -> container `5000`
- Public IP equivalent: `127.0.0.1`.
- Cost: `$0`.

## 2. Terraform (OpenTofu) Implementation

- CLI used: OpenTofu `v1.10.9` (Terraform-compatible HCL).
- Project path: `terraform/`.
- Main files:
  - `versions.tf`: provider + required version.
  - `main.tf`: network + Ubuntu VM container + published ports.
  - `variables.tf`: bind IPs, host ports, labels.
  - `outputs.tf`: endpoints and connection commands.

### Key Decisions

- Used Ubuntu image directly to keep `apply` simple and avoid local custom image build failures.
- Used a long-running command (`sleep` loop) so container stays available as VM equivalent.
- Bound SSH to `127.0.0.1` by default to reduce exposure.

### Challenges

- Provider download from registry/GitHub release assets may timeout on slow links.
- Workaround: local plugin mirror (`~/.terraform.d/plugins`) if direct provider install fails.

### Command Output

```bash
cd terraform
tofu init -plugin-dir="$HOME/.terraform.d/plugins"
tofu plan
tofu apply -auto-approve
tofu output
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}' | rg 'lab04-local-vm|NAMES'
```

## 3. Pulumi Implementation

- Pulumi CLI: `v3.x`
- Language: Python
- Project path: `pulumi/`
- Resources:
  - Docker network
  - Docker `RemoteImage` (`ubuntu:24.04`)
  - Docker container with same ports as Terraform setup

### Command Output

```bash
cd pulumi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp Pulumi.dev.yaml.example Pulumi.dev.yaml
# Verify language plugin is present:
which pulumi-language-python || echo "Missing pulumi-language-python in PATH"
pulumi stack init dev || true
pulumi preview
pulumi up --yes
pulumi stack output
```

## 4. Terraform vs Pulumi (Local Docker Case)

- Ease of learning: OpenTofu/Terraform is faster to start for simple resource graphs.
- Readability: Terraform is shorter for this case; Pulumi is more explicit and programmable.
- Debugging: Terraform plan output is clearer for infra diffs; Pulumi errors are usually better typed in Python.
- Docs: Terraform ecosystem is broader; Pulumi docs are good but smaller.
- Use case:
  - Terraform/OpenTofu: straightforward declarative infrastructure.
  - Pulumi: infrastructure that benefits from real language abstractions and reuse.

## 5. Lab 5 Preparation & Cleanup

- VM for Lab 5:
  - Keep running VM: optional (`lab04-local-vm`).
  - Alternative: recreate quickly with IaC before Lab 5.
- Cleanup commands:

```bash
cd terraform
tofu destroy -auto-approve
cd pulumi && pulumi destroy --yes
```

## Notes

- This is a local Docker-provider adaptation of a cloud-VM lab.
- It is practical for learning IaC workflows, but not a full replacement for real cloud-provider experience.
