"""
Core Lifecycle Manager

Manages the overall lifecycle of the application including startup,
shutdown, and health monitoring.
"""

import asyncio
import logging
import signal
from typing import Callable, List, Optional, Dict, Any
from datetime import datetime

from .states import LifecycleState


logger = logging.getLogger(__name__)


class LifecycleManager:
    """
    Central lifecycle manager for the TBCoin Engine.
    
    Handles:
    - Application startup and shutdown
    - Graceful shutdown with cleanup handlers
    - Health checks and monitoring
    - State management
    """
    
    def __init__(self, app_name: str = "tbcoin-engine"):
        self.app_name = app_name
        self.state = LifecycleState.UNINITIALIZED
        self.startup_handlers: List[Callable] = []
        self.shutdown_handlers: List[Callable] = []
        self.health_checks: Dict[str, Callable] = {}
        self._start_time: Optional[datetime] = None
        self._shutdown_event = asyncio.Event()
        
    def add_startup_handler(self, handler: Callable):
        """Register a handler to be called during startup."""
        self.startup_handlers.append(handler)
        logger.info(f"Registered startup handler: {handler.__name__}")
        
    def add_shutdown_handler(self, handler: Callable):
        """Register a handler to be called during shutdown."""
        self.shutdown_handlers.append(handler)
        logger.info(f"Registered shutdown handler: {handler.__name__}")
        
    def add_health_check(self, name: str, check: Callable):
        """Register a health check function."""
        self.health_checks[name] = check
        logger.info(f"Registered health check: {name}")
        
    async def startup(self):
        """Execute startup sequence."""
        logger.info(f"Starting {self.app_name}...")
        self.state = LifecycleState.STARTING
        
        try:
            for handler in self.startup_handlers:
                logger.info(f"Executing startup handler: {handler.__name__}")
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
                    
            self._start_time = datetime.now()
            self.state = LifecycleState.RUNNING
            logger.info(f"{self.app_name} started successfully")
            
        except Exception as e:
            self.state = LifecycleState.ERROR
            logger.error(f"Startup failed: {e}", exc_info=True)
            raise
            
    async def shutdown(self):
        """Execute graceful shutdown sequence."""
        if self.state == LifecycleState.STOPPED:
            logger.warning("Already stopped")
            return
            
        logger.info(f"Shutting down {self.app_name}...")
        self.state = LifecycleState.STOPPING
        
        try:
            # Execute shutdown handlers in reverse order
            for handler in reversed(self.shutdown_handlers):
                try:
                    logger.info(f"Executing shutdown handler: {handler.__name__}")
                    if asyncio.iscoroutinefunction(handler):
                        await handler()
                    else:
                        handler()
                except Exception as e:
                    logger.error(f"Error in shutdown handler {handler.__name__}: {e}")
                    
            self.state = LifecycleState.STOPPED
            self._shutdown_event.set()
            logger.info(f"{self.app_name} shut down successfully")
            
        except Exception as e:
            self.state = LifecycleState.ERROR
            logger.error(f"Shutdown failed: {e}", exc_info=True)
            raise
            
    async def health_check(self) -> Dict[str, Any]:
        """
        Execute all health checks and return status.
        
        Returns:
            Dict containing overall health and individual check results
        """
        results = {
            "status": "healthy",
            "state": str(self.state),
            "uptime_seconds": self.uptime_seconds,
            "checks": {}
        }
        
        for name, check in self.health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check):
                    result = await check()
                else:
                    result = check()
                    
                results["checks"][name] = {
                    "status": "healthy" if result else "unhealthy",
                    "result": result
                }
                
                if not result:
                    results["status"] = "degraded"
                    
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results["checks"][name] = {
                    "status": "error",
                    "error": str(e)
                }
                results["status"] = "unhealthy"
                
        return results
        
    @property
    def uptime_seconds(self) -> Optional[float]:
        """Get application uptime in seconds."""
        if self._start_time is None:
            return None
        return (datetime.now() - self._start_time).total_seconds()
        
    @property
    def is_running(self) -> bool:
        """Check if the application is in running state."""
        return self.state == LifecycleState.RUNNING
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
            
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
    async def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()
