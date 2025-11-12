# FastVal Azure Deployment Guide

## Prerequisites

Before deploying to Azure, ensure you have:

1. **Azure Account** with active subscription
2. **Azure CLI** installed and configured
   ```bash
   az --version
   az login
   ```

3. **Terraform** installed (>= 1.0)
   ```bash
   terraform --version
   ```

4. **Docker** installed for local testing
   ```bash
   docker --version
   ```

5. **Git** with GitHub repository access

## Step 1: Set Up Azure Resources with Terraform

### 1.1 Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:
```hcl
project_name = "fastval"
environment  = "prod"  # or "dev", "staging"
location     = "eastus"

db_admin_username = "fastvaladmin"
db_admin_password = "SecurePassword123!"
app_secret_key = "your-secret-key-here"

# Optional: Your IP for database access
allow_dev_ip = "1.2.3.4"
```

### 1.2 Initialize and Apply Terraform

```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -out=tfplan

# Apply the configuration
terraform apply tfplan
```

**Save the outputs** - you'll need them for GitHub Actions:
```bash
terraform output
```

Important outputs:
- `acr_login_server`
- `backend_url`
- `frontend_url`
- `database_fqdn`

### 1.3 Get ACR Credentials

```bash
# Get ACR admin password
az acr credential show --name fastvaldevacr --query "passwords[0].value" -o tsv
```

## Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

### Required Secrets

1. **ACR_LOGIN_SERVER**
   - Value from `terraform output acr_login_server`
   - Example: `fastvaldevacr.azurecr.io`

2. **ACR_USERNAME**
   - Value from `terraform output acr_admin_username`

3. **ACR_PASSWORD**
   - Get with: `az acr credential show --name fastvaldevacr`

4. **AZURE_CREDENTIALS**
   - Create service principal:
   ```bash
   az ad sp create-for-rbac --name "fastval-github-actions" \
     --role contributor \
     --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/fastval-dev-rg \
     --sdk-auth
   ```
   - Copy the entire JSON output

5. **DATABASE_URL**
   - Format: `postgresql://USERNAME:PASSWORD@HOST:5432/DATABASE?sslmode=require`
   - Get from `terraform output database_fqdn`

6. **APP_SECRET_KEY**
   - Generate: `openssl rand -hex 32`

## Step 3: Initial Database Setup

### 3.1 Allow Your IP to Access Database

```bash
az postgres flexible-server firewall-rule create \
  --resource-group fastval-dev-rg \
  --name fastval-dev-psql \
  --rule-name AllowMyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

### 3.2 Run Migrations Locally

```bash
# Set environment variables
export DATABASE_URL="postgresql://fastvaladmin:YourPassword@fastval-dev-psql.postgres.database.azure.com:5432/fastval?sslmode=require"

# Run migrations
alembic upgrade head
```

Or run from Azure Cloud Shell:
```bash
# Install dependencies in Cloud Shell
pip install alembic psycopg2-binary sqlalchemy

# Clone repo and run migrations
git clone https://github.com/domjweb/FastVal.git
cd FastVal
alembic upgrade head
```

## Step 4: Deploy Application

### Option A: Deploy via GitHub Actions (Recommended)

1. Push to main branch:
   ```bash
   git push origin main
   ```

2. Monitor deployment:
   - Go to GitHub → Actions tab
   - Watch the "Deploy to Azure" workflow

### Option B: Manual Docker Deployment

```bash
# Login to ACR
az acr login --name fastvaldevacr

# Build and push backend
docker build -t fastvaldevacr.azurecr.io/fastval-backend:latest -f Dockerfile.backend .
docker push fastvaldevacr.azurecr.io/fastval-backend:latest

# Build and push frontend
docker build -t fastvaldevacr.azurecr.io/fastval-frontend:latest \
  --build-arg REACT_APP_API_URL=https://fastval-dev-backend.azurewebsites.net/api/v1 \
  -f Dockerfile.frontend ./frontend
docker push fastvaldevacr.azurecr.io/fastval-frontend:latest

# Restart App Services to pull new images
az webapp restart --name fastval-dev-backend --resource-group fastval-dev-rg
az webapp restart --name fastval-dev-frontend --resource-group fastval-dev-rg
```

## Step 5: Verify Deployment

### 5.1 Check Backend Health

```bash
# Get backend URL
BACKEND_URL=$(terraform output -raw backend_url)

# Test health endpoint
curl $BACKEND_URL/health

# Test API docs
open $BACKEND_URL/docs
```

### 5.2 Check Frontend

```bash
# Get frontend URL
FRONTEND_URL=$(terraform output -raw frontend_url)

# Open in browser
open $FRONTEND_URL
```

### 5.3 Check Application Logs

```bash
# Backend logs
az webapp log tail --name fastval-dev-backend --resource-group fastval-dev-rg

