# LAB04 - IaC with Local Docker Provider

## 1. Cloud Provider & Infrastructure

- Provider choice: local Docker (`kreuzwerker/docker` for OpenTofu/Terraform, `pulumi-docker` for Pulumi).
- Rationale: zero cloud cost, reproducible setup, no credential management.
- Context: I was unable to obtain a free cloud provider account, but I still wanted practical hands-on experience with Terraform and Pulumi, so I used the local Docker provider.
- Instance type/size equivalent: one `ubuntu:24.04` container with default Docker host resources.
- Region/zone equivalent: local machine (`N/A` for cloud region/zone).
- VM equivalent: one `ubuntu:24.04` container (`lab04-local-vm`).
- Network/VPC equivalent: one user-defined Docker network (`lab04-local-net`).
- Resources created:
  - `docker_network.lab04`
  - `docker_image.vm_image`
  - `docker_container.vm`
- Security group/firewall equivalent: published ports on the VM container:
  - SSH: host `127.0.0.1:2222` -> container `22`
  - HTTP: host `0.0.0.0:80` -> container `80`
  - App: host `0.0.0.0:5000` -> container `5000`
- Public IP equivalent: `127.0.0.1`.
- Cost: `$0`.

## 2. Terraform (OpenTofu) Implementation

- CLI used: OpenTofu `v1.10.9` (Terraform-compatible HCL).
- Project path: `terraform/`.
- Main files:
  - `versions.tf`: provider + required version.
  - `main.tf`: network + Ubuntu VM container + startup bootstrap for SSH service + published ports.
  - `variables.tf`: bind IPs, host ports, labels.
  - `outputs.tf`: endpoints and connection commands.
- Project structure: split into `versions.tf` (providers), `variables.tf` (inputs), `main.tf` (resources), and `outputs.tf` (connection/output values) for readability and predictable diffs.

### Key Decisions

- Used Ubuntu image directly to keep `apply` simple and avoid local custom image build failures.
- Used startup bootstrap in a separate shell script (`docker/provision_vm.sh`) to avoid duplicated provisioning logic across Terraform and Pulumi.
- Kept `80` and `5000` port mappings defined in IaC, but did not run mock HTTP services in the container.
- Bound SSH to `127.0.0.1` by default to reduce exposure.

### Challenges

- Provider download from registry/GitHub release assets may timeout on slow links.
- Workaround: local plugin mirror (`~/.terraform.d/plugins`) if direct provider install fails.

### Command Output

<details>
<summary>`tofu plan`</summary>

