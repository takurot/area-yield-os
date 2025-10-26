# Cloud SQL PostgreSQL instance

resource "google_sql_database_instance" "main" {
  name             = "areayield-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.database_tier

    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      point_in_time_recovery_enabled = true
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "allow-all" # TODO: Restrict in production
        value = "0.0.0.0/0"
      }
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = var.environment == "production" ? true : false
}

resource "google_sql_database" "areayield" {
  name     = "areayield"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "default" {
  name     = "areayield"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database URL in Secret Manager
resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url-${var.environment}"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "database_url" {
  secret = google_secret_manager_secret.database_url.id
  secret_data = "postgresql://${google_sql_user.default.name}:${google_sql_user.default.password}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.areayield.name}"
}

