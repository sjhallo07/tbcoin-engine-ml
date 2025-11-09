applyTo: '*TB COIN ENGINE ML*'
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.   
# IBM Free Tier Non-Cost Deployment Instructions     

This deployment leverages IBM Cloud's scalable, orchestrated environment to support both supervised and unsupervised machine learning workflows. The system collects, cleans, and processes data in managed databases, enabling iterative ML cycles for analysis and order execution. Logs are continuously reviewed, with iteration and control possible via log commands and API endpoints.

The architecture separates concerns:
- **Node.js/Express backend**: Handles smart contract and blockchain interactions, exposes endpoints for orchestration and control.
- **Python backend**: Dedicated to ML and LLM tasks, ensuring robust AI/ML processing.

Dependencies are organized for compatibility between Python and Node.js, enabling seamless integration between blockchain operations and advanced ML/AI features.

<!-- Add useful information to your short description that explains what the product is, why a user wants to install and use it, and any additional details the user needs to get started. The following information is an example. Make sure you update this section accordingly. -->


# TB COIN ENGINE ML — IBM Cloud Free Tier Deployment

TB COIN ENGINE ML is an AI-powered backend platform for cryptocurrency operations, combining blockchain integration, autonomous trading agents, and advanced machine learning (ML) for intelligent coin management, transaction processing, and automated decision-making. It features:

- **FastAPI-based API** for coin management, staking, minting, burning, and secure transaction processing
- **Autonomous AI/ML agent** for continuous market analysis, recommendations, and controlled trading
- **ML/LLM integration** (e.g., OpenAI GPT-4) for smart recommendations, fraud detection, and trend prediction
- **Modular architecture** supporting local, Docker, serverless, and cloud-native (Kubernetes/IBM Code Engine) deployments

Deploying on IBM Cloud Free Tier allows you to run the full backend (API, ML worker, blockchain listener) at zero cost for development and experimentation, leveraging IBM Code Engine, Container Registry, and managed databases within free tier limits.

This guide provides step-by-step instructions for a cost-free, production-ready deployment on IBM Cloud, including prerequisites, resource requirements, installation, and management.

In IBM Cloud, you can configure your installation from the Create tab, and then install it with a single click instead of executing the Helm installation directly. Your Helm Chart is installed by using IBM Cloud Schematics, and after the installation is complete, you can view the chart instance, update the version, or uninstall from your Schematics workspace.

## Before you begin

### SDLC Agile Lifecycle Management Requirements (IBM)

To ensure robust, maintainable, and collaborative deployments, follow IBM's SDLC Agile Lifecycle Management best practices:

- Use IBM Cloud Continuous Delivery toolchains for CI/CD automation (pipelines, Git integration, issue tracking)
- Manage work with IBM Engineering Workflow Management (EWM) or GitHub Projects for agile boards, sprints, and backlog
- Apply version control (Git) for all code, configuration, and infrastructure-as-code assets
- Enforce code reviews, automated testing, and security scans in the pipeline
- Document user stories, acceptance criteria, and deployment runbooks
- Track deployments, rollbacks, and changes using pipeline logs and audit trails
- Foster collaboration with regular standups, sprint reviews, and retrospectives

These practices help ensure traceability, quality, and rapid iteration throughout the software delivery lifecycle on IBM Cloud.



Before deploying TB COIN ENGINE ML on IBM Cloud Free Tier, ensure you have:

