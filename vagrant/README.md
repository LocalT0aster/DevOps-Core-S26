# Vagrant (libvirt)

This VM is configured for the `libvirt` provider and uses:

- Box: `alvistack/ubuntu-24.04`

## Requirements

- `vagrant`
- `libvirt` + `qemu`/`kvm`
- Vagrant plugin: `vagrant-libvirt`

## Usage

From repository root:

```bash
cd vagrant
vagrant plugin install vagrant-libvirt
vagrant up
vagrant ssh
```

`vagrant up` automatically runs `shared/provision.sh` as root.
To re-run provisioning on an existing VM:

```bash
vagrant provision
```

Provisioning is split into two stages:

- `shared/provision.sh` (kernel/package update stage)
- automatic reboot between stages
- `shared/provision-post-kernel.sh` (post-kernel stage with ansible install)

SSH key setup:

- host private key path: `~/.ssh/vagrant`
- host public key path: `~/.ssh/vagrant.pub`
- public key is added to `/home/vagrant/.ssh/authorized_keys` during provisioning

Static VM IP:

- default: `192.168.121.50`
- override: `VM_IP=192.168.121.60 vagrant up`

This setup uses:

- management NIC (`eth0`, DHCP) for Vagrant internals
- static NIC (`eth1`, fixed IP above) for your direct SSH usage

If the VM already existed before static IP was added, recreate it once:

```bash
vagrant destroy -f
vagrant up --provider=libvirt
```

`~/.ssh/config` example:

```sshconfig
Host vagrant
	HostName 192.168.121.50
	User vagrant
	IdentityFile ~/.ssh/vagrant
```
