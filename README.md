# tbcoin-engine-ml

Backend engine for TBCoin with ML capabilities and comprehensive lifecycle management.

## Features

- **Comprehensive Lifecycle Management**: Full application, model, and resource lifecycle management
- **ML Model Management**: Dynamic model loading, versioning, and hot-swapping
- **Resource Management**: Automatic initialization and cleanup of resources
- **Health Monitoring**: Built-in health checks and monitoring
- **Graceful Shutdown**: Proper cleanup of all resources on shutdown

## Documentation

- [Lifecycle Management Guide](LIFECYCLE.md) - Comprehensive guide to the lifecycle management system

## Quick Start

```python
import asyncio
from lifecycle import LifecycleManager

async def main():
    manager = LifecycleManager(app_name="tbcoin-engine")
    await manager.startup()
    # Your application logic here
    await manager.shutdown()

asyncio.run(main())
```

See [example_usage.py](example_usage.py) for a complete example.

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
pytest tests/ -v
```

## License

MIT License - see LICENSE file for details.
