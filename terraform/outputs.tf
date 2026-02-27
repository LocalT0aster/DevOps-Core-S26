output "vm_name" {
  description = "Name of the VM-like Docker container."
  value       = docker_container.vm.name
}

output "network_name" {
  description = "Name of the Docker network (VPC equivalent)."
  value       = docker_network.lab04.name
}

output "container_ip" {
  description = "Container IP inside the Docker network."
  value       = one(docker_container.vm.network_data).ip_address
}

output "public_ip_equivalent" {
  description = "Host endpoint used as public access in the local provider setup."
  value       = "127.0.0.1"
}

output "ssh_command" {
  description = "SSH command for the VM-like container."
  value       = "ssh -i ${var.ssh_private_key_path} -p ${var.ssh_host_port} ${var.vm_user}@127.0.0.1"
}

output "container_shell_command" {
  description = "Direct shell access without SSH."
  value       = "docker exec -it ${docker_container.vm.name} /bin/bash"
}

output "http_url" {
  description = "HTTP endpoint (port 80 equivalent)."
  value       = "http://127.0.0.1:${var.http_host_port}"
}

output "app_url" {
  description = "Application endpoint (port 5000 equivalent)."
  value       = "http://127.0.0.1:${var.app_host_port}"
}