* An [IBM Cloud account](https://cloud.ibm.com/registration) (free tier is sufficient)
* IBM Cloud CLI installed: [Install instructions](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli)
* IBM Cloud Code Engine CLI plugin: `ibmcloud plugin install code-engine`
* Docker installed locally (for building and pushing images)
* Permissions: You must have **administrator** and **manager** roles for Code Engine and Container Registry services in your IBM Cloud account
* (Optional) jq and bash for running deployment scripts

No Kubernetes or Helm setup is required—IBM Code Engine abstracts away cluster management for you.

## Security and compliance controlsÂ 

## Security, Compliance, and Support

### Security Features
- JWT-based authentication for API endpoints
- Password hashing and secure secret management
- Transaction validation, fraud detection, and risk assessment using ML
- Environment variables and secrets managed via IBM Cloud Code Engine

### Compliance Controls
| Profile | ID |
|---------|----|
| NIST | SC-7(3) |
| GDPR | Data minimization, user consent |
| SOC 2 | Security, availability (cloud infra) |

### Support
- For issues, open a GitHub issue in the repository
- For IBM Cloud platform support, use [IBM Cloud Support](https://cloud.ibm.com/unifiedsupport/supportcenter)
- For documentation and updates, see the main project README and docs

#### IBM Profile Contact Information
- **Name:** Marcos Mora
- **User ID:** abreu760@hotmail.com
- **Email:** abreu760@hotmail.com
- **Language:** English

## Required resources





To run TB COIN ENGINE ML on IBM Cloud Free Tier, you need:

* **Containerization & Orchestration:**
  - Docker containers for all services
  - Kubernetes (managed by IBM Code Engine, no manual cluster setup required)
* **IBM Code Engine:**
  - For running API, ML worker, blockchain listener, and scalable workloads
* **Data Analysis & AI:**
  - Integration with IBM Watson AI services for advanced data analysis and machine learning (optional, enhances AI/ML capabilities)
* **IBM Cloud Container Registry** (for storing Docker images):
  - Up to 0.5 GB storage (free tier)
* **IBM Cloud Databases for PostgreSQL** (optional, for persistent storage):
  - Smallest instance (see cost script for free/low-cost options)
* **IBM Cloud Databases for Redis** (optional, for caching):
  - Smallest instance (see cost script for free/low-cost options)
* **Basic logging and monitoring** (included in free tier)

* **IBM Code Engine** (for API, ML worker, and blockchain listener):
  - API: 0.25 vCPU, 0.5 GB RAM (min 1, max 3 instances)
  - ML Worker: 0.5 vCPU, 1 GB RAM (min 1, max 2 instances)
  - Blockchain Listener Job: 0.25 vCPU, 0.5 GB RAM
* **IBM Cloud Container Registry** (for storing Docker images):
  - Up to 0.5 GB storage (free tier)
* **IBM Cloud Databases for PostgreSQL** (optional, for persistent storage):
  - Smallest instance (see cost script for free/low-cost options)
* **IBM Cloud Databases for Redis** (optional, for caching):
  - Smallest instance (see cost script for free/low-cost options)
* **Basic logging and monitoring** (included in free tier)

All of the above fit within IBM Cloud Free Tier limits for development and testing. For production, review IBM Cloud quotas and consider scaling resources as needed.

## Installing the software



### Step-by-Step IBM Cloud Free Tier Deployment

1. **Clone the repository and set up environment:**
  ```bash
  git clone https://github.com/sjhallo07/tbcoin-engine-ml.git
  cd tbcoin-engine-ml
  cp .env.example .env
  # Edit .env with your secrets and config (see README)
  ```

2. **Log in to IBM Cloud and set target region:**
  ```bash
  ibmcloud login
  ibmcloud target -r us-south
  ```

3. **Install Code Engine plugin and create project:**
  ```bash
  ibmcloud plugin install code-engine
  ibmcloud ce project create --name tbcoin-project
  ibmcloud ce project select --name tbcoin-project
  ```

4. **Build and push Docker images:**
  ```bash
  ./deploy-ibm-ce.sh
  # This script builds, pushes, and deploys all components (API, ML worker, listener)
  ```

5. **Set up secrets and environment variables:**
  - The deployment script will prompt or use `setup-secrets.sh` to create IBM Cloud secrets for DB, Redis, API keys, etc.

6. **Verify deployment:**
  ```bash
  ibmcloud ce app list
  ibmcloud ce job list
  ibmcloud ce jobrun list
  # Get API URL:
  ibmcloud ce app get --name tbcoin-api -o json | jq -r '.status.url'
  ```

7. **Access the API:**
  - Visit the API URL from the previous step
  - API docs: `<API_URL>/docs`
  - Health check: `<API_URL>/health`

All steps above are designed to fit within IBM Cloud Free Tier limits. For advanced configuration, see the provided YAML files and scripts.

<!-- Add additional H3 level headings as needed for sections that apply to IBM Cloud such as network policy, persistence, cluster topologies, etc.
### H3
### H3
-->

## Upgrading to a new version


When a new version of a Helm Chart is available, you're alerted in your Schematics workspace. To upgrade to a new version, complete the following steps:

1. Go to the **Menu** > **Schematics**.
2. Select your workspace name. 
3. Click **Settings**. In the Summary section, your version number is displayed. 
4. Click **Update**.
5. Select a version, and click **Update**.

#### Production Configuration

- For production, set `APP_ENV=production` and `DEBUG=False` in your environment variables or IBM Cloud secrets.
- Use strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`.
- Scale resources by adjusting min/max instances and CPU/memory in Code Engine app settings or YAMLs.
- Configure custom domains and HTTPS via IBM Cloud Code Engine settings if needed.
- For persistent storage, provision IBM Cloud Databases for PostgreSQL and Redis, and update secrets accordingly.

#### Upgrading to a New Version

To upgrade to a new version:
1. Update your codebase and Docker images.
2. Re-run the deployment script (`./deploy-ibm-ce.sh`) to build, push, and redeploy the latest images.
3. Alternatively, update the image tag in Code Engine via CLI or UI and redeploy the app.

#### Uninstalling the Software

To remove all deployed resources:
1. Delete Code Engine apps and jobs:
  ```bash
  ibmcloud ce app delete --name tbcoin-api
  ibmcloud ce app delete --name tbcoin-ml-worker
  ibmcloud ce job delete --name tbcoin-blockchain-listener
  ```
2. Delete the Code Engine project (optional):
  ```bash
  ibmcloud ce project delete --name tbcoin-project
  ```
3. Remove any associated secrets and registry images if desired.

## Uninstalling the software

<!-- Information about how a user can uninstall this product. The following information is an example. Make sure you update this section accordingly. -->

Complete the following steps to uninstall a Helm Chart from your account. 

1. Go to the **Menu** > **Schematics**.
2. Select your workspace name. 
3. Click **Actions** > **Destroy resources**. All resources in your workspace are deleted.
4. Click **Update**.
5. To delete your workspace, click **Actions** > **Delete workspace**.
