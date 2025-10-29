#!/bin/bash
# scripts/deploy-ibm-ce.sh

set -e

echo "🚀 Deploying TB Coin to IBM Code Engine..."

# Load environment
source .env

# Build and push images
./scripts/build-push-images.sh

# Create project if it doesn't exist
if ! ibmcloud ce project get --name tbcoin-project > /dev/null 2>&1; then
    ./scripts/create-ce-project.sh
fi

# Setup secrets
./scripts/setup-secrets.sh

# Deploy applications
echo "📦 Deploying applications..."

# Deploy API
ibmcloud ce app create --name tbcoin-api \
    --image us-south.icr.io/tbcoin-registry/tbcoin-api:v1.0.0 \
    --port 8000 \
    --env-from-secret tbcoin-secrets \
    --cpu 0.25 \
    --memory 0.5G \
    --min-scale 1 \
    --max-scale 3

# Deploy ML Worker
ibmcloud ce app create --name tbcoin-ml-worker \
    --image us-south.icr.io/tbcoin-registry/tbcoin-ml-worker:v1.0.0 \
    --env-from-secret tbcoin-secrets \
    --cpu 0.5 \
    --memory 1G \
    --min-scale 1 \
    --max-scale 2

# Create blockchain listener job
ibmcloud ce job create --name tbcoin-blockchain-listener \
    --image us-south.icr.io/tbcoin-registry/tbcoin-blockchain-listener:v1.0.0 \
    --env-from-secret tbcoin-secrets \
    --cpu 0.25 \
    --memory 0.5G \
    --retry-limit 3

# Submit job to run
ibmcloud ce jobrun submit --name tbcoin-listener-run --job tbcoin-blockchain-listener

echo "✅ Deployment completed!"
echo "📊 Checking application status..."
ibmcloud ce app list
ibmcloud ce job list
ibmcloud ce jobrun list

# Get application URLs
API_URL=$(ibmcloud ce app get --name tbcoin-api -o json | jq -r '.status.url')
echo "🌐 API URL: $API_URL"
echo "📚 API Docs: $API_URL/docs"
echo "❤️  Health Check: $API_URL/health"