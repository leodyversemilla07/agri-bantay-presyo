# Azure Deployment Guide - Agri Bantay Presyo

This guide covers deploying Agri Bantay Presyo to Azure Container Apps.

## Prerequisites

- Azure subscription
- Azure Container Registry (ACR)
- Azure CLI (`az`)

## Step 1: Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create --name agri-bantay-rg --location eastus

# Create Container Registry
az acr create --resource-group agri-bantay-rg --name agriBantayCR --sku Standard

# Create Container Apps environment
az containerapp env create \
  --name agri-bantay-env \
  --resource-group agri-bantay-rg \
  --location eastus
```

## Step 2: Create Azure Service Principal

```bash
# Create service principal with Contributor role
az ad sp create-for-rbac --name agri-bantay-sp \
  --role Contributor \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/agri-bantay-rg
```

Save the output credentials for GitHub secrets.

## Step 3: Configure GitHub Secrets

Go to your repository settings → Secrets and variables → Actions, add these secrets:

| Secret | Description | Example |
|--------|-------------|---------|
| `AZURE_CR` | Full ACR login server | `agribantaycr.azurecr.io` |
| `AZURE_CR_NAME` | ACR name | `agriBantayCR` |
| `AZURE_CR_USERNAME` | Service principal appId | `xxxx-xxxx-xxxx` |
| `AZURE_CR_PASSWORD` | Service principal password | `xxxx~xxxx` |
| `AZURE_SP` | Service principal JSON | `{"clientId":..., "clientSecret":..., "subscriptionId":..., "tenantId":...}` |
| `AZURE_RG` | Resource group name | `agri-bantay-rg` |
| `AZURE_APP_NAME` | Container app name | `agri-bantay-presyo` |
| `AZURE_ENV` | Environment name | `agri-bantay-env` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@server:5432/db` |
| `REDIS_URL` | Redis connection | `redis://redis:6379/0` |
| `API_KEY` | API key for endpoints | `your-api-key` |

## Step 4: Deploy PostgreSQL and Redis

Option A: Use Azure managed services:
```bash
# Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group agri-bantay-rg \
  --name agri-bantay-db

# Azure Cache for Redis
az redis create \
  --resource-group agri-bantay-rg \
  --name agri-bantay-redis \
  --sku Basic --vm-size c0
```

Option B: Use Azure Container Instances for DB/Redis:
```bash
# PostgreSQL
az container create \
  --resource-group agri-bantay-rg \
  --name agri-bantay-postgres \
  --image postgres:16 \
  --environment-variables \
    POSTGRES_PASSWORD=your-secure-password \
    POSTGRES_DB=bantay_presyo \
  --port 5432

# Redis
az container create \
  --resource-group agri-bantay-rg \
  --name agri-bantay-redis \
  --image redis:7-alpine \
  --port 6379
```

## Step 5: Manual Test Deploy

```bash
# Build and push manually
az acr build \
  --registry agriBantayCR \
  --image agri-bantay-presyo:latest \
  --file Dockerfile .

# Deploy to Container Apps
az containerapp create \
  --name agri-bantay-presyo \
  --resource-group agri-bantay-rg \
  --image agriBantayCR.azurecr.io/agri-bantay-presyo:latest \
  --environment agri-bantay-env \
  --cpu 0.25 --memory 0.5Gi \
  --port 8000 \
  --min-replicas 1 \
  --max-replicas 1 \
  --ingress external \
  --target-port 8000
```

## Step 6: Set Environment Variables

```bash
az containerapp update \
  --name agri-bantay-presyo \
  --resource-group agri-bantay-rg \
  --set-env-vars \
    APP_ENV=production \
    DATABASE_URL="postgresql://user:pass@server:5432/db" \
    REDIS_URL="redis://server:6379/0" \
    API_KEY="your-api-key" \
    LOG_LEVEL=INFO \
    LOG_AS_JSON=true
```

## Step 7: Enable GitHub Actions

Push to main branch will trigger the CD workflow to build and deploy automatically.

## Health Checks

```bash
# Check container status
az containerapp show --name agri-bantay-presyo --resource-group agri-bantay-rg

# View logs
az containerapp logs show --name agri-bantay-presyo --resource-group agri-bantay-rg --tail 100
```

## Scaling

Azure Container Apps supports auto-scaling:

```bash
az containerapp update \
  --name agri-bantay-presyo \
  --resource-group agri-bantay-rg \
  --min-replicas 0 \
  --max-replicas 5 \
  --scale-rule-name http-scaling \
  --scale-rule-type http \
  --scale-rule-metadata "minReplicas=0" "maxReplicas=5" "metadata={}"
```

Note: For Celery worker, you may want to deploy it as a separate container app with `min-replicas=1` (always running).
