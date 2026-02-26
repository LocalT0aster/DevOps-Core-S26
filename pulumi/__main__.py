from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pulumi
import pulumi_docker as docker


@dataclass(frozen=True)
class HostPorts:
    ssh: int
    http: int
    app: int


config = pulumi.Config()

project_name: str = config.get("projectName") or "lab04-local"
vm_user: str = config.get("vmUser") or "devops"
ssh_public_key: str = config.require("sshPublicKey")
ssh_private_key_path: str = config.get("sshPrivateKeyPath") or "~/.ssh/id_ed25519"
ssh_bind_ip: str = config.get("sshBindIp") or "127.0.0.1"
public_bind_ip: str = config.get("publicBindIp") or "0.0.0.0"

ports = HostPorts(
    ssh=config.get_int("sshHostPort") or 2222,
    http=config.get_int("httpHostPort") or 8080,
    app=config.get_int("appHostPort") or 5000,
)

labels: dict[str, str] = {
    "lab": "04",
    "managed-by": "pulumi",
    "project": project_name,
}

bootstrap_script = (Path(__file__).resolve().parent.parent / "docker" / "provision_vm.sh").read_text(
    encoding="utf-8"
)

network = docker.Network(
    "lab04-net",
    name=f"{project_name}-net",
    labels=[docker.NetworkLabelArgs(label=k, value=v) for k, v in labels.items()],
)

image = docker.RemoteImage(
    "lab04-vm-image",
    name="ubuntu:24.04",
    keep_locally=True,
)

container = docker.Container(
    "lab04-vm",
    name=f"{project_name}-vm",
    image=image.repo_digest,
    hostname=f"{project_name}-vm",
    restart="unless-stopped",
    command=["/bin/bash", "-lc", bootstrap_script],
    envs=[f"VM_USER={vm_user}", f"SSH_PUBLIC_KEY={ssh_public_key}"],
    ports=[
        docker.ContainerPortArgs(internal=22, external=ports.ssh, ip=ssh_bind_ip, protocol="tcp"),
        docker.ContainerPortArgs(internal=80, external=ports.http, ip=public_bind_ip, protocol="tcp"),
        docker.ContainerPortArgs(internal=5000, external=ports.app, ip=public_bind_ip, protocol="tcp"),
    ],
    labels=[docker.ContainerLabelArgs(label=k, value=v) for k, v in labels.items()],
    networks_advanced=[
        docker.ContainerNetworksAdvancedArgs(
            name=network.name,
            aliases=[f"{project_name}-vm"],
        )
    ],
)

pulumi.export("vmName", container.name)
pulumi.export("networkName", network.name)
pulumi.export("publicIpEquivalent", "127.0.0.1")
pulumi.export("sshCommand", f"ssh -i {ssh_private_key_path} -p {ports.ssh} {vm_user}@127.0.0.1")
pulumi.export("containerShellCommand", f"docker exec -it {project_name}-vm /bin/bash")
pulumi.export("httpUrl", f"http://127.0.0.1:{ports.http}")
pulumi.export("appUrl", f"http://127.0.0.1:{ports.app}")
