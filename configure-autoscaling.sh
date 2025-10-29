#!/bin/bash
# scripts/configure-autoscaling.sh

echo "⚙️ Configuring auto-scaling for cost optimization..."

# Configure API auto-scaling
ibmcloud ce app update --name tbcoin-api \
    --min-scale 0 \
    --max-scale 2 \
    --cpu 0.125 \
    --memory 0.25G

# Configure ML worker auto-scaling  
ibmcloud ce app update --name tbcoin-ml-worker \
    --min-scale 0 \
    --max-scale 1 \
    --cpu 0.25 \
    --memory 0.5G

echo "✅ Auto-scaling configured for cost optimization"