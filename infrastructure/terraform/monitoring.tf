# Cloud Monitoring configuration

# Alert policy for API errors
resource "google_monitoring_alert_policy" "api_error_rate" {
  display_name = "High API Error Rate - ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 5%"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
      duration        = "300s" # 5 minutes
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = []

  documentation {
    content = "API error rate exceeded 5% for 5 minutes in ${var.environment}"
  }
}

# Alert policy for high latency
resource "google_monitoring_alert_policy" "api_latency" {
  display_name = "High API Latency - ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "P95 latency > 10 seconds"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10000 # 10 seconds in milliseconds

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_95"
      }
    }
  }

  notification_channels = []

  documentation {
    content = "API P95 latency exceeded 10 seconds for 5 minutes in ${var.environment}"
  }
}

# Alert policy for Cloud SQL connections
resource "google_monitoring_alert_policy" "db_connections" {
  display_name = "High Database Connection Usage - ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "Connection usage > 80%"

    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 80

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = []

  documentation {
    content = "Database connection usage exceeded 80% for 5 minutes in ${var.environment}"
  }
}

