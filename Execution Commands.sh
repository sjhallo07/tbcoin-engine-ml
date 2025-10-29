# Make the deployment script executable
chmod +x scripts/deploy.sh

# Execute the deployment
./scripts/deploy.sh

# Or run manually step by step:
docker-compose up -d
docker-compose logs -f api  # Monitor API logs

# Check service status
docker-compose ps

# View logs
docker-compose logs api
docker-compose logs blockchain-listener
docker-compose logs ml-worker