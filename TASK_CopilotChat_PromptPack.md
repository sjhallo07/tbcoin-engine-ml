# Copilot Chat – Best Prompts Pack (Editor, CI, Devcontainers, Cost Optimization)

This document provides curated prompts for GitHub Copilot Chat to help with common development tasks, CI/CD optimization, devcontainer management, and cost-effective workflows.

---

## 📝 Editor & Code Quality Prompts

### General Code Improvements
- **"Review this function for potential bugs and suggest improvements"**
- **"Refactor this code to follow Python PEP 8 style guidelines"**
- **"Add comprehensive error handling to this function"**
- **"Optimize this code for better performance"**
- **"Add type hints to this Python function"**

### Documentation
- **"Generate docstrings for this function following Google style"**
- **"Create a README section explaining how to use this module"**
- **"Add inline comments explaining the complex logic in this function"**

### Testing
- **"Generate unit tests for this function using pytest"**
- **"Create integration tests for this API endpoint"**
- **"Suggest edge cases I should test for this function"**

---

## 🔄 CI/CD Optimization Prompts

### Workflow Performance
- **"Analyze this GitHub Actions workflow and suggest ways to reduce execution time"**
- **"Help me add dependency caching to reduce CI minutes"**
- **"Optimize this workflow to minimize GitHub Actions billable minutes"**
- **"Suggest concurrency settings to prevent duplicate workflow runs"**

### Cost Efficiency
- **"Review this CI workflow and identify opportunities to reduce costs"**
- **"Help me set up path filters to skip unnecessary workflow runs"**
- **"Suggest timeout values to prevent runaway jobs"**
- **"Show me how to use conditional job execution to save CI minutes"**

### Build & Test Optimization
- **"Help me parallelize these tests to reduce CI time"**
- **"Suggest ways to split this monolithic CI job into faster parallel jobs"**
- **"Optimize pip install steps with proper caching"**
- **"Help me implement fail-fast strategy for test jobs"**

---

## 🐳 Devcontainer Prompts

### Setup & Configuration
- **"Create a minimal devcontainer.json for Python 3.11 development"**
- **"Add VS Code extensions for Python development to my devcontainer"**
- **"Configure devcontainer post-create commands to install dependencies"**
- **"Set up devcontainer settings for auto-save and format-on-save"**

### Optimization
- **"Optimize this devcontainer for faster startup time"**
- **"Suggest a lighter base image for my Python devcontainer"**
- **"Help me reduce devcontainer rebuild time"**
- **"Configure devcontainer to use local pip cache"**

### Features & Tools
- **"Add Docker-in-Docker support to my devcontainer"**
- **"Configure multiple Python versions in my devcontainer"**
- **"Set up port forwarding for my FastAPI app in devcontainer"**
- **"Add git configuration to my devcontainer"**

---

## 💰 Cost Optimization Prompts

### GitHub Actions Minutes
- **"Audit my workflows and calculate estimated monthly Actions minutes usage"**
- **"Help me migrate long-running jobs to self-hosted runners"**
- **"Suggest strategies to stay within free tier limits for Actions"**
- **"Identify redundant workflow triggers that waste CI minutes"**

### Codespaces Optimization
- **"Configure prebuilds to reduce Codespaces startup time"**
- **"Help me set up lifecycle scripts to minimize Codespaces compute hours"**
- **"Suggest devcontainer settings to reduce Codespaces memory usage"**
- **"Configure auto-stop for Codespaces to prevent idle charges"**

### Resource Management
- **"Review my project dependencies and suggest lighter alternatives"**
- **"Help me implement conditional dependency installation in CI"**
- **"Optimize Docker image layers to reduce build time and storage"**
- **"Suggest ways to reduce repository artifact storage costs"**

---

## 🔍 Debugging & Troubleshooting Prompts

### CI/CD Issues
- **"This GitHub Actions job is failing, help me debug it"**
- **"Explain why this workflow was skipped"**
- **"Help me fix this timeout issue in my CI pipeline"**
- **"Debug this caching issue causing slow builds"**

### Devcontainer Issues
- **"My devcontainer is failing to build, help me troubleshoot"**
- **"Extensions are not loading in my devcontainer, what's wrong?"**
- **"Help me fix this permission error in devcontainer"**
- **"Debug why post-create commands are not running"**

### Performance Issues
- **"Profile this function and suggest performance improvements"**
- **"Help me identify the bottleneck in this code"**
- **"Analyze memory usage in this Python script"**
- **"Suggest ways to optimize this database query"**

---

## 🛡️ Security & Best Practices Prompts

### Security Review
- **"Review this code for security vulnerabilities"**
- **"Check if this code properly sanitizes user input"**
- **"Identify potential SQL injection risks in this function"**
- **"Review error handling to ensure secrets are not leaked in logs"**

### Best Practices
- **"Review this code against Python best practices"**
- **"Suggest improvements for code maintainability"**
- **"Help me apply SOLID principles to this class"**
- **"Review this API design for RESTful best practices"**

---

## 🎯 Project-Specific Prompts (tbcoin-engine-ml)

### ML/AI Specific
- **"Optimize this model training pipeline for faster convergence"**
- **"Review this ML model for potential bias"**
- **"Suggest ways to reduce inference latency"**
- **"Help me implement model versioning with MLflow"**

### Blockchain Integration
- **"Review this Solana integration for best practices"**
- **"Help me optimize blockchain transaction gas costs"**
- **"Suggest error handling for blockchain connection failures"**
- **"Review this Web3 interaction for security issues"**

### API Development
- **"Optimize this FastAPI endpoint for better performance"**
- **"Add proper input validation to this API endpoint"**
- **"Help me implement rate limiting for this API"**
- **"Review this async function for proper error handling"**

---

## 💡 Tips for Using These Prompts

1. **Be Specific**: Add context about your specific code or issue when using these prompts
2. **Iterate**: Start with a general prompt, then follow up with more specific questions
3. **Provide Context**: Share relevant code snippets or error messages with your prompts
4. **Combine Prompts**: Use multiple prompts in sequence for comprehensive assistance
5. **Validate Suggestions**: Always review and test Copilot's suggestions before applying them

---

## 🚀 Quick Start Examples

### For New Features
1. "Help me design the API for [feature name]"
2. "Generate the implementation for [feature name]"
3. "Create tests for [feature name]"
4. "Document [feature name] in the README"

### For Bug Fixes
1. "Analyze this error: [error message]"
2. "Suggest root cause for this bug"
3. "Help me fix this issue while maintaining backward compatibility"
4. "Add tests to prevent this bug from recurring"

### For Optimization
1. "Profile this code and identify bottlenecks"
2. "Suggest optimization strategies"
3. "Implement the optimization"
4. "Benchmark before and after to verify improvement"

---

## 📚 Additional Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/best-practices-for-github-actions)
- [Development Containers Specification](https://containers.dev/)
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html)

---

**Last Updated**: January 2026  
**Maintained by**: @sjhallo07  
**Purpose**: Optimize development workflow, reduce costs, and maintain code quality in tbcoin-engine-ml project
