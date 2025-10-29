#!/bin/bash
# scripts/monitor-costs.sh

echo "💰 Monitoring IBM Cloud Free Tier Usage..."

# Check Code Engine usage
echo "📊 Code Engine Usage:"
ibmcloud ce proj current -o json | jq '.status.computed_usage'

# Check container registry usage
echo "📦 Container Registry Usage:"
ibmcloud cr quota

# Check overall free tier usage
echo "📈 Overall Free Tier Usage:"
ibmcloud billing account-usage

echo "💡 Free Tier Limits:"
echo "   - Code Engine: 400 GB-hours per month"
echo "   - Container Registry: 0.5 GB storage free"
echo "   - 256 MB of built container images per month"