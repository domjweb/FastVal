variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "fastval"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "db_admin_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "fastval_admin"
  sensitive   = true
}

variable "db_admin_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "fastval_db"
}

variable "cors_origins" {
  description = "Allowed CORS origins for the backend"
  type        = list(string)
  default     = ["http://localhost:3000", "http://localhost"]
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "FastVal"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}