```
$ tofu plan

OpenTofu used the selected providers to generate the following execution plan. Resource
actions are indicated with the following symbols:
  + create

OpenTofu will perform the following actions:

  # docker_container.vm will be created
  + resource "docker_container" "vm" {
      + attach                                      = false
      + bridge                                      = (known after apply)
      + command                                     = [
          + "/bin/bash",
          + "-lc",
          + <<-EOT
                #!/usr/bin/env bash

                set -euo pipefail

                : "${VM_USER:?VM_USER must be set}"
                : "${SSH_PUBLIC_KEY:?SSH_PUBLIC_KEY must be set}"

                export DEBIAN_FRONTEND=noninteractive

                if ! command -v sshd >/dev/null 2>&1; then
                  apt-get update
                  apt-get install -y --no-install-recommends openssh-server ca-certificates
                fi

                id -u "${VM_USER}" >/dev/null 2>&1 || useradd -m -s /bin/bash "${VM_USER}"
                install -d -m 700 -o "${VM_USER}" -g "${VM_USER}" "/home/${VM_USER}/.ssh"
                printf '%s\n' "${SSH_PUBLIC_KEY}" >"/home/${VM_USER}/.ssh/authorized_keys"
                chown "${VM_USER}:${VM_USER}" "/home/${VM_USER}/.ssh/authorized_keys"
                chmod 600 "/home/${VM_USER}/.ssh/authorized_keys"

                mkdir -p /run/sshd
                cat >/etc/ssh/sshd_config.d/lab04.conf <<CFG
                PasswordAuthentication no
                PubkeyAuthentication yes
                PermitRootLogin no
                AllowUsers ${VM_USER}
                CFG

                /usr/sbin/sshd
                tail -f /dev/null
            EOT,
        ]
      + container_logs                              = (known after apply)
      + container_read_refresh_timeout_milliseconds = 15000
      + entrypoint                                  = (known after apply)
      + env                                         = (sensitive value)
      + exit_code                                   = (known after apply)
      + hostname                                    = "lab04-local-vm"
      + id                                          = (known after apply)
      + image                                       = (known after apply)
      + init                                        = (known after apply)
      + ipc_mode                                    = (known after apply)
      + log_driver                                  = (known after apply)
      + logs                                        = false
      + must_run                                    = true
      + name                                        = "lab04-local-vm"
      + network_data                                = (known after apply)
      + network_mode                                = "bridge"
      + read_only                                   = false
      + remove_volumes                              = true
      + restart                                     = "unless-stopped"
      + rm                                          = false
      + runtime                                     = (known after apply)
      + security_opts                               = (known after apply)
      + shm_size                                    = (known after apply)
      + start                                       = true
      + stdin_open                                  = false
      + stop_signal                                 = (known after apply)
      + stop_timeout                                = (known after apply)
      + tty                                         = false
      + wait                                        = false
      + wait_timeout                                = 60

      + healthcheck (known after apply)

      + labels {
          + label = "lab"
          + value = "04"
        }
      + labels {
          + label = "managed-by"
          + value = "terraform"
        }
      + labels {
          + label = "project"
          + value = "lab04-local"
        }

      + networks_advanced {
          + aliases = [
              + "lab04-local-vm",
            ]
          + name    = "lab04-local-net"
        }

      + ports {
          + external = 2222
          + internal = 22
          + ip       = "127.0.0.1"
          + protocol = "tcp"
        }
      + ports {
          + external = 80
          + internal = 80
          + ip       = "0.0.0.0"
          + protocol = "tcp"
        }
      + ports {
          + external = 5000
          + internal = 5000
          + ip       = "0.0.0.0"
          + protocol = "tcp"
        }
    }

  # docker_image.vm_image will be created
  + resource "docker_image" "vm_image" {
      + id           = (known after apply)
      + image_id     = (known after apply)
      + keep_locally = true
      + name         = "ubuntu:24.04"
      + repo_digest  = (known after apply)
    }

  # docker_network.lab04 will be created
  + resource "docker_network" "lab04" {
      + driver      = (known after apply)
      + id          = (known after apply)
      + internal    = (known after apply)
      + ipam_driver = "default"
      + name        = "lab04-local-net"
      + options     = (known after apply)
      + scope       = (known after apply)

      + ipam_config (known after apply)

      + labels {
          + label = "lab"
          + value = "04"
        }
      + labels {
          + label = "managed-by"
          + value = "terraform"
        }
      + labels {
          + label = "project"
          + value = "lab04-local"
        }
    }

Plan: 3 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + app_url                 = "http://127.0.0.1:5000"
  + container_ip            = (known after apply)
  + container_shell_command = "docker exec -it lab04-local-vm /bin/bash"
  + http_url                = "http://127.0.0.1:80"
  + network_name            = "lab04-local-net"
  + public_ip_equivalent    = "127.0.0.1"
  + ssh_command             = "ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1"
  + vm_name                 = "lab04-local-vm"

───────────────────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so OpenTofu can't guarantee to take
exactly these actions if you run "tofu apply" now.
```

</details>

<details>
<summary>`tofu apply`</summary>

