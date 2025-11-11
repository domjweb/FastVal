# Terraform Azure Deployment

This directory contains Terraform configurations for deploying FastVal to Azure.

## Architecture

- **Azure Container Apps**: For backend and frontend
- **Azure Container Registry**: For Docker images
- **Azure Database for PostgreSQL**: Managed database
- **Log Analytics**: For monitoring and logging

## Prerequisites

1. Azure CLI installed and logged in:
   ```bash
   az login
   ```

2. Terraform installed (>= 1.0)

3. Azure subscription with appropriate permissions

## Setup

1. **Initialize Terraform**:
   ```bash
   cd terraform
   terraform init
   ```

2. **Create `terraform.tfvars`** (or use environment variables):
   ```hcl
   project_name        = "fastval"
   environment         = "dev"
   location            = "eastus"
   db_admin_username   = "your_admin_username"
   db_admin_password   = "YourSecurePassword123!"
   db_name             = "fastval_db"
   cors_origins        = ["https://your-frontend-domain.com"]
   ```

3. **Review the plan**:
   ```bash
   terraform plan
   ```

4. **Apply the configuration**:
   ```bash
   terraform apply
   ```

## Deployment Steps

### 1. Build and Push Docker Images

```bash
# Login to Azure Container Registry
az acr login --name <registry-name>

# Build and push backend
docker build -f Dockerfile.backend -t <registry-name>.azurecr.io/fastval-backend:latest .
docker push <registry-name>.azurecr.io/fastval-backend:latest

# Build and push frontend
docker build -f Dockerfile.frontend -t <registry-name>.azurecr.io/fastval-frontend:latest .
docker push <registry-name>.azurecr.io/fastval-frontend:latest
```

### 2. Run Database Migrations

```bash
# Connect to backend container
az containerapp exec \
  --name fastval-dev-backend \
  --resource-group fastval-dev-rg \
  --command "alembic upgrade head"
```

## Configuration

### Environment Variables

Set these in the Container Apps or use Azure Key Vault:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Application secret key
- `ENVIRONMENT`: Environment name (dev, staging, prod)
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins

### Scaling

Container Apps auto-scale based on configuration:
- Backend: 1-3 replicas
- Frontend: 1-2 replicas

Adjust in `main.tf`:
```hcl
template {
  min_replicas = 1
  max_replicas = 5
}
```

## Monitoring

Access logs through:
- Azure Portal → Log Analytics Workspace
- Container Apps → Logs

Example query:
```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastval-dev-backend"
| order by TimeGenerated desc
```

## Security

- Database credentials stored as Terraform variables (use Azure Key Vault for production)
- Container Registry admin access enabled (use managed identity for production)
- HTTPS enforced on all Container Apps endpoints
- PostgreSQL firewall configured

## Cost Estimation

Approximate monthly costs (East US):
- Container Apps: ~$30-50
- PostgreSQL Flexible Server (B1ms): ~$15-20
- Container Registry (Basic): ~$5
- Log Analytics: ~$5-10

**Total: ~$55-85/month**

## Cleanup

To destroy all resources:
```bash
terraform destroy
```

## Alternative: AKS Deployment

For Kubernetes deployment, see `terraform/aks/` directory (if you prefer AKS over Container Apps).

## Troubleshooting

### Container won't start
```bash
# Check logs
az containerapp logs show \
  --name fastval-dev-backend \
  --resource-group fastval-dev-rg \
  --follow
```

### Database connection issues
```bash
# Test connectivity
az postgres flexible-server connect \
  --name fastval-dev-psql \
  --admin-user fastval_admin
```

### Image pull errors
```bash
# Verify ACR credentials
az acr credential show --name fastvalacrdev
```

## Production Considerations

1. **Use Azure Key Vault** for secrets
2. **Enable managed identities** instead of admin credentials
3. **Set up custom domains** and SSL certificates
4. **Configure backup retention** for database
5. **Enable monitoring and alerts**
6. **Use separate state storage** for Terraform
7. **Implement CI/CD** with GitHub Actions
