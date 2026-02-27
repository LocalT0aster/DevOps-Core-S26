variable "docker_host" {
  description = "Docker daemon socket."
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "project_name" {
  description = "Prefix used for Docker resource names."
  type        = string
  default     = "lab04-local"
}

variable "vm_user" {
  description = "Linux username created inside the VM-like container for SSH access."
  type        = string
  default     = "devops"
}

variable "ssh_public_key" {
  description = "SSH public key allowed to access the VM-like container."
  type        = string
  sensitive   = true
}

variable "ssh_private_key_path" {
  description = "Private key path used in the rendered SSH command output."
  type        = string
  default     = "~/.ssh/id_ed25519"
}

variable "ssh_bind_ip" {
  description = "Host IP used for SSH binding. Keep 127.0.0.1 to restrict access."
  type        = string
  default     = "127.0.0.1"
}

variable "public_bind_ip" {
  description = "Host IP used for HTTP and app ports."
  type        = string
  default     = "0.0.0.0"
}

variable "ssh_host_port" {
  description = "Host port mapped to container port 22."
  type        = number
  default     = 2222

  validation {
    condition     = var.ssh_host_port >= 1 && var.ssh_host_port <= 65535
    error_message = "ssh_host_port must be between 1 and 65535."
  }
}

variable "http_host_port" {
  description = "Host port mapped to container port 80."
  type        = number
  default     = 80

  validation {
    condition     = var.http_host_port >= 1 && var.http_host_port <= 65535
    error_message = "http_host_port must be between 1 and 65535."
  }
}

variable "app_host_port" {
  description = "Host port mapped to container port 5000."
  type        = number
  default     = 5000

  validation {
    condition     = var.app_host_port >= 1 && var.app_host_port <= 65535
    error_message = "app_host_port must be between 1 and 65535."
  }
}

variable "extra_labels" {
  description = "Additional Docker labels to attach to resources."
  type        = map(string)
  default     = {}
}