```
$ tofu apply

OpenTofu used the selected providers to generate the following execution plan. Resource
actions are indicated with the following symbols:
  + create

OpenTofu will perform the following actions:

  # docker_container.vm will be created
  + resource "docker_container" "vm" {
      + attach                                      = false
      + bridge                                      = (known after apply)
      + command                                     = [
          + "/bin/bash",
          + "-lc",
          + <<-EOT
                #!/usr/bin/env bash

                set -euo pipefail

                : "${VM_USER:?VM_USER must be set}"
                : "${SSH_PUBLIC_KEY:?SSH_PUBLIC_KEY must be set}"

                export DEBIAN_FRONTEND=noninteractive

                if ! command -v sshd >/dev/null 2>&1; then
                  apt-get update
                  apt-get install -y --no-install-recommends openssh-server ca-certificates
                fi

                id -u "${VM_USER}" >/dev/null 2>&1 || useradd -m -s /bin/bash "${VM_USER}"
                install -d -m 700 -o "${VM_USER}" -g "${VM_USER}" "/home/${VM_USER}/.ssh"
                printf '%s\n' "${SSH_PUBLIC_KEY}" >"/home/${VM_USER}/.ssh/authorized_keys"
                chown "${VM_USER}:${VM_USER}" "/home/${VM_USER}/.ssh/authorized_keys"
                chmod 600 "/home/${VM_USER}/.ssh/authorized_keys"

                mkdir -p /run/sshd
                cat >/etc/ssh/sshd_config.d/lab04.conf <<CFG
                PasswordAuthentication no
                PubkeyAuthentication yes
                PermitRootLogin no
                AllowUsers ${VM_USER}
                CFG

                /usr/sbin/sshd
                tail -f /dev/null
            EOT,
        ]
      + container_logs                              = (known after apply)
      + container_read_refresh_timeout_milliseconds = 15000
      + entrypoint                                  = (known after apply)
      + env                                         = (sensitive value)
      + exit_code                                   = (known after apply)
      + hostname                                    = "lab04-local-vm"
      + id                                          = (known after apply)
      + image                                       = (known after apply)
      + init                                        = (known after apply)
      + ipc_mode                                    = (known after apply)
      + log_driver                                  = (known after apply)
      + logs                                        = false
      + must_run                                    = true
      + name                                        = "lab04-local-vm"
      + network_data                                = (known after apply)
      + network_mode                                = "bridge"
      + read_only                                   = false
      + remove_volumes                              = true
      + restart                                     = "unless-stopped"
      + rm                                          = false
      + runtime                                     = (known after apply)
      + security_opts                               = (known after apply)
      + shm_size                                    = (known after apply)
      + start                                       = true
      + stdin_open                                  = false
      + stop_signal                                 = (known after apply)
      + stop_timeout                                = (known after apply)
      + tty                                         = false
      + wait                                        = false
      + wait_timeout                                = 60

      + healthcheck (known after apply)

      + labels {
          + label = "lab"
          + value = "04"
        }
      + labels {
          + label = "managed-by"
          + value = "terraform"
        }
      + labels {
          + label = "project"
          + value = "lab04-local"
        }

      + networks_advanced {
          + aliases = [
              + "lab04-local-vm",
            ]
          + name    = "lab04-local-net"
        }

      + ports {
          + external = 2222
          + internal = 22
          + ip       = "127.0.0.1"
          + protocol = "tcp"
        }
      + ports {
          + external = 80
          + internal = 80
          + ip       = "0.0.0.0"
          + protocol = "tcp"
        }
      + ports {
          + external = 5000
          + internal = 5000
          + ip       = "0.0.0.0"
          + protocol = "tcp"
        }
    }

  # docker_image.vm_image will be created
  + resource "docker_image" "vm_image" {
      + id           = (known after apply)
      + image_id     = (known after apply)
      + keep_locally = true
      + name         = "ubuntu:24.04"
      + repo_digest  = (known after apply)
    }

  # docker_network.lab04 will be created
  + resource "docker_network" "lab04" {
      + driver      = (known after apply)
      + id          = (known after apply)
      + internal    = (known after apply)
      + ipam_driver = "default"
      + name        = "lab04-local-net"
      + options     = (known after apply)
      + scope       = (known after apply)

      + ipam_config (known after apply)

      + labels {
          + label = "lab"
          + value = "04"
        }
      + labels {
          + label = "managed-by"
          + value = "terraform"
        }
      + labels {
          + label = "project"
          + value = "lab04-local"
        }
    }

Plan: 3 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + app_url                 = "http://127.0.0.1:5000"
  + container_ip            = (known after apply)
  + container_shell_command = "docker exec -it lab04-local-vm /bin/bash"
  + http_url                = "http://127.0.0.1:80"
  + network_name            = "lab04-local-net"
  + public_ip_equivalent    = "127.0.0.1"
  + ssh_command             = "ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1"
  + vm_name                 = "lab04-local-vm"

Do you want to perform these actions?
  OpenTofu will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

docker_image.vm_image: Creating...
docker_network.lab04: Creating...
docker_image.vm_image: Creation complete after 0s [id=sha256:bbdabce66f1b7dde0c081a6b4536d837cd81dd322dd8c99edd68860baf3b2db3ubuntu:24.04]
docker_network.lab04: Creation complete after 2s [id=c5e934e4d29b45d2fd996e3baed55a401b28f966d0999eba7ff48967535c4075]
docker_container.vm: Creating...
docker_container.vm: Creation complete after 0s [id=5bfb16950cb9d1ef9ab7eb3f6dedc020ff8729bafa667d250a58b8746ed3bb1e]

Apply complete! Resources: 3 added, 0 changed, 0 destroyed.

Outputs:

app_url = "http://127.0.0.1:5000"
container_ip = "172.18.0.2"
container_shell_command = "docker exec -it lab04-local-vm /bin/bash"
http_url = "http://127.0.0.1:80"
network_name = "lab04-local-net"
public_ip_equivalent = "127.0.0.1"
ssh_command = "ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1"
vm_name = "lab04-local-vm"
```

