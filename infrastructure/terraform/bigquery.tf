# BigQuery dataset and tables

resource "google_bigquery_dataset" "areayield_mvp" {
  dataset_id                  = "areayield_mvp_${var.environment}"
  friendly_name               = "AreaYield MVP Dataset"
  description                 = "Main dataset for AreaYield analytics and aggregations"
  location                    = var.region
  default_table_expiration_ms = null

  labels = {
    environment = var.environment
    project     = "areayield"
  }
}

# Area statistics table
resource "google_bigquery_table" "area_stats" {
  dataset_id = google_bigquery_dataset.areayield_mvp.dataset_id
  table_id   = "area_stats"

  schema = jsonencode([
    {
      name        = "area_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Unique identifier for the area"
    },
    {
      name        = "prefecture"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Prefecture name"
    },
    {
      name        = "city"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "City name"
    },
    {
      name        = "district"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "District/town name"
    },
    {
      name        = "avg_revpar"
      type        = "FLOAT"
      mode        = "NULLABLE"
      description = "Average RevPAR"
    },
    {
      name        = "total_listings"
      type        = "INTEGER"
      mode        = "NULLABLE"
      description = "Total number of listings"
    },
    {
      name        = "occupancy_rate"
      type        = "FLOAT"
      mode        = "NULLABLE"
      description = "Average occupancy rate"
    },
    {
      name        = "collected_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Data collection timestamp"
    }
  ])

  time_partitioning {
    type  = "DAY"
    field = "collected_at"
  }

  clustering = ["prefecture", "city"]
}

# Analysis results table
resource "google_bigquery_table" "analysis_results" {
  dataset_id = google_bigquery_dataset.areayield_mvp.dataset_id
  table_id   = "analysis_results"

  schema = jsonencode([
    {
      name        = "analysis_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Unique analysis identifier"
    },
    {
      name        = "user_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "User identifier"
    },
    {
      name        = "address"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Analyzed address"
    },
    {
      name        = "judgment"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Go/Amber/Stop judgment"
    },
    {
      name        = "score"
      type        = "FLOAT"
      mode        = "REQUIRED"
      description = "Overall score"
    },
    {
      name        = "profitability_score"
      type        = "FLOAT"
      mode        = "NULLABLE"
      description = "Profitability score"
    },
    {
      name        = "licensing_score"
      type        = "FLOAT"
      mode        = "NULLABLE"
      description = "Licensing feasibility score"
    },
    {
      name        = "regulation_risk_score"
      type        = "FLOAT"
      mode        = "NULLABLE"
      description = "Regulation risk score"
    },
    {
      name        = "analyzed_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Analysis timestamp"
    }
  ])

  time_partitioning {
    type  = "DAY"
    field = "analyzed_at"
  }

  clustering = ["user_id", "judgment"]
}

