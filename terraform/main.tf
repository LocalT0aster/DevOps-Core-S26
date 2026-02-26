provider "docker" {
  host = var.docker_host
}

locals {
  vm_name = "${var.project_name}-vm"

  default_labels = {
    lab        = "04"
    managed-by = "terraform"
    project    = var.project_name
  }

  resource_labels = merge(local.default_labels, var.extra_labels)
}

resource "docker_network" "lab04" {
  name = "${var.project_name}-net"

  dynamic "labels" {
    for_each = local.resource_labels

    content {
      label = labels.key
      value = labels.value
    }
  }
}

resource "docker_image" "vm_image" {
  name         = "ubuntu:24.04"
  keep_locally = true
}

resource "docker_container" "vm" {
  name     = local.vm_name
  image    = docker_image.vm_image.image_id
  hostname = local.vm_name
  restart  = "unless-stopped"
  command  = ["/bin/bash", "-lc", "while true; do sleep 3600; done"]

  networks_advanced {
    name    = docker_network.lab04.name
    aliases = [local.vm_name]
  }

  ports {
    internal = 22
    external = var.ssh_host_port
    ip       = var.ssh_bind_ip
    protocol = "tcp"
  }

  ports {
    internal = 80
    external = var.http_host_port
    ip       = var.public_bind_ip
    protocol = "tcp"
  }

  ports {
    internal = 5000
    external = var.app_host_port
    ip       = var.public_bind_ip
    protocol = "tcp"
  }

  dynamic "labels" {
    for_each = local.resource_labels

    content {
      label = labels.key
      value = labels.value
    }
  }
}