# Frontend logs
az webapp log tail --name fastval-dev-frontend --resource-group fastval-dev-rg
```

## Step 6: Configure Custom Domain (Optional)

### 6.1 Add Custom Domain to App Service

```bash
# Add domain
az webapp config hostname add \
  --webapp-name fastval-dev-backend \
  --resource-group fastval-dev-rg \
  --hostname api.yourdomain.com

az webapp config hostname add \
  --webapp-name fastval-dev-frontend \
  --resource-group fastval-dev-rg \
  --hostname app.yourdomain.com
```

### 6.2 Enable HTTPS with Managed Certificate

```bash
# Create managed certificate
az webapp config ssl create \
  --resource-group fastval-dev-rg \
  --name fastval-dev-backend \
  --hostname api.yourdomain.com

# Bind certificate
az webapp config ssl bind \
  --resource-group fastval-dev-rg \
  --name fastval-dev-backend \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

## Monitoring and Maintenance

### View Application Metrics

```bash
# CPU and Memory
az monitor metrics list \
  --resource /subscriptions/SUB_ID/resourceGroups/fastval-dev-rg/providers/Microsoft.Web/sites/fastval-dev-backend \
  --metric "CpuPercentage,MemoryPercentage"
```

### Enable Application Insights (Optional)

```bash
# Create Application Insights
az monitor app-insights component create \
  --app fastval-insights \
  --location eastus \
  --resource-group fastval-dev-rg

# Get instrumentation key
az monitor app-insights component show \
  --app fastval-insights \
  --resource-group fastval-dev-rg \
  --query instrumentationKey -o tsv
```

Add to App Service settings:
```bash
az webapp config appsettings set \
  --name fastval-dev-backend \
  --resource-group fastval-dev-rg \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=<key>
```

## Troubleshooting

### Issue: Database Connection Failed

**Solution:**
```bash
# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group fastval-dev-rg \
  --name fastval-dev-psql

# Verify connection string
az postgres flexible-server show \
  --resource-group fastval-dev-rg \
  --name fastval-dev-psql \
  --query "fullyQualifiedDomainName"
```

### Issue: Container Pull Failed

**Solution:**
```bash
# Verify ACR credentials in App Service
az webapp config container show \
  --name fastval-dev-backend \
  --resource-group fastval-dev-rg

# Update ACR credentials
az webapp config container set \
  --name fastval-dev-backend \
  --resource-group fastval-dev-rg \
  --docker-registry-server-url https://fastvaldevacr.azurecr.io \
  --docker-registry-server-user <username> \
  --docker-registry-server-password <password>
```

### Issue: App Not Starting

**Solution:**
```bash
# Check logs
az webapp log tail --name fastval-dev-backend --resource-group fastval-dev-rg

# SSH into container
az webapp ssh --name fastval-dev-backend --resource-group fastval-dev-rg

# Check environment variables
az webapp config appsettings list --name fastval-dev-backend --resource-group fastval-dev-rg
```

### Issue: CORS Errors

**Solution:**
```bash
# Verify CORS settings
az webapp cors show --name fastval-dev-backend --resource-group fastval-dev-rg

# Update CORS
az webapp cors add \
  --name fastval-dev-backend \
  --resource-group fastval-dev-rg \
  --allowed-origins "https://fastval-dev-frontend.azurewebsites.net"
```

## Cost Management

### Estimate Monthly Costs

- **App Service B1 (2 instances)**: ~$110/month
- **PostgreSQL B_Standard_B1ms**: ~$25/month
- **Container Registry Basic**: ~$5/month
- **Bandwidth**: Variable (typically $0.05-0.10/GB)

**Total estimated**: ~$140-150/month

### Cost Optimization Tips

1. **Use B1 tier for dev** (scale up for production)
2. **Enable auto-scaling** only when needed
3. **Stop dev/staging apps** outside business hours
4. **Use Azure Reservations** for 1-3 year commitments (30-50% savings)

```bash
# Stop app service (dev/staging only)
az webapp stop --name fastval-dev-backend --resource-group fastval-dev-rg
az webapp stop --name fastval-dev-frontend --resource-group fastval-dev-rg

# Start app service
az webapp start --name fastval-dev-backend --resource-group fastval-dev-rg
az webapp start --name fastval-dev-frontend --resource-group fastval-dev-rg
```

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

Or manually:
```bash
az group delete --name fastval-dev-rg --yes --no-wait
```

## Next Steps

1. **Set up CI/CD** - Push to main automatically deploys
2. **Add monitoring** - Application Insights for APM
3. **Configure backups** - PostgreSQL automated backups
4. **Add staging environment** - Create separate resource group
5. **Implement blue-green deployment** - Zero-downtime updates

## Support

- **Documentation**: See `/terraform/README.md` and inline code comments
- **Issues**: GitHub Issues at https://github.com/domjweb/FastVal/issues
- **Azure Support**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
