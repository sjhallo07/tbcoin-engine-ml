#!/bin/bash
# scripts/setup-registry.sh

# Create container registry namespace
REGISTRY_NAMESPACE="tbcoin-registry"
ibmcloud cr namespace-add $REGISTRY_NAMESPACE

# Set up container registry
ibmcloud cr region-set us-south
ibmcloud cr login

echo "✅ Container registry namespace created: $REGISTRY_NAMESPACE"