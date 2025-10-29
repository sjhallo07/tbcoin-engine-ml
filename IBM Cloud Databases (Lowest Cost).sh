# Create PostgreSQL instance (lowest cost tier)
ibmcloud resource service-instance-create tbcoin-postgresql databases-for-postgresql standard us-south \
    -g Default -p '{"members_memory_allocation_mb": 3072, "members_disk_allocation_mb": 5120}'

# Create Redis instance
ibmcloud resource service-instance-create tbcoin-redis databases-for-redis standard us-south \
    -g Default -p '{"memory_allocation_mb": 1024}'