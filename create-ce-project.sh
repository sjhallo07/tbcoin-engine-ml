#!/bin/bash
# scripts/create-ce-project.sh

echo "🏗️ Creating IBM Code Engine project..."

PROJECT_NAME="tbcoin-project"
REGION="us-south"

# Create project
ibmcloud ce project create --name $PROJECT_NAME --wait

# Select project
ibmcloud ce project select --name $PROJECT_NAME

echo "✅ Project created: $PROJECT_NAME"