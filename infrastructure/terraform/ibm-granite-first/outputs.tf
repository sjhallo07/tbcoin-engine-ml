output "resource_group_id" {
  description = "IBM Cloud resource group ID."
  value       = ibm_resource_group.this.id
}

output "code_engine_project_name" {
  description = "Provisioned Code Engine project name."
  value       = ibm_code_engine_project.this.name
}

output "cos_instance_guid" {
  description = "GUID for the Cloud Object Storage instance."
  value       = ibm_resource_instance.cos.guid
}

output "cos_bucket_name" {
  description = "Bucket for artifacts and prompts."
  value       = ibm_cos_bucket.artifacts.bucket_name
}

output "postgresql_instance_id" {
  description = "Resource ID for PostgreSQL."
  value       = ibm_resource_instance.postgresql.id
}

output "redis_instance_id" {
  description = "Resource ID for Redis."
  value       = ibm_resource_instance.redis.id
}

output "watsonx_runtime_id" {
  description = "Optional watsonx.ai runtime resource ID."
  value       = try(ibm_resource_instance.watsonx_runtime[0].id, null)
}
