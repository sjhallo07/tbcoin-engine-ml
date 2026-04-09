locals {
  common_tags = concat(var.tags, [
    "region:${var.region}",
    "stack:granite-first",
  ])
}

resource "ibm_resource_group" "this" {
  name = var.resource_group_name
}

resource "ibm_resource_instance" "cos" {
  name              = var.cos_instance_name
  service           = "cloud-object-storage"
  plan              = var.cos_plan
  location          = "global"
  resource_group_id = ibm_resource_group.this.id
  tags              = local.common_tags
}

resource "ibm_cos_bucket" "artifacts" {
  bucket_name          = var.cos_bucket_name
  resource_instance_id = ibm_resource_instance.cos.guid
  region_location      = var.bucket_region
  storage_class        = var.cos_bucket_storage_class
}

resource "ibm_resource_instance" "postgresql" {
  name              = var.postgres_instance_name
  service           = "databases-for-postgresql"
  plan              = var.postgres_plan
  location          = var.region
  resource_group_id = ibm_resource_group.this.id
  tags              = local.common_tags
}

resource "ibm_resource_instance" "redis" {
  name              = var.redis_instance_name
  service           = "databases-for-redis"
  plan              = var.redis_plan
  location          = var.region
  resource_group_id = ibm_resource_group.this.id
  tags              = local.common_tags
}

resource "ibm_code_engine_project" "this" {
  name              = var.code_engine_project_name
  resource_group_id = ibm_resource_group.this.id
}

resource "ibm_resource_instance" "watsonx_runtime" {
  count             = var.provision_watsonx_runtime ? 1 : 0
  name              = var.watsonx_runtime_name
  service           = var.watsonx_runtime_service
  plan              = var.watsonx_runtime_plan
  location          = var.region
  resource_group_id = ibm_resource_group.this.id
  tags              = local.common_tags
}

# Code Engine application and job deployment remain intentionally externalized.
# This repository already contains deployable YAML and shell flows:
#   - ibm-cloud-code-engine-api-app.yaml
#   - ibm-cloud-code-engine-ml-worker-app.yaml
#   - ibm-cloud-code-engine-blockchain-listener-job.yaml
#   - deploy-ibm-ce.sh
#
# Recommended sequence:
# 1. terraform apply   -> provision the foundation (RG, COS, DBs, CE project)
# 2. build/push images -> existing project scripts
# 3. deploy apps/jobs  -> Code Engine YAMLs or ibmcloud ce commands