</details>

<details>
<summary>SSH test</summary>

```
$ ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1 echo "SSH available"
The authenticity of host '[127.0.0.1]:2222 ([127.0.0.1]:2222)' can't be established.
ED25519 key fingerprint is: SHA256:shGIrzMssSaR8sB9yuUyId7BYrKHyfi/OQSvGJq5gkk
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[127.0.0.1]:2222' (ED25519) to the list of known hosts.
SSH available
```

</details>

Teardown command (Terraform resources):

```bash
cd terraform
tofu destroy -auto-approve
```

## 3. Pulumi Implementation

- Pulumi CLI: `v3.192.0`
- Language: Python
- Project path: `pulumi/`
- Resources:
  - Docker network
  - Docker `RemoteImage` (`ubuntu:24.04`)
  - Docker container with same ports as Terraform setup

### Code Differences vs Terraform

- Terraform uses declarative HCL resources and variable blocks.
- Pulumi uses Python (`__main__.py`) and typed constructor args (`docker.ContainerPortArgs`, `docker.ContainerLabelArgs`).
- The shared provisioning logic is loaded from `docker/provision_vm.sh` in both implementations, but Pulumi reads it via `Path(...).read_text()`, while Terraform uses `file(...)`.

### Advantages Discovered

- Strong typing and native language constructs in Python made refactoring (for example, shared provisioning script usage) easier.
- Pulumi outputs and resource objects map naturally to normal programming workflows.
- For this lab size, Pulumi and Terraform were both fast enough; Pulumi felt better when logic started to grow.

### Challenges

- Pulumi passphrase prompts can interrupt command flow if `PULUMI_CONFIG_PASSPHRASE` is not set.
- On Nix/Home-Manager-based setups, `pulumi-language-python` may be missing from `PATH`, which blocks `preview/up` until fixed.
- Docker provider behavior is similar across tools, but plugin/setup issues differ and require separate troubleshooting steps.

### Command Output

`tofu destroy` before Pulumi migration:

```bash
$ tofu destroy -auto-approve
```

<details>
<summary>`pulumi preview`</summary>

```
$ pulumi preview
Enter your passphrase to unlock config/secrets
    (set PULUMI_CONFIG_PASSPHRASE or PULUMI_CONFIG_PASSPHRASE_FILE to remember):
Enter your passphrase to unlock config/secrets
Previewing update (dev):
     Type                         Name                    Plan       Info
 +   pulumi:pulumi:Stack          lab04-local-docker-dev  create     1 warning
 +   ├─ docker:index:Network      lab04-net               create
 +   ├─ docker:index:RemoteImage  lab04-vm-image          create
 +   └─ docker:index:Container    lab04-vm                create

Diagnostics:
  pulumi:pulumi:Stack (lab04-local-docker-dev):
    warning: using pulumi-language-python from $PATH at /etc/profiles/per-user/t0ast/bin/pulumi-language-python

Outputs:
    appUrl               : "http://127.0.0.1:5000"
    containerShellCommand: "docker exec -it lab04-local-vm /bin/bash"
    httpUrl              : "http://127.0.0.1:80"
    networkName          : "lab04-local-net"
    publicIpEquivalent   : "127.0.0.1"
    sshCommand           : "ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1"
    vmName               : "lab04-local-vm"

Resources:
    + 4 to create
```

</details>

<details>
<summary>`pulumi up`</summary>

