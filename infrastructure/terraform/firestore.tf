# Firestore configuration

resource "google_firestore_database" "main" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  # Prevent accidental deletion in production
  lifecycle {
    prevent_destroy = false # Set to true in production
  }
}

# Firestore indexes for common queries
resource "google_firestore_index" "cache_by_key" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "cache"

  fields {
    field_path = "key"
    order      = "ASCENDING"
  }

  fields {
    field_path = "expires_at"
    order      = "ASCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

resource "google_firestore_index" "user_profiles" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "user_profiles"

  fields {
    field_path = "uid"
    order      = "ASCENDING"
  }

  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }

  fields {
    field_path = "__name__"
    order      = "ASCENDING"
  }
}

