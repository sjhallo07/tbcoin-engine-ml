"""
Example usage of the TBCoin Engine Lifecycle Management System
"""

import asyncio
import logging
from pathlib import Path

from lifecycle import (
    LifecycleManager,
    ModelLifecycleManager,
    ResourceLifecycleManager,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Example model loader
def load_dummy_model(path: Path, config: dict = None):
    """Example model loader - replace with actual ML model loading."""
    logger.info(f"Loading model from {path}")
    return {"model_data": "dummy_model", "config": config}


# Example resource initializer
async def initialize_database(config: dict = None):
    """Example database connection initializer."""
    logger.info("Initializing database connection")
    await asyncio.sleep(0.1)  # Simulate connection time
    return {"connection": "dummy_db_connection"}


# Example resource cleaner
async def cleanup_database(resource):
    """Example database cleanup."""
    logger.info("Closing database connection")
    await asyncio.sleep(0.1)  # Simulate cleanup time


# Example health check
async def check_database_health(resource):
    """Example database health check."""
    # In real scenario, this would ping the database
    return True


async def main():
    """Main application example."""
    
    # Initialize the core lifecycle manager
    lifecycle = LifecycleManager(app_name="tbcoin-engine-example")
    
    # Initialize model lifecycle manager
    model_manager = ModelLifecycleManager(model_dir=Path("./models"))
    model_manager.register_model_loader("ml_model", load_dummy_model)
    
    # Initialize resource lifecycle manager
    resource_manager = ResourceLifecycleManager()
    resource_manager.register_resource_type(
        "database",
        initialize_database,
        cleanup_database,
        check_database_health
    )
    
    # Register startup handlers
    async def startup_models():
        """Load initial models on startup."""
        logger.info("Loading initial models...")
        await model_manager.load_model(
            name="tbcoin_predictor",
            version="1.0.0",
            model_type="ml_model",
            config={"param": "value"}
        )
        
    async def startup_resources():
        """Initialize resources on startup."""
        logger.info("Initializing resources...")
        await resource_manager.initialize_resource(
            name="main_db",
            resource_type="database",
            config={"host": "localhost", "port": 5432}
        )
        
    lifecycle.add_startup_handler(startup_models)
    lifecycle.add_startup_handler(startup_resources)
    
    # Register shutdown handlers
    async def shutdown_resources():
        """Cleanup resources on shutdown."""
        await resource_manager.cleanup_all()
        
    lifecycle.add_shutdown_handler(shutdown_resources)
    
    # Register health checks
    async def check_models():
        """Check if required models are loaded."""
        models = model_manager.list_models()
        return len(models) > 0
        
    async def check_resources():
        """Check resource health."""
        health = await resource_manager.check_all_resources_health()
        return all(h.get("healthy", False) for h in health.values())
        
    lifecycle.add_health_check("models", check_models)
    lifecycle.add_health_check("resources", check_resources)
    
    try:
        # Start the application
        await lifecycle.startup()
        
        # Simulate application running
        logger.info("Application is running...")
        
        # Perform a health check
        health = await lifecycle.health_check()
        logger.info(f"Health check result: {health}")
        
        # List loaded models
        models = model_manager.list_models()
        logger.info(f"Loaded models: {models}")
        
        # List resources
        resources = resource_manager.list_resources()
        logger.info(f"Active resources: {resources}")
        
        # Demonstrate hot-swapping a model
        logger.info("Demonstrating model hot-swap...")
        await model_manager.hot_swap_model(
            name="tbcoin_predictor",
            old_version="1.0.0",
            new_version="1.1.0",
            model_type="ml_model"
        )
        
        # Simulate some work
        await asyncio.sleep(2)
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
    finally:
        # Shutdown the application
        await lifecycle.shutdown()
        
    logger.info("Application terminated")


if __name__ == "__main__":
    asyncio.run(main())