```
$ pulumi up
Enter your passphrase to unlock config/secrets
    (set PULUMI_CONFIG_PASSPHRASE or PULUMI_CONFIG_PASSPHRASE_FILE to remember):
Enter your passphrase to unlock config/secrets
Previewing update (dev):
     Type                         Name                    Plan       Info
 +   pulumi:pulumi:Stack          lab04-local-docker-dev  create     1 warning
 +   ├─ docker:index:RemoteImage  lab04-vm-image          create
 +   ├─ docker:index:Network      lab04-net               create
 +   └─ docker:index:Container    lab04-vm                create

Diagnostics:
  pulumi:pulumi:Stack (lab04-local-docker-dev):
    warning: using pulumi-language-python from $PATH at /etc/profiles/per-user/t0ast/bin/pulumi-language-python

Outputs:
    appUrl               : "http://127.0.0.1:5000"
    containerShellCommand: "docker exec -it lab04-local-vm /bin/bash"
    httpUrl              : "http://127.0.0.1:80"
    networkName          : "lab04-local-net"
    publicIpEquivalent   : "127.0.0.1"
    sshCommand           : "ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1"
    vmName               : "lab04-local-vm"

Resources:
    + 4 to create

Do you want to perform this update? yes
Updating (dev):
     Type                         Name                    Status              Info
 +   pulumi:pulumi:Stack          lab04-local-docker-dev  created (2s)        1 warning
 +   ├─ docker:index:RemoteImage  lab04-vm-image          created (0.01s)
 +   ├─ docker:index:Network      lab04-net               created (2s)
 +   └─ docker:index:Container    lab04-vm                created (0.38s)

Diagnostics:
  pulumi:pulumi:Stack (lab04-local-docker-dev):
    warning: using pulumi-language-python from $PATH at /etc/profiles/per-user/t0ast/bin/pulumi-language-python

Outputs:
    appUrl               : "http://127.0.0.1:5000"
    containerShellCommand: "docker exec -it lab04-local-vm /bin/bash"
    httpUrl              : "http://127.0.0.1:80"
    networkName          : "lab04-local-net"
    publicIpEquivalent   : "127.0.0.1"
    sshCommand           : "ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1"
    vmName               : "lab04-local-vm"

Resources:
    + 4 created

Duration: 3s
```

</details>

<details>
<summary>SSH test</summary>

```
$ ssh -i ~/.ssh/id_ed25519 -p 2222 devops@127.0.0.1 echo "SSH works"
The authenticity of host '[127.0.0.1]:2222 ([127.0.0.1]:2222)' can't be established.
ED25519 key fingerprint is: SHA256:spW/AgFoqrVqpf1i7ZWEUqYGXJ8rZM6wGU5+S4WheVI
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[127.0.0.1]:2222' (ED25519) to the list of known hosts.
SSH works
```

</details>

Teardown command (Pulumi resources):

```bash
pulumi destroy --yes
```

## 4. Terraform vs Pulumi (Local Docker Case)

### Ease of Learning

Terraform/OpenTofu was faster to start because the resource graph is explicit in HCL and examples are abundant. I needed less scaffolding to get a first working run with `tofu init/plan/apply`. Pulumi required understanding stack config and language-plugin behavior in addition to infrastructure code.

### Code Readability

For small infrastructure, Terraform is shorter and easier to scan in one file. Pulumi is more verbose, but the Python structure becomes clearer when the project grows and you need reusable helpers. In this lab, Terraform is more concise, while Pulumi is more flexible.

### Debugging

Terraform plan/apply diffs are straightforward and helped quickly validate expected port mappings and resource creation. Pulumi diagnostics were helpful when runtime issues occurred, but setup-level failures (passphrase/plugin) were less obvious initially. Once setup was correct, both were manageable to debug.

### Documentation

Terraform has broader community examples and more copy-paste-ready snippets for common patterns. Pulumi official docs are good and practical, but there are fewer examples for some edge workflows. For this lab, Terraform documentation felt easier to navigate quickly.

### Use Case

I would choose Terraform/OpenTofu for straightforward declarative infrastructure with predictable patterns. I would choose Pulumi when infrastructure logic needs stronger abstraction, conditional behavior, or shared code with application teams. For this local Docker lab, either works, but Terraform was simpler and Pulumi was more programmable.

## 5. Lab 5 Preparation & Cleanup

### VM for Lab 5

- Are you keeping your VM for Lab 5? **No**.
- What will you use for Lab 5? A local VM via libvirt, or a fresh Linux VPS.

### Cleanup Status

- Decision: destroy both Terraform and Pulumi-managed resources after verification.
- Teardown commands used:

```bash
cd terraform
tofu destroy -auto-approve

cd ../pulumi
pulumi destroy --yes
```

- Verification commands:

```bash
docker ps --format '{{.Names}}' | rg 'lab04-local' || echo "No lab04 containers"
docker network ls --format '{{.Name}}' | rg 'lab04-local' || echo "No lab04 networks"
```

## Notes

- This is a local Docker-provider adaptation of a cloud-VM lab.
- Suggestion: this lab could also use `localstack/localstack` (or forks) to emulate parts of AWS locally for free.
  - <https://docs.localstack.cloud/aws/integrations/infrastructure-as-code/terraform/>
  - <https://docs.localstack.cloud/aws/integrations/infrastructure-as-code/pulumi/>
  - The developer recently stated the end of support for this community image, but there will most probably be forks.
