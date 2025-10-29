# 1. Setup IBM Cloud environment
chmod +x scripts/ibm-cloud-setup.sh
./scripts/ibm-cloud-setup.sh

# 2. Setup container registry
chmod +x scripts/setup-registry.sh  
./scripts/setup-registry.sh

# 3. Deploy everything
chmod +x scripts/deploy-ibm-ce.sh
./scripts/deploy-ibm-ce.sh

# 4. Configure cost optimization
chmod +x scripts/configure-autoscaling.sh
./scripts/configure-autoscaling.sh

# 5. Monitor deployment
chmod +x scripts/monitor-costs.sh
./scripts/monitor-costs.sh