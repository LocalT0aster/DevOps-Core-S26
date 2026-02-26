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
  - `main.tf`: network + Ubuntu VM container + startup bootstrap for SSH/HTTP services + published ports.
  - `variables.tf`: bind IPs, host ports, labels.
  - `outputs.tf`: endpoints and connection commands.

### Key Decisions

- Used Ubuntu image directly to keep `apply` simple and avoid local custom image build failures.
- Used startup bootstrap in the container command to install and run `openssh-server` and HTTP services automatically.
- Bound SSH to `127.0.0.1` by default to reduce exposure.

### Challenges

- Provider download from registry/GitHub release assets may timeout on slow links.
- Workaround: local plugin mirror (`~/.terraform.d/plugins`) if direct provider install fails.

### Command Output


```
Outputs:

app_url = "http://127.0.0.1:5000"
container_ip = "172.18.0.2"
container_shell_command = "docker exec -it lab04-local-vm /bin/bash"
http_url = "http://127.0.0.1:8080"
network_name = "lab04-local-net"
public_ip_equivalent = "127.0.0.1"
ssh_command = "ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1"
vm_name = "lab04-local-vm"
```

```
$ ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1 echo "SSH avaliable"
The authenticity of host '[127.0.0.1]:2222 ([127.0.0.1]:2222)' can't be established.
ED25519 key fingerprint is: SHA256:shGIrzMssSaR8sB9yuUyId7BYrKHyfi/OQSvGJq5gkk
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[127.0.0.1]:2222' (ED25519) to the list of known hosts.
SSH avaliable
```


## 3. Pulumi Implementation

- Pulumi CLI: `v3.192.0`
- Language: Python
- Project path: `pulumi/`
- Resources:
  - Docker network
  - Docker `RemoteImage` (`ubuntu:24.04`)
  - Docker container with same ports as Terraform setup

### Command Output

```bash
wait a minute
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
