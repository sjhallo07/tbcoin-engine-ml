#!/bin/bash
# scripts/setup-secrets.sh

echo "🔐 Setting up secrets in IBM Code Engine..."

# Create secrets for sensitive data
ibmcloud ce secret create --name tbcoin-secrets \
    --from-literal "database-url=postgresql://user:pass@host:5432/tbcoin" \
    --from-literal "redis-url=redis://host:6379" \
    --from-literal "jwt-secret=your-jwt-secret-here" \
    --from-literal "solana-private-key=your-private-key"

echo "✅ Secrets created successfully"