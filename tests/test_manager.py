"""
Tests for Lifecycle Manager
"""

import pytest
import asyncio
from lifecycle import LifecycleManager, LifecycleState


@pytest.mark.asyncio
async def test_lifecycle_manager_initialization():
    """Test lifecycle manager initialization."""
    manager = LifecycleManager(app_name="test-app")
    assert manager.app_name == "test-app"
    assert manager.state == LifecycleState.UNINITIALIZED
    assert not manager.is_running


@pytest.mark.asyncio
async def test_lifecycle_manager_startup():
    """Test application startup."""
    manager = LifecycleManager()
    startup_called = False
    
    def startup_handler():
        nonlocal startup_called
        startup_called = True
        
    manager.add_startup_handler(startup_handler)
    await manager.startup()
    
    assert startup_called
    assert manager.state == LifecycleState.RUNNING
    assert manager.is_running
    
    await manager.shutdown()


@pytest.mark.asyncio
async def test_lifecycle_manager_shutdown():
    """Test application shutdown."""
    manager = LifecycleManager()
    shutdown_called = False
    
    def shutdown_handler():
        nonlocal shutdown_called
        shutdown_called = True
        
    manager.add_shutdown_handler(shutdown_handler)
    await manager.startup()
    await manager.shutdown()
    
    assert shutdown_called
    assert manager.state == LifecycleState.STOPPED


@pytest.mark.asyncio
async def test_lifecycle_manager_health_check():
    """Test health check functionality."""
    manager = LifecycleManager()
    
    def health_check():
        return True
        
    manager.add_health_check("test_check", health_check)
    await manager.startup()
    
    health = await manager.health_check()
    assert health["status"] == "healthy"
    assert "test_check" in health["checks"]
    assert health["checks"]["test_check"]["status"] == "healthy"
    
    await manager.shutdown()


@pytest.mark.asyncio
async def test_lifecycle_manager_health_check_failure():
    """Test health check with failure."""
    manager = LifecycleManager()
    
    def failing_check():
        return False
        
    manager.add_health_check("failing_check", failing_check)
    await manager.startup()
    
    health = await manager.health_check()
    assert health["status"] == "degraded"
    assert health["checks"]["failing_check"]["status"] == "unhealthy"
    
    await manager.shutdown()


@pytest.mark.asyncio
async def test_lifecycle_manager_async_handlers():
    """Test async startup and shutdown handlers."""
    manager = LifecycleManager()
    startup_called = False
    shutdown_called = False
    
    async def async_startup():
        nonlocal startup_called
        await asyncio.sleep(0.01)
        startup_called = True
        
    async def async_shutdown():
        nonlocal shutdown_called
        await asyncio.sleep(0.01)
        shutdown_called = True
        
    manager.add_startup_handler(async_startup)
    manager.add_shutdown_handler(async_shutdown)
    
    await manager.startup()
    assert startup_called
    
    await manager.shutdown()
    assert shutdown_called


@pytest.mark.asyncio
async def test_lifecycle_manager_uptime():
    """Test uptime tracking."""
    manager = LifecycleManager()
    
    assert manager.uptime_seconds is None
    
    await manager.startup()
    await asyncio.sleep(0.1)
    
    uptime = manager.uptime_seconds
    assert uptime is not None
    assert uptime >= 0.1
    
    await manager.shutdown()
