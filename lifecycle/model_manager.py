"""
ML Model Lifecycle Manager

Manages the lifecycle of machine learning models including loading,
versioning, hot-swapping, and cleanup.
"""

import asyncio
import logging
from typing import Dict, Optional, Any, Callable
from datetime import datetime
from pathlib import Path

from .states import LifecycleState


logger = logging.getLogger(__name__)


class ModelMetadata:
    """Metadata for a loaded ML model."""
    
    def __init__(self, name: str, version: str, path: Optional[Path] = None):
        self.name = name
        self.version = version
        self.path = path
        self.loaded_at = datetime.now()
        self.last_used = datetime.now()
        self.usage_count = 0
        self.state = LifecycleState.UNINITIALIZED
        
    def update_usage(self):
        """Update usage statistics."""
        self.last_used = datetime.now()
        self.usage_count += 1


class ModelLifecycleManager:
    """
    Manages the lifecycle of ML models in the TBCoin Engine.
    
    Features:
    - Model loading and unloading
    - Version management
    - Hot-swapping models without downtime
    - Automatic cleanup of unused models
    - Model health monitoring
    """
    
    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or Path("./models")
        self.models: Dict[str, Any] = {}
        self.metadata: Dict[str, ModelMetadata] = {}
        self.model_loaders: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()
        
    def register_model_loader(self, model_type: str, loader: Callable):
        """Register a loader function for a specific model type."""
        self.model_loaders[model_type] = loader
        logger.info(f"Registered loader for model type: {model_type}")
        
    async def load_model(
        self,
        name: str,
        version: str,
        model_type: str,
        path: Optional[Path] = None,
        config: Optional[Dict] = None
    ) -> Any:
        """
        Load a model into memory.
        
        Args:
            name: Model identifier
            version: Model version
            model_type: Type of model (must have registered loader)
            path: Optional path to model file
            config: Optional configuration for the model
            
        Returns:
            Loaded model object
        """
        async with self._lock:
            model_key = f"{name}:{version}"
            
            if model_key in self.models:
                logger.info(f"Model {model_key} already loaded")
                self.metadata[model_key].update_usage()
                return self.models[model_key]
                
            logger.info(f"Loading model {model_key}...")
            
            # Get the appropriate loader
            if model_type not in self.model_loaders:
                raise ValueError(f"No loader registered for model type: {model_type}")
                
            loader = self.model_loaders[model_type]
            
            # Create metadata
            metadata = ModelMetadata(name, version, path)
            metadata.state = LifecycleState.INITIALIZING
            self.metadata[model_key] = metadata
            
            try:
                # Load the model
                model_path = path or (self.model_dir / name / version)
                if asyncio.iscoroutinefunction(loader):
                    model = await loader(model_path, config)
                else:
                    model = loader(model_path, config)
                    
                self.models[model_key] = model
                metadata.state = LifecycleState.READY
                metadata.update_usage()
                
                logger.info(f"Model {model_key} loaded successfully")
                return model
                
            except Exception as e:
                metadata.state = LifecycleState.ERROR
                logger.error(f"Failed to load model {model_key}: {e}", exc_info=True)
                raise
                
    async def unload_model(self, name: str, version: str):
        """
        Unload a model from memory.
        
        Args:
            name: Model identifier
            version: Model version
        """
        async with self._lock:
            model_key = f"{name}:{version}"
            
            if model_key not in self.models:
                logger.warning(f"Model {model_key} not loaded")
                return
                
            logger.info(f"Unloading model {model_key}...")
            
            try:
                # Remove model and metadata
                metadata = self.metadata[model_key]
                metadata.state = LifecycleState.STOPPED
                del self.models[model_key]
                
                logger.info(
                    f"Model {model_key} unloaded. "
                    f"Total uses: {metadata.usage_count}"
                )
                
            except Exception as e:
                logger.error(f"Error unloading model {model_key}: {e}", exc_info=True)
                raise
                
    async def hot_swap_model(
        self,
        name: str,
        old_version: str,
        new_version: str,
        model_type: str,
        path: Optional[Path] = None,
        config: Optional[Dict] = None
    ):
        """
        Hot-swap a model by loading a new version and unloading the old one.
        
        Args:
            name: Model identifier
            old_version: Current version to replace
            new_version: New version to load
            model_type: Type of model
            path: Optional path to new model
            config: Optional configuration
        """
        logger.info(f"Hot-swapping model {name} from {old_version} to {new_version}")
        
        # Load new version first
        await self.load_model(name, new_version, model_type, path, config)
        
        # Unload old version
        await self.unload_model(name, old_version)
        
        logger.info(f"Hot-swap completed for model {name}")
        
    def get_model(self, name: str, version: str) -> Optional[Any]:
        """
        Get a loaded model.
        
        Args:
            name: Model identifier
            version: Model version
            
        Returns:
            Model object if loaded, None otherwise
        """
        model_key = f"{name}:{version}"
        if model_key in self.models:
            self.metadata[model_key].update_usage()
            return self.models[model_key]
        return None
        
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """
        List all loaded models with their metadata.
        
        Returns:
            Dictionary of model information
        """
        result = {}
        for key, metadata in self.metadata.items():
            result[key] = {
                "name": metadata.name,
                "version": metadata.version,
                "state": str(metadata.state),
                "loaded_at": metadata.loaded_at.isoformat(),
                "last_used": metadata.last_used.isoformat(),
                "usage_count": metadata.usage_count,
            }
        return result
        
    async def cleanup_unused_models(self, max_age_seconds: int = 3600):
        """
        Cleanup models that haven't been used recently.
        
        Args:
            max_age_seconds: Maximum age in seconds before cleanup
        """
        now = datetime.now()
        to_unload = []
        
        for key, metadata in self.metadata.items():
            age = (now - metadata.last_used).total_seconds()
            if age > max_age_seconds:
                to_unload.append((metadata.name, metadata.version))
                
        for name, version in to_unload:
            logger.info(f"Cleaning up unused model: {name}:{version}")
            await self.unload_model(name, version)
            
        if to_unload:
            logger.info(f"Cleaned up {len(to_unload)} unused models")
