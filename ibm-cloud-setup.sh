#!/bin/bash
# scripts/ibm-cloud-setup.sh

echo "🔧 Setting up IBM Cloud for TB Coin deployment..."

# Install IBM Cloud CLI
if ! command -v ibmcloud &> /dev/null; then
    echo "📥 Installing IBM Cloud CLI..."
    curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
    ibmcloud plugin install code-engine
    ibmcloud plugin install container-registry
fi

# Login to IBM Cloud
echo "🔐 Logging into IBM Cloud..."
ibmcloud login --sso

# Target resource group
ibmcloud target -g Default

# Check free tier quotas
echo "📊 Checking free tier quotas..."
ibmcloud ce proj limit