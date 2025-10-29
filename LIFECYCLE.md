# TBCoin Engine ML - Lifecycle Management

A comprehensive lifecycle management system for the TBCoin Engine backend with ML capabilities.

## Features

### 1. Application Lifecycle Management
- **Startup/Shutdown Orchestration**: Manage the complete lifecycle of your application
- **Graceful Shutdown**: Ensure all resources are properly cleaned up
- **Health Monitoring**: Built-in health checks and monitoring
- **Signal Handling**: Automatic handling of system signals (SIGTERM, SIGINT)

### 2. ML Model Lifecycle Management
- **Model Loading/Unloading**: Dynamically load and unload ML models
- **Version Management**: Support for multiple model versions
- **Hot-Swapping**: Update models without downtime
- **Automatic Cleanup**: Remove unused models to free memory
- **Usage Tracking**: Monitor model usage statistics

### 3. Resource Lifecycle Management
- **Resource Initialization**: Manage database connections, caches, and external clients
- **Health Checks**: Monitor resource health
- **Automatic Cleanup**: Proper resource cleanup on shutdown
- **Connection Pooling**: Support for resource pooling patterns

### 4. Request/Transaction Lifecycle
- **State Tracking**: Track request states throughout their lifecycle
- **Monitoring**: Built-in monitoring for all lifecycle events

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
import asyncio
from lifecycle import LifecycleManager

async def main():
    # Create lifecycle manager
    manager = LifecycleManager(app_name="my-app")
    
    # Register startup handler
    manager.add_startup_handler(lambda: print("Starting up!"))
    
    # Register shutdown handler
    manager.add_shutdown_handler(lambda: print("Shutting down!"))
    
    # Start application
    await manager.startup()
    
    # Your application logic here...
    
    # Shutdown
    await manager.shutdown()

asyncio.run(main())
```

### Model Lifecycle Management

```python
from lifecycle import ModelLifecycleManager
from pathlib import Path

# Create model manager
model_manager = ModelLifecycleManager(model_dir=Path("./models"))

# Register a model loader
def load_model(path: Path, config: dict = None):
    # Your model loading logic
    return your_ml_model

model_manager.register_model_loader("ml_model", load_model)

# Load a model
model = await model_manager.load_model(
    name="predictor",
    version="1.0.0",
    model_type="ml_model"
)

# Use the model
result = model.predict(data)

# Hot-swap to a new version
await model_manager.hot_swap_model(
    name="predictor",
    old_version="1.0.0",
    new_version="2.0.0",
    model_type="ml_model"
)
```

### Resource Management

```python
from lifecycle import ResourceLifecycleManager

# Create resource manager
resource_manager = ResourceLifecycleManager()

# Register resource type
async def init_database(config: dict = None):
    # Initialize database connection
    return db_connection

async def cleanup_database(resource):
    # Close database connection
    await resource.close()

resource_manager.register_resource_type(
    "database",
    init_database,
    cleanup_database
)

# Initialize resource
db = await resource_manager.initialize_resource(
    name="main_db",
    resource_type="database",
    config={"host": "localhost"}
)

# Use resource
result = await db.query("SELECT * FROM users")

# Cleanup when done
await resource_manager.cleanup_resource("main_db")
```

## Architecture

### Lifecycle States

The system uses well-defined states for all components:

- `UNINITIALIZED`: Component not yet initialized
- `INITIALIZING`: Component is being initialized
- `READY`: Component is ready but not actively running
- `STARTING`: Component is starting up
- `RUNNING`: Component is actively running
- `STOPPING`: Component is shutting down
- `STOPPED`: Component has stopped
- `ERROR`: Component encountered an error

### Component Overview

```
┌─────────────────────────────────────────┐
│       LifecycleManager                  │
│   (Application Lifecycle)               │
├─────────────────────────────────────────┤
│  - Startup/Shutdown orchestration       │
│  - Health checks                        │
│  - Signal handling                      │
└─────────────────────────────────────────┘
            │
            ├─────────────────┬─────────────────┐
            │                 │                 │
