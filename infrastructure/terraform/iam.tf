# IAM configuration

# Service account for Cloud Run
resource "google_service_account" "cloud_run" {
  account_id   = "areayield-cloud-run-${var.environment}"
  display_name = "AreaYield Cloud Run Service Account"
  description  = "Service account for Cloud Run API service"
}

# Grant Cloud Run service account access to resources
resource "google_project_iam_member" "cloud_run_cloud_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Service account for data pipeline
resource "google_service_account" "data_pipeline" {
  account_id   = "areayield-pipeline-${var.environment}"
  display_name = "AreaYield Data Pipeline Service Account"
  description  = "Service account for data pipeline operations"
}

resource "google_project_iam_member" "pipeline_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.data_pipeline.email}"
}

resource "google_project_iam_member" "pipeline_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.data_pipeline.email}"
}

