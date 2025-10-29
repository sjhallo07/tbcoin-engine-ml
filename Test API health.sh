# Test API health
curl http://localhost:8000/health

# Test database connection
docker-compose exec db psql -U tbcoin_user -d tbcoin -c "SELECT COUNT(*) FROM transactions;"

# Test Redis connection
docker-compose exec redis redis-cli ping

# Check service status
docker-compose ps