"""
Tests for Model Lifecycle Manager
"""

import pytest
import asyncio
from pathlib import Path
from lifecycle import ModelLifecycleManager, LifecycleState


def dummy_model_loader(path: Path, config: dict = None):
    """Dummy model loader for testing."""
    return {"model": "dummy", "path": str(path), "config": config}


@pytest.mark.asyncio
async def test_model_manager_initialization():
    """Test model manager initialization."""
    manager = ModelLifecycleManager()
    assert manager.model_dir == Path("./models")
    assert len(manager.models) == 0


@pytest.mark.asyncio
async def test_model_loading():
    """Test loading a model."""
    manager = ModelLifecycleManager()
    manager.register_model_loader("dummy", dummy_model_loader)
    
    model = await manager.load_model(
        name="test_model",
        version="1.0.0",
        model_type="dummy"
    )
    
    assert model is not None
    assert "test_model:1.0.0" in manager.models
    assert manager.metadata["test_model:1.0.0"].state == LifecycleState.READY


@pytest.mark.asyncio
async def test_model_unloading():
    """Test unloading a model."""
    manager = ModelLifecycleManager()
    manager.register_model_loader("dummy", dummy_model_loader)
    
    await manager.load_model(
        name="test_model",
        version="1.0.0",
        model_type="dummy"
    )
    
    await manager.unload_model("test_model", "1.0.0")
    assert "test_model:1.0.0" not in manager.models


@pytest.mark.asyncio
async def test_model_hot_swap():
    """Test hot-swapping a model."""
    manager = ModelLifecycleManager()
    manager.register_model_loader("dummy", dummy_model_loader)
    
    # Load initial version
    await manager.load_model(
        name="test_model",
        version="1.0.0",
        model_type="dummy"
    )
    
    # Hot swap to new version
    await manager.hot_swap_model(
        name="test_model",
        old_version="1.0.0",
        new_version="2.0.0",
        model_type="dummy"
    )
    
    assert "test_model:2.0.0" in manager.models
    assert "test_model:1.0.0" not in manager.models


@pytest.mark.asyncio
async def test_model_get():
    """Test getting a loaded model."""
    manager = ModelLifecycleManager()
    manager.register_model_loader("dummy", dummy_model_loader)
    
    await manager.load_model(
        name="test_model",
        version="1.0.0",
        model_type="dummy"
    )
    
    model = manager.get_model("test_model", "1.0.0")
    assert model is not None
    
    # Check usage counter incremented
    metadata = manager.metadata["test_model:1.0.0"]
    assert metadata.usage_count == 2  # Once during load, once during get


@pytest.mark.asyncio
async def test_model_list():
    """Test listing loaded models."""
    manager = ModelLifecycleManager()
    manager.register_model_loader("dummy", dummy_model_loader)
    
    await manager.load_model(
        name="model1",
        version="1.0.0",
        model_type="dummy"
    )
    
    await manager.load_model(
        name="model2",
        version="1.0.0",
        model_type="dummy"
    )
    
    models = manager.list_models()
    assert len(models) == 2
    assert "model1:1.0.0" in models
    assert "model2:1.0.0" in models


@pytest.mark.asyncio
async def test_model_cleanup_unused():
    """Test cleaning up unused models."""
    manager = ModelLifecycleManager()
    manager.register_model_loader("dummy", dummy_model_loader)
    
    await manager.load_model(
        name="test_model",
        version="1.0.0",
        model_type="dummy"
    )
    
    # Immediately cleanup models older than 0 seconds
    await manager.cleanup_unused_models(max_age_seconds=0)
    
    # Model should be unloaded
    assert "test_model:1.0.0" not in manager.models


@pytest.mark.asyncio
async def test_model_loader_not_registered():
    """Test loading with unregistered model type."""
    manager = ModelLifecycleManager()
    
    with pytest.raises(ValueError, match="No loader registered"):
        await manager.load_model(
            name="test_model",
            version="1.0.0",
            model_type="nonexistent"
        )
