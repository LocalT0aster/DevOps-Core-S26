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