┌───────────▼───────┐ ┌──────▼──────┐ ┌────────▼────────┐
│ ModelLifecycle    │ │ Resource    │ │  Health         │
│ Manager           │ │ Lifecycle   │ │  Monitoring     │
│                   │ │ Manager     │ │                 │
├───────────────────┤ ├─────────────┤ ├─────────────────┤
│ - Load models     │ │ - Init      │ │ - Check health  │
│ - Version mgmt    │ │   resources │ │ - Track uptime  │
│ - Hot-swapping    │ │ - Cleanup   │ │ - Status report │
│ - Cleanup         │ │ - Health    │ │                 │
└───────────────────┘ └─────────────┘ └─────────────────┘
```

## Configuration

Configuration can be provided via the `LifecycleConfig` class:

```python
from lifecycle.config import LifecycleConfig

config = LifecycleConfig(
    app_name="tbcoin-engine",
    log_level="INFO",
    model_cleanup_interval_seconds=3600,
    graceful_shutdown_timeout_seconds=30
)
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=lifecycle --cov-report=html
```

## Example Application

See `example_usage.py` for a complete example application demonstrating:
- Application lifecycle management
- Model loading and hot-swapping
- Resource management
- Health checks
- Graceful shutdown

Run the example:

```bash
python example_usage.py
```

## Best Practices

### 1. Startup Order
Register handlers in the correct order:
```python
manager.add_startup_handler(init_config)
manager.add_startup_handler(init_database)
manager.add_startup_handler(load_models)
```

### 2. Shutdown Order
Shutdown happens in reverse order of registration automatically.

### 3. Health Checks
Add health checks for all critical components:
```python
manager.add_health_check("database", check_db_health)
manager.add_health_check("models", check_models_loaded)
```

### 4. Model Cleanup
Configure automatic cleanup to prevent memory leaks:
```python
# Cleanup models unused for more than 1 hour
await model_manager.cleanup_unused_models(max_age_seconds=3600)
```

### 5. Error Handling
Always handle errors in lifecycle handlers:
```python
async def safe_startup():
    try:
        await initialize_component()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

manager.add_startup_handler(safe_startup)
```

## API Reference

### LifecycleManager

#### Methods
- `add_startup_handler(handler: Callable)`: Register startup handler
- `add_shutdown_handler(handler: Callable)`: Register shutdown handler
- `add_health_check(name: str, check: Callable)`: Register health check
- `async startup()`: Start the application
- `async shutdown()`: Shutdown the application
- `async health_check()`: Run all health checks

#### Properties
- `state: LifecycleState`: Current application state
- `is_running: bool`: Whether application is running
- `uptime_seconds: float`: Application uptime

### ModelLifecycleManager

#### Methods
- `register_model_loader(model_type: str, loader: Callable)`: Register model loader
- `async load_model(name, version, model_type, ...)`: Load a model
- `async unload_model(name, version)`: Unload a model
- `async hot_swap_model(name, old_version, new_version, ...)`: Hot-swap models
- `get_model(name, version)`: Get loaded model
- `list_models()`: List all loaded models
- `async cleanup_unused_models(max_age_seconds)`: Cleanup old models

### ResourceLifecycleManager

#### Methods
- `register_resource_type(type, initializer, cleaner, health_checker)`: Register resource type
- `async initialize_resource(name, resource_type, config)`: Initialize resource
- `async cleanup_resource(name)`: Cleanup resource
- `get_resource(name)`: Get resource
- `async check_resource_health(name)`: Check resource health
- `async check_all_resources_health()`: Check all resources
- `list_resources()`: List all resources
- `async cleanup_all()`: Cleanup all resources

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass
2. Code follows the existing style
3. New features include tests
4. Documentation is updated

## License

This project is licensed under the MIT License - see the LICENSE file for details.
