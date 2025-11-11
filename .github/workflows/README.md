# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for automated testing, building, and deployment.

## Workflows

### 1. Backend CI (`backend-ci.yml`)
Runs on every push/PR to backend code:
- **Linting**: Checks code style with flake8
- **Testing**: Runs pytest with coverage
- **Build**: Creates Docker image for main branch

### 2. Frontend CI (`frontend-ci.yml`)
Runs on every push/PR to frontend code:
- **Linting**: ESLint checks
- **Testing**: Jest tests with coverage
- **Build**: Production build

### 3. Deploy (`deploy.yml`)
Deploys to Azure on push to main:
1. **Build & Push**: Docker images to ACR
2. **Deploy Infrastructure**: Terraform apply
3. **Deploy Containers**: Update Container Apps
4. **Smoke Tests**: Verify deployment

## Setup

### Required Secrets

Configure these in GitHub repository settings (Settings → Secrets and variables → Actions):

#### `AZURE_CREDENTIALS`
Azure service principal credentials in JSON format:

```json
{
  "clientId": "<your-client-id>",
  "clientSecret": "<your-client-secret>",
  "subscriptionId": "<your-subscription-id>",
  "tenantId": "<your-tenant-id>"
}
```

Create service principal:
```bash
az ad sp create-for-rbac \
  --name "fastval-github-actions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth
```

#### `DB_ADMIN_USERNAME`
PostgreSQL administrator username

#### `DB_ADMIN_PASSWORD`
PostgreSQL administrator password (must meet Azure complexity requirements)

### Optional Secrets

- `CODECOV_TOKEN`: For code coverage reporting
- `SLACK_WEBHOOK`: For deployment notifications

## Usage

### Automatic Deployment

Push to main branch:
```bash
git push origin main
```

### Manual Deployment

1. Go to Actions tab in GitHub
2. Select "Deploy to Azure" workflow
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

## Environments

### Development
- Triggered by push to `develop` branch
- Deploys to dev environment
- Limited resources

### Production
- Triggered by push to `main` branch
- Requires manual approval (recommended)
- Full resources

## Branch Protection

Recommended branch protection rules for `main`:

1. Require pull request reviews
2. Require status checks to pass:
   - Backend CI
   - Frontend CI
3. Require branches to be up to date
4. Include administrators

## Monitoring

### Workflow Status
- View in GitHub Actions tab
- Email notifications for failures
- Status badges in README

### Deployment Logs
```bash
# View workflow runs
gh run list --workflow=deploy.yml

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

## Troubleshooting

### Authentication Failures
```bash
# Test Azure credentials
az login --service-principal \
  -u <client-id> \
  -p <client-secret> \
  --tenant <tenant-id>
```

### Docker Build Failures
- Check Dockerfile syntax
- Verify base image availability
- Check disk space in runner

### Terraform Errors
- Verify state backend access
- Check resource quotas
- Review variable values

### Container App Deployment Failures
```bash
# Check container logs
az containerapp logs show \
  --name fastval-prod-backend \
  --resource-group fastval-prod-rg \
  --follow

# Check revision status
az containerapp revision list \
  --name fastval-prod-backend \
  --resource-group fastval-prod-rg
```

## Cost Optimization

- Workflows run on GitHub-hosted runners (free for public repos)
- Private repos: 2,000 minutes/month free
- Consider self-hosted runners for heavy usage

## Security Best Practices

1. ✅ Use secrets for sensitive data
2. ✅ Limit service principal permissions
3. ✅ Enable branch protection
4. ✅ Review workflow logs regularly
5. ✅ Rotate credentials periodically
6. ✅ Use environment-specific secrets
7. ✅ Enable Dependabot for dependencies

## Advanced Configuration

### Matrix Builds
Test against multiple Python/Node versions:
```yaml
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]
```

### Parallel Jobs
Run jobs concurrently:
```yaml
jobs:
  backend:
    # ...
  frontend:
    # runs in parallel with backend
```

### Conditional Execution
```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### Caching
Speed up builds:
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure GitHub Actions](https://github.com/Azure/actions)
- [Terraform GitHub Actions](https://github.com/hashicorp/setup-terraform)
