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
