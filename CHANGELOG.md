# Changelog

All notable changes to the TB Coin Engine ML project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-11-22

### Added
- **Automated Dependency Checking**: New GitHub workflow for weekly security audits and dependency reviews
  - File: `.github/workflows/dependency-check.yml`
  - Features: pip-audit integration, dependency review on PRs, scheduled weekly runs
  
- **Dependabot Configuration**: Automated dependency updates for Python, GitHub Actions, Docker, and npm
  - File: `.github/dependabot.yml`
  - Weekly updates with automatic PR creation
  
- **Pre-commit Hooks**: Development workflow improvements with automated checks
  - File: `.pre-commit-config.yaml`
  - Includes: black, isort, flake8, bandit, markdownlint, yamllint, hadolint
  - Supporting files: `.bandit`, `.yamllint.yml`
  
- **Documentation**:
  - `DEPRECATION_FIXES.md`: Complete guide to deprecated code fixes and migrations
  - `WORKFLOW_IMPROVEMENTS.md`: Comprehensive workflow recommendations and best practices
  - `CHANGELOG.md`: This file for tracking changes

### Changed
- **Updated Python Packages**:
  - `aioredis==2.0.1` → `redis[hiredis]>=5.0.0` (aioredis is deprecated)
  - `gym==0.26.2` → `gymnasium>=0.29.0` (gym is deprecated)
  - `grafana-api==1.0.4` → `grafana-client>=3.5.0` (grafana-api is outdated)
  - `torch==2.9.0` → `torch==2.5.1` (corrected to existing version)
  - `torchvision==0.24.0` → `torchvision==0.20.1` (compatible with torch 2.5.1)

- **Updated GitHub Actions**:
  - `actions/checkout@v2` → `actions/checkout@v4` in main.yml
  - `actions/setup-python@v4` → `actions/setup-python@v5` in canary-model-ci.yml
  - `ibmcloud/ibm-cloud-cli-action@v2` → `ibmcloud/ibm-cloud-cli-action@v3` in main.yml

- **Improved requirements-minimal.txt**:
  - Removed duplicate entries
  - Added proper version constraints
  - Updated Flask to `>=3.0.0`
  - Standardized pytest version to `>=7.4.0`

### Removed
- **asyncio==3.4.3**: Removed from requirements.txt (asyncio is a standard library module)

### Fixed
- Corrected non-existent package versions (torch 2.9.0, torchvision 0.24.0)
- Consolidated duplicate package specifications across requirements files
- Updated deprecated package references

### Security
- Implemented automated security scanning with pip-audit
- Added Dependabot for automatic security updates
- Included pre-commit hooks with bandit security scanner
- All deprecated packages with known vulnerabilities updated

## Migration Notes

### For Developers

If you're using any of the deprecated packages in your local development:

1. **aioredis → redis**:
   ```python
   # Old
   import aioredis
   
   # New
   import redis.asyncio as aioredis
   # or
   from redis import asyncio as redis
   ```

2. **gym → gymnasium**:
   ```python
   # Old
   import gym
   
   # New
   import gymnasium as gym
   ```

3. **grafana_api → grafana_client**:
   ```python
   # Old
   from grafana_api.grafana_face import GrafanaFace
   
   # New
   from grafana_client import GrafanaApi
   ```

### For CI/CD

- All GitHub Actions workflows have been updated to use latest versions
- New dependency-check workflow will run weekly and on PR
- Dependabot will create automated PRs for dependency updates

### Testing

After updating dependencies:
```bash
# Create fresh virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows

# Install updated requirements
pip install -r requirements-minimal.txt

# Run tests
pytest

# Optional: Install pre-commit hooks
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Compatibility

- **Python**: 3.11, 3.12 (tested)
- **OS**: Linux, macOS, Windows
- **Deployment**: Docker, IBM Code Engine, serverless platforms

## Contributors

- Automated updates and fixes by GitHub Copilot

## Links

- [Repository](https://github.com/sjhallo07/tbcoin-engine-ml)
- [Issues](https://github.com/sjhallo07/tbcoin-engine-ml/issues)
- [Pull Requests](https://github.com/sjhallo07/tbcoin-engine-ml/pulls)

---

## How to Update This Changelog

When making changes:
1. Add entries under `[Unreleased]` section
2. Use categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. Keep entries concise but descriptive
4. Include file paths for new files
5. Link to relevant issues/PRs when applicable

When releasing a new version:
1. Change `[Unreleased]` to `[Version] - Date`
2. Create new `[Unreleased]` section
3. Update version in relevant files
4. Create a git tag for the release
