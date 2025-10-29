#!/bin/bash
# scripts/build-push-images.sh

set -e

echo "🐳 Building and pushing images to IBM Container Registry..."

REGISTRY_REGION="us-south"
REGISTRY_NAMESPACE="tbcoin-registry"
IMAGE_TAG="v1.0.0"

# Build API image
echo "📦 Building API image..."
docker build -t $REGISTRY_REGION.icr.io/$REGISTRY_NAMESPACE/tbcoin-api:$IMAGE_TAG -f Dockerfile.ibm .

# Build ML Worker image
echo "🤖 Building ML Worker image..."
docker build -t $REGISTRY_REGION.icr.io/$REGISTRY_NAMESPACE/tbcoin-ml-worker:$IMAGE_TAG -f Dockerfile.ml.ibm .

# Build Blockchain Listener image
echo "🔗 Building Blockchain Listener image..."
docker build -t $REGISTRY_REGION.icr.io/$REGISTRY_NAMESPACE/tbcoin-blockchain-listener:$IMAGE_TAG -f Dockerfile.listener .

# Push images
echo "📤 Pushing images to IBM Container Registry..."
docker push $REGISTRY_REGION.icr.io/$REGISTRY_NAMESPACE/tbcoin-api:$IMAGE_TAG
docker push $REGISTRY_REGION.icr.io/$REGISTRY_NAMESPACE/tbcoin-ml-worker:$IMAGE_TAG
docker push $REGISTRY_REGION.icr.io/$REGISTRY_NAMESPACE/tbcoin-blockchain-listener:$IMAGE_TAG

echo "✅ All images pushed successfully!"