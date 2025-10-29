# services/health_monitor.py
import asyncio
import aiohttp
import logging
from datetime import datetime

class IBMHealthMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def check_services_health(self):
        """Check health of all deployed services"""
        services = {
            'api': os.getenv('API_URL', ''),
            'ml_worker': os.getenv('ML_WORKER_URL', ''),
            'database': os.getenv('DATABASE_URL', ''),
            'redis': os.getenv('REDIS_URL', '')
        }
        
        health_status = {}
        
        for service, url in services.items():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/health", timeout=10) as response:
                        health_status[service] = response.status == 200
            except Exception as e:
                health_status[service] = False
                self.logger.error(f"Health check failed for {service}: {e}")
                
        return health_status
    
    async def report_metrics(self):
        """Report metrics to IBM Cloud Monitoring"""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'tbcoin',
            'cpu_usage': await self.get_cpu_usage(),
            'memory_usage': await self.get_memory_usage(),
            'active_connections': await self.get_active_connections()
        }
        
        # Log metrics (IBM Cloud will pick these up)
        self.logger.info(f"METRICS: {metrics}")
        
        return metrics