terraform {
  required_version = ">= 1.9.0"

  required_providers {
    docker = {
      source  = "registry.terraform.io/kreuzwerker/docker"
      version = "~> 3.6"
    }
  }
}
