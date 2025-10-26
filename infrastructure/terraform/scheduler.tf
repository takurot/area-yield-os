# Cloud Scheduler for periodic tasks

# Enable Cloud Scheduler API
resource "google_project_service" "scheduler" {
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

# Monthly data update job
resource "google_cloud_scheduler_job" "monthly_data_update" {
  name             = "monthly-data-update-${var.environment}"
  description      = "Monthly AirDNA and public data update"
  schedule         = "0 2 1 * *" # 1st of month at 2:00 AM
  time_zone        = "Asia/Tokyo"
  attempt_deadline = "1800s" # 30 minutes

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.api.status[0].url}/api/v1/internal/update-data"
    
    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      task = "monthly_update"
    }))

    oidc_token {
      service_account_email = google_service_account.cloud_run.email
    }
  }

  depends_on = [google_project_service.scheduler]
}

# Weekly RAG update job
resource "google_cloud_scheduler_job" "weekly_rag_update" {
  name             = "weekly-rag-update-${var.environment}"
  description      = "Weekly議事録crawl and RAG update"
  schedule         = "0 3 * * 0" # Sunday at 3:00 AM
  time_zone        = "Asia/Tokyo"
  attempt_deadline = "3600s" # 1 hour

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.api.status[0].url}/api/v1/internal/update-rag"
    
    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      task = "rag_update"
    }))

    oidc_token {
      service_account_email = google_service_account.cloud_run.email
    }
  }

  depends_on = [google_project_service.scheduler]
}

