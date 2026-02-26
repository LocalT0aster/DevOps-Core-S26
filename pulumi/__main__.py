from __future__ import annotations

from dataclasses import dataclass

import pulumi
import pulumi_docker as docker


@dataclass(frozen=True)
class HostPorts:
    ssh: int
    http: int
    app: int


config = pulumi.Config()

project_name: str = config.get("projectName") or "lab04-local"
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
    command=["/bin/bash", "-lc", "while true; do sleep 3600; done"],
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
pulumi.export("sshCommand", f"ssh -p {ports.ssh} ubuntu@127.0.0.1")
pulumi.export("containerShellCommand", f"docker exec -it {project_name}-vm /bin/bash")
pulumi.export("httpUrl", f"http://127.0.0.1:{ports.http}")
pulumi.export("appUrl", f"http://127.0.0.1:{ports.app}")
