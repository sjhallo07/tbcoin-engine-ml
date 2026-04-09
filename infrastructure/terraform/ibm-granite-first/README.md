# IBM Granite-First Terraform Stack

This Terraform scaffold provisions the **foundation layer** for the Granite-first target architecture described in `docs/ibm_granite_first_proposal.md`.

## What it provisions

- IBM Cloud **resource group**
- IBM Cloud Object Storage **instance**
- COS **bucket** for artifacts, prompts, datasets, and model bundles
- **Databases for PostgreSQL** instance
- **Databases for Redis** instance
- **Code Engine project** for the application tier
- optional **watsonx.ai runtime/service instance** toggle

## Why the Code Engine apps are not fully in Terraform here

This repository already includes deployment assets for the workload layer:

- `deploy-ibm-ce.sh`
- `ibm-cloud-code-engine-api-app.yaml`
- `ibm-cloud-code-engine-ml-worker-app.yaml`
- `ibm-cloud-code-engine-blockchain-listener-job.yaml`

So this Terraform stack focuses on **stable shared infrastructure**, while the existing repo assets continue to manage the application rollout.

That split keeps the infrastructure modular and matches the repo’s current deployment model.

## Suggested flow

1. Install Terraform locally.
2. Copy `terraform.tfvars.example` to `terraform.tfvars`.
3. Replace placeholders with your IBM Cloud values.
4. Run:

```bash
terraform init
terraform plan
terraform apply
```

5. Build and push application images using the repo’s existing scripts.
6. Deploy the runtime workloads to Code Engine.

## Variables you will most likely customize

- `ibmcloud_api_key`
- `region`
- `resource_group_name`
- `cos_bucket_name`
- `postgres_instance_name`
- `redis_instance_name`
- `code_engine_project_name`
- `provision_watsonx_runtime`

## Notes for watsonx.ai

The Terraform in this folder can provision an optional watsonx-related service instance entry point, but the **AI service logic, Granite prompts, and runtime invocation flow** remain application concerns and should be deployed together with the Python services described in the proposal document.

## Notes for low-cost / PoC usage

For a cheaper first pass:

- keep `provision_watsonx_runtime = false` unless you are ready to bind it
- use a single artifacts bucket in COS
- provision PostgreSQL first
- add Redis only if coordination/caching load requires it
- reuse the existing Code Engine YAMLs and scripts for the app tier
