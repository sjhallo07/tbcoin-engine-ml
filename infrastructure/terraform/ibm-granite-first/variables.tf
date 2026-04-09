variable "ibmcloud_api_key" {
  description = "IBM Cloud API key used by the Terraform provider."
  type        = string
  sensitive   = true
}

variable "region" {
  description = "Primary IBM Cloud region for regional services."
  type        = string
  default     = "us-south"
}

variable "resource_group_name" {
  description = "Resource group that will hold the Granite-first stack."
  type        = string
  default     = "tbcoin-granite-rg"
}

variable "prefix" {
  description = "Naming prefix for all IBM Cloud resources."
  type        = string
  default     = "tbcoin"
}

variable "tags" {
  description = "Tags applied to supported IBM resources."
  type        = list(string)
  default     = ["tbcoin", "granite-first", "watsonx", "code-engine"]
}

variable "cos_instance_name" {
  description = "Cloud Object Storage instance name."
  type        = string
  default     = "tbcoin-cos"
}

variable "cos_plan" {
  description = "Cloud Object Storage plan."
  type        = string
  default     = "standard"
}

variable "cos_bucket_name" {
  description = "Bucket used for artifacts, prompts, datasets, and model bundles."
  type        = string
  default     = "tbcoin-granite-artifacts"
}

variable "bucket_region" {
  description = "Bucket region for IBM Cloud Object Storage."
  type        = string
  default     = "us-south"
}

variable "cos_bucket_storage_class" {
  description = "Storage class for the artifacts bucket."
  type        = string
  default     = "smart"
}

variable "postgres_instance_name" {
  description = "Managed PostgreSQL instance name."
  type        = string
  default     = "tbcoin-postgresql"
}

variable "postgres_plan" {
  description = "Plan for IBM Databases for PostgreSQL."
  type        = string
  default     = "standard"
}

variable "redis_instance_name" {
  description = "Managed Redis instance name."
  type        = string
  default     = "tbcoin-redis"
}

variable "redis_plan" {
  description = "Plan for IBM Databases for Redis."
  type        = string
  default     = "standard"
}

variable "code_engine_project_name" {
  description = "Code Engine project that hosts the API, workers, and jobs."
  type        = string
  default     = "tbcoin-granite-project"
}

variable "watsonx_runtime_name" {
  description = "Optional name for the watsonx.ai runtime service instance."
  type        = string
  default     = "tbcoin-watsonx-runtime"
}

variable "provision_watsonx_runtime" {
  description = "Whether to provision a watsonx.ai runtime/service instance via Terraform."
  type        = bool
  default     = false
}

variable "watsonx_runtime_service" {
  description = "IBM Cloud catalog service name for watsonx.ai runtime in your account."
  type        = string
  default     = "pm-20"
}

variable "watsonx_runtime_plan" {
  description = "Plan for the watsonx.ai runtime service instance."
  type        = string
  default     = "standard"
}
