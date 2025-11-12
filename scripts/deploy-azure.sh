#!/bin/bash

# FastVal Azure Quick Deployment Script
# This script helps automate the initial Azure deployment

set -e  # Exit on error

echo "==================================="
echo "FastVal Azure Deployment Setup"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed${NC}"
    echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform is not installed${NC}"
    echo "Install from: https://www.terraform.io/downloads"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Azure. Logging in...${NC}"
    az login
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}"
echo ""

# Get user input
echo "Please provide deployment configuration:"
echo ""

read -p "Project name [fastval]: " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-fastval}

read -p "Environment (dev/staging/prod) [dev]: " ENVIRONMENT
ENVIRONMENT=${ENVIRONMENT:-dev}

read -p "Azure region [eastus]: " LOCATION
LOCATION=${LOCATION:-eastus}

read -p "Database admin username [fastvaladmin]: " DB_USERNAME
DB_USERNAME=${DB_USERNAME:-fastvaladmin}

read -sp "Database admin password: " DB_PASSWORD
echo ""

read -sp "Application secret key (or press enter to generate): " APP_SECRET
echo ""
if [ -z "$APP_SECRET" ]; then
    APP_SECRET=$(openssl rand -hex 32)
    echo -e "${GREEN}Generated secret key${NC}"
fi

# Get user's IP for database access
echo "Detecting your public IP for database access..."
USER_IP=$(curl -s ifconfig.me)
echo "Your IP: $USER_IP"
read -p "Allow this IP to access database? (y/n) [y]: " ALLOW_IP
ALLOW_IP=${ALLOW_IP:-y}

# Create terraform.tfvars
echo ""
echo "Creating terraform.tfvars..."
cd terraform

cat > terraform.tfvars <<EOF
project_name = "$PROJECT_NAME"
environment  = "$ENVIRONMENT"
location     = "$LOCATION"

db_admin_username = "$DB_USERNAME"
db_admin_password = "$DB_PASSWORD"

app_secret_key = "$APP_SECRET"

allow_dev_ip = "$([[ $ALLOW_IP == "y" ]] && echo $USER_IP || echo '')"

acr_sku                   = "Basic"
db_storage_mb             = 32768
db_sku_name               = "B_Standard_B1ms"
backend_app_service_sku   = "B1"
frontend_app_service_sku  = "B1"
backend_always_on         = true
frontend_always_on        = true
EOF

echo -e "${GREEN}✓ terraform.tfvars created${NC}"

# Initialize Terraform
echo ""
echo "Initializing Terraform..."
terraform init

# Plan deployment
echo ""
echo "Planning deployment..."
terraform plan -out=tfplan

# Confirm deployment
echo ""
echo -e "${YELLOW}Review the plan above.${NC}"
read -p "Deploy to Azure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

# Apply Terraform
echo ""
echo "Deploying to Azure..."
terraform apply tfplan

# Save outputs
echo ""
echo "Saving deployment outputs..."
terraform output > ../deployment-outputs.txt

ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server)
ACR_USERNAME=$(terraform output -raw acr_admin_username)
BACKEND_URL=$(terraform output -raw backend_url)
FRONTEND_URL=$(terraform output -raw frontend_url)
DATABASE_FQDN=$(terraform output -raw database_fqdn)

# Get ACR password
echo "Getting ACR password..."
ACR_PASSWORD=$(az acr credential show --name "${PROJECT_NAME}${ENVIRONMENT}acr" --query "passwords[0].value" -o tsv)

# Create GitHub secrets instructions
echo ""
echo -e "${GREEN}==================================="
echo "Deployment Complete!"
echo "===================================${NC}"
echo ""
echo "Backend URL:  $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Configure GitHub Secrets (Settings → Secrets → Actions):"
echo ""
echo "   ACR_LOGIN_SERVER=$ACR_LOGIN_SERVER"
echo "   ACR_USERNAME=$ACR_USERNAME"
echo "   ACR_PASSWORD=$ACR_PASSWORD"
echo ""
echo "   DATABASE_URL=postgresql://$DB_USERNAME:$DB_PASSWORD@$DATABASE_FQDN:5432/fastval?sslmode=require"
echo "   APP_SECRET_KEY=$APP_SECRET"
echo ""
echo "   AZURE_CREDENTIALS: Run this command and copy the JSON output:"
echo "   az ad sp create-for-rbac --name \"$PROJECT_NAME-github-actions\" \\"
echo "     --role contributor \\"
echo "     --scopes /subscriptions/\$(az account show --query id -o tsv)/resourceGroups/$PROJECT_NAME-$ENVIRONMENT-rg \\"
echo "     --sdk-auth"
echo ""
echo "2. Run database migrations:"
echo "   export DATABASE_URL=\"postgresql://$DB_USERNAME:$DB_PASSWORD@$DATABASE_FQDN:5432/fastval?sslmode=require\""
echo "   alembic upgrade head"
echo ""
echo "3. Push to GitHub to trigger deployment:"
echo "   git push origin main"
echo ""
echo -e "${GREEN}See DEPLOYMENT.md for detailed instructions${NC}"
