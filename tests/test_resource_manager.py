"""
Tests for Resource Lifecycle Manager
"""

import pytest
import asyncio
from lifecycle import ResourceLifecycleManager, LifecycleState


def dummy_initializer(config: dict = None):
    """Dummy resource initializer."""
    return {"resource": "dummy", "config": config}


def dummy_cleaner(resource):
    """Dummy resource cleaner."""
    pass


def dummy_health_checker(resource):
    """Dummy health checker."""
    return True


@pytest.mark.asyncio
async def test_resource_manager_initialization():
    """Test resource manager initialization."""
    manager = ResourceLifecycleManager()
    assert len(manager.resources) == 0


@pytest.mark.asyncio
async def test_resource_type_registration():
    """Test registering a resource type."""
    manager = ResourceLifecycleManager()
    manager.register_resource_type(
        "dummy",
        dummy_initializer,
        dummy_cleaner,
        dummy_health_checker
    )
    
    assert "dummy" in manager.initializers
    assert "dummy" in manager.cleaners
    assert "dummy" in manager.health_checkers


@pytest.mark.asyncio
async def test_resource_initialization():
    """Test initializing a resource."""
    manager = ResourceLifecycleManager()
    manager.register_resource_type("dummy", dummy_initializer)
    
    resource = await manager.initialize_resource(
        name="test_resource",
        resource_type="dummy",
        config={"key": "value"}
    )
    
    assert resource is not None
    assert "test_resource" in manager.resources
    assert manager.resource_info["test_resource"].state == LifecycleState.READY


@pytest.mark.asyncio
async def test_resource_cleanup():
    """Test cleaning up a resource."""
    manager = ResourceLifecycleManager()
    manager.register_resource_type("dummy", dummy_initializer, dummy_cleaner)
    
    await manager.initialize_resource(
        name="test_resource",
        resource_type="dummy"
    )
    
    await manager.cleanup_resource("test_resource")
    assert "test_resource" not in manager.resources


@pytest.mark.asyncio
async def test_resource_get():
    """Test getting a resource."""
    manager = ResourceLifecycleManager()
    manager.register_resource_type("dummy", dummy_initializer)
    
    await manager.initialize_resource(
        name="test_resource",
        resource_type="dummy"
    )
    
    resource = manager.get_resource("test_resource")
    assert resource is not None


@pytest.mark.asyncio
async def test_resource_health_check():
    """Test checking resource health."""
    manager = ResourceLifecycleManager()
    manager.register_resource_type(
        "dummy",
        dummy_initializer,
        health_checker=dummy_health_checker
    )
    
    await manager.initialize_resource(
        name="test_resource",
        resource_type="dummy"
    )
    
    health = await manager.check_resource_health("test_resource")
    assert health["status"] == "checked"
    assert health["healthy"] is True


@pytest.mark.asyncio
async def test_resource_health_check_all():
    """Test checking all resources health."""
    manager = ResourceLifecycleManager()
    manager.register_resource_type(
        "dummy",
        dummy_initializer,
        health_checker=dummy_health_checker
    )
    
    await manager.initialize_resource(
        name="resource1",
        resource_type="dummy"
    )
    
    await manager.initialize_resource(
        name="resource2",
        resource_type="dummy"
    )
    
    health = await manager.check_all_resources_health()
    assert len(health) == 2
    assert all(h["healthy"] for h in health.values())


@pytest.mark.asyncio
async def test_resource_list():
    """Test listing resources."""
    manager = ResourceLifecycleManager()
    manager.register_resource_type("dummy", dummy_initializer)
    
    await manager.initialize_resource(
        name="resource1",
        resource_type="dummy"
    )
    
    await manager.initialize_resource(
        name="resource2",
        resource_type="dummy"
    )
    
    resources = manager.list_resources()
    assert len(resources) == 2
    assert "resource1" in resources
    assert "resource2" in resources


@pytest.mark.asyncio
async def test_resource_cleanup_all():
    """Test cleaning up all resources."""
    manager = ResourceLifecycleManager()
    manager.register_resource_type("dummy", dummy_initializer, dummy_cleaner)
    
    await manager.initialize_resource(
        name="resource1",
        resource_type="dummy"
    )
    
    await manager.initialize_resource(
        name="resource2",
        resource_type="dummy"
    )
    
    await manager.cleanup_all()
    assert len(manager.resources) == 0


@pytest.mark.asyncio
async def test_resource_unknown_type():
    """Test initializing with unknown resource type."""
    manager = ResourceLifecycleManager()
    
    with pytest.raises(ValueError, match="Unknown resource type"):
        await manager.initialize_resource(
            name="test_resource",
            resource_type="nonexistent"
        )
