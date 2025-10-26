# Terraform outputs

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "cloud_run_url" {
  description = "Cloud Run API URL"
  value       = google_cloud_run_service.api.status[0].url
}

output "database_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.main.name
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "bigquery_dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.areayield_mvp.dataset_id
}

output "storage_bucket_raw" {
  description = "Raw data bucket name"
  value       = google_storage_bucket.raw_data.name
}

output "storage_bucket_processed" {
  description = "Processed data bucket name"
  value       = google_storage_bucket.processed_data.name
}

output "redis_host" {
  description = "Redis host"
  value       = google_redis_instance.cache.host
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.cache.port
}

output "cloud_run_service_account" {
  description = "Cloud Run service account email"
  value       = google_service_account.cloud_run.email
}

output "data_pipeline_service_account" {
  description = "Data pipeline service account email"
  value       = google_service_account.data_pipeline.email
}

