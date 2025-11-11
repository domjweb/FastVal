output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "container_registry_login_server" {
  description = "Container registry login server URL"
  value       = azurerm_container_registry.acr.login_server
}

output "postgres_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.postgres.fqdn
}

output "backend_url" {
  description = "Backend application URL"
  value       = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
}

output "frontend_url" {
  description = "Frontend application URL"
  value       = "https://${azurerm_container_app.frontend.ingress[0].fqdn}"
}

output "database_connection_string" {
  description = "Database connection string (without password)"
  value       = "postgresql://${var.db_admin_username}:****@${azurerm_postgresql_flexible_server.postgres.fqdn}:5432/${var.db_name}"
  sensitive   = true
}
