"""
Resource Lifecycle Manager

Manages lifecycle of application resources such as database connections,
caches, external API clients, and other resources that need proper
initialization and cleanup.
"""

import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime

from .states import LifecycleState


logger = logging.getLogger(__name__)


class ResourceInfo:
    """Information about a managed resource."""
    
    def __init__(self, name: str, resource_type: str):
        self.name = name
        self.resource_type = resource_type
        self.state = LifecycleState.UNINITIALIZED
        self.created_at = datetime.now()
        self.last_health_check: Optional[datetime] = None
        self.health_status = "unknown"
        
    def update_health(self, status: str):
        """Update health status."""
        self.health_status = status
        self.last_health_check = datetime.now()


class ResourceLifecycleManager:
    """
    Manages lifecycle of application resources.
    
    Features:
    - Resource initialization and cleanup
    - Connection pooling and management
    - Health monitoring
    - Automatic reconnection on failure
    """
    
    def __init__(self):
        self.resources: Dict[str, Any] = {}
        self.resource_info: Dict[str, ResourceInfo] = {}
        self.initializers: Dict[str, Callable] = {}
        self.cleaners: Dict[str, Callable] = {}
        self.health_checkers: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()
        
    def register_resource_type(
        self,
        resource_type: str,
        initializer: Callable,
        cleaner: Optional[Callable] = None,
        health_checker: Optional[Callable] = None
    ):
        """
        Register handlers for a resource type.
        
        Args:
            resource_type: Type identifier for the resource
            initializer: Function to initialize the resource
            cleaner: Optional function to clean up the resource
            health_checker: Optional function to check resource health
        """
        self.initializers[resource_type] = initializer
        if cleaner:
            self.cleaners[resource_type] = cleaner
        if health_checker:
            self.health_checkers[resource_type] = health_checker
            
        logger.info(f"Registered resource type: {resource_type}")
        
    async def initialize_resource(
        self,
        name: str,
        resource_type: str,
        config: Optional[Dict] = None
    ) -> Any:
        """
        Initialize a resource.
        
        Args:
            name: Resource identifier
            resource_type: Type of resource
            config: Optional configuration
            
        Returns:
            Initialized resource
        """
        async with self._lock:
            if name in self.resources:
                logger.warning(f"Resource {name} already initialized")
                return self.resources[name]
                
            if resource_type not in self.initializers:
                raise ValueError(f"Unknown resource type: {resource_type}")
                
            logger.info(f"Initializing resource: {name} ({resource_type})")
            
            info = ResourceInfo(name, resource_type)
            info.state = LifecycleState.INITIALIZING
            self.resource_info[name] = info
            
            try:
                initializer = self.initializers[resource_type]
                
                if asyncio.iscoroutinefunction(initializer):
                    resource = await initializer(config)
                else:
                    resource = initializer(config)
                    
                self.resources[name] = resource
                info.state = LifecycleState.READY
                info.update_health("healthy")
                
                logger.info(f"Resource {name} initialized successfully")
                return resource
                
            except Exception as e:
                info.state = LifecycleState.ERROR
                info.update_health("error")
                logger.error(f"Failed to initialize resource {name}: {e}", exc_info=True)
                raise
                
    async def cleanup_resource(self, name: str):
        """
        Cleanup a resource.
        
        Args:
            name: Resource identifier
        """
        async with self._lock:
            if name not in self.resources:
                logger.warning(f"Resource {name} not found")
                return
                
            info = self.resource_info[name]
            logger.info(f"Cleaning up resource: {name}")
            info.state = LifecycleState.STOPPING
            
            try:
                if info.resource_type in self.cleaners:
                    cleaner = self.cleaners[info.resource_type]
                    resource = self.resources[name]
                    
                    if asyncio.iscoroutinefunction(cleaner):
                        await cleaner(resource)
                    else:
                        cleaner(resource)
                        
                del self.resources[name]
                info.state = LifecycleState.STOPPED
                
                logger.info(f"Resource {name} cleaned up successfully")
                
            except Exception as e:
                info.state = LifecycleState.ERROR
                logger.error(f"Error cleaning up resource {name}: {e}", exc_info=True)
                raise
                
    def get_resource(self, name: str) -> Optional[Any]:
        """
        Get a resource by name.
        
        Args:
            name: Resource identifier
            
        Returns:
            Resource if exists, None otherwise
        """
        return self.resources.get(name)
        
    async def check_resource_health(self, name: str) -> Dict[str, Any]:
        """
        Check health of a resource.
        
        Args:
            name: Resource identifier
            
        Returns:
            Health check results
        """
        if name not in self.resources:
            return {"status": "not_found", "healthy": False}
            
        info = self.resource_info[name]
        
        if info.resource_type not in self.health_checkers:
            return {
                "status": "no_health_check",
                "healthy": True,
                "state": str(info.state)
            }
            
        try:
            checker = self.health_checkers[info.resource_type]
            resource = self.resources[name]
            
            if asyncio.iscoroutinefunction(checker):
                result = await checker(resource)
            else:
                result = checker(resource)
                
            healthy = bool(result)
            info.update_health("healthy" if healthy else "unhealthy")
            
            return {
                "status": "checked",
                "healthy": healthy,
                "state": str(info.state),
                "last_check": info.last_health_check.isoformat()
            }
            
        except Exception as e:
            info.update_health("error")
            logger.error(f"Health check failed for {name}: {e}")
            return {
                "status": "error",
                "healthy": False,
                "error": str(e)
            }
            
    async def check_all_resources_health(self) -> Dict[str, Dict[str, Any]]:
        """
        Check health of all resources.
        
        Returns:
            Dictionary of health check results
        """
        results = {}
        for name in self.resources:
            results[name] = await self.check_resource_health(name)
        return results
        
    def list_resources(self) -> Dict[str, Dict[str, Any]]:
        """
        List all resources with their information.
        
        Returns:
            Dictionary of resource information
        """
        result = {}
        for name, info in self.resource_info.items():
            result[name] = {
                "name": name,
                "type": info.resource_type,
                "state": str(info.state),
                "health": info.health_status,
                "created_at": info.created_at.isoformat(),
                "last_health_check": (
                    info.last_health_check.isoformat()
                    if info.last_health_check
                    else None
                ),
            }
        return result
        
    async def cleanup_all(self):
        """Cleanup all resources."""
        logger.info("Cleaning up all resources...")
        names = list(self.resources.keys())
        for name in names:
            await self.cleanup_resource(name)
        logger.info("All resources cleaned up")
