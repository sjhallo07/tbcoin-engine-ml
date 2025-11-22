# Deprecation Fixes and Updates

This document outlines all deprecated code, requirements, and workflow changes made to modernize the TB Coin Engine ML project.

## Date: 2025-11-22

## Python Package Updates

### 1. Removed `asyncio` Package
- **Issue**: `asyncio==3.4.3` was listed in requirements.txt
- **Fix**: Removed - `asyncio` is a standard library module in Python 3.4+ and should not be installed via pip
- **Impact**: No code changes needed, asyncio imports will work directly from standard library

### 2. Updated `aioredis` to `redis`
- **Issue**: `aioredis==2.0.1` is deprecated
- **Old**: `aioredis==2.0.1`
- **New**: `redis[hiredis]>=5.0.0`
- **Reason**: aioredis has been merged into redis-py 5.0+. The redis package now includes async support natively
- **Migration Guide**: 
  - Change imports from `import aioredis` to `import redis.asyncio as aioredis`
  - Or use `from redis import asyncio as redis`
  - The API is mostly compatible but check redis-py documentation for breaking changes

### 3. Updated `gym` to `gymnasium`
- **Issue**: `gym==0.26.2` is deprecated
- **Old**: `gym==0.26.2`
- **New**: `gymnasium>=0.29.0`
- **Reason**: OpenAI Gym has been officially deprecated in favor of Gymnasium (maintained by Farama Foundation)
- **Migration Guide**:
  - Change imports from `import gym` to `import gymnasium as gym`
  - Most APIs remain compatible, but check Gymnasium documentation for environment updates
  - Update any custom environments to use Gymnasium's API

### 4. Updated `grafana-api` to `grafana-client`
- **Issue**: `grafana-api==1.0.4` is outdated and unmaintained
- **Old**: `grafana-api==1.0.4`
- **New**: `grafana-client>=3.5.0`
- **Reason**: grafana-client is actively maintained and provides better API coverage
- **Migration Guide**:
  - Update imports from `grafana_api` to `grafana_client`
  - Review API differences in grafana-client documentation

### 5. Corrected PyTorch Versions
- **Issue**: `torch==2.9.0` and `torchvision==0.24.0` do not exist
- **Old**: `torch==2.9.0`, `torchvision==0.24.0`
- **New**: `torch==2.5.1`, `torchvision==0.20.1`
- **Reason**: Versions were incorrectly specified. PyTorch 2.5.1 is the latest stable version
- **Impact**: These are valid, compatible versions for Python 3.12

## GitHub Actions Updates

### 1. Updated `actions/checkout`
- **Old**: `actions/checkout@v2` (in main.yml)
- **New**: `actions/checkout@v4`
- **Reason**: v2 is deprecated, v4 includes security updates and performance improvements

### 2. Updated `actions/setup-python`
- **Old**: `actions/setup-python@v4` (in canary-model-ci.yml)
- **New**: `actions/setup-python@v5`
- **Reason**: v5 includes better caching support and newer Python version support

### 3. Updated `ibmcloud/ibm-cloud-cli-action`
- **Old**: `ibmcloud/ibm-cloud-cli-action@v2` (in main.yml)
- **New**: `ibmcloud/ibm-cloud-cli-action@v3`
- **Reason**: v3 includes updated CLI tools and security patches

## New Workflows Added

### Dependency Check Workflow
- **File**: `.github/workflows/dependency-check.yml`
- **Purpose**: Automatically check for outdated packages and security vulnerabilities
- **Features**:
  - Weekly scheduled runs
  - Security audits using `pip-audit`
  - Dependency review on pull requests
  - Checks all requirements files

## Requirements File Improvements

### requirements-minimal.txt
- Removed duplicate entries
- Added version constraints for all packages
- Updated Flask to `>=3.0.0` for security improvements
- Consolidated pytest version to `>=7.4.0`

## Compatibility Notes

### Python Version
- Current: Python 3.12.3
- All updated packages are compatible with Python 3.12

### Breaking Changes to Watch
1. **redis-py 5.0+**: If using aioredis in code, import paths need updating
2. **Gymnasium**: If using gym environments, import statements need updating
3. **grafana-client**: API may differ from grafana-api, review usage

## Testing Recommendations

After applying these changes, test the following:
1. Install updated requirements in a fresh virtual environment
2. Run all existing tests
3. Check for import errors related to renamed packages
4. Verify async Redis operations if used
5. Test any Gym/Gymnasium environments if implemented
6. Verify Grafana integrations if used

## Migration Script Suggestions

If you have code using the deprecated packages, consider these changes:

### For aioredis → redis
```python
# Old
import aioredis
redis = await aioredis.create_redis_pool('redis://localhost')

# New
import redis.asyncio as aioredis
redis = aioredis.Redis.from_url('redis://localhost')
```

### For gym → gymnasium
```python
# Old
import gym
env = gym.make('CartPole-v1')

# New
import gymnasium as gym
env = gym.make('CartPole-v1')
```

## Next Steps

1. ✅ Update requirements files
2. ✅ Update GitHub Actions workflows
3. ✅ Add automated dependency checking
4. 🔲 Review and update code for renamed imports (if applicable)
5. 🔲 Test all workflows
6. 🔲 Update documentation references to old package names

## References

- [redis-py GitHub](https://github.com/redis/redis-py)
- [Gymnasium Documentation](https://gymnasium.farama.org/)
- [PyTorch Release Notes](https://pytorch.org/docs/stable/notes/introduction.html)
- [GitHub Actions Version Updates](https://github.com/actions)
