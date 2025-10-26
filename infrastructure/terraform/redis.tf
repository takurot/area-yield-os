# Cloud Memorystore (Redis) instance

resource "google_redis_instance" "cache" {
  name           = "areayield-redis-${var.environment}"
  tier           = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = var.redis_memory_size_gb
  region         = var.region

  redis_version = "REDIS_7_0"

  display_name = "AreaYield Cache ${var.environment}"

  authorized_network = "default" # TODO: Use VPC

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }
}

# Store Redis URL in Secret Manager
resource "google_secret_manager_secret" "redis_url" {
  secret_id = "redis-url-${var.environment}"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "redis_url" {
  secret      = google_secret_manager_secret.redis_url.id
  secret_data = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
}

output "redis_host" {
  value = google_redis_instance.cache.host
}

output "redis_port" {
  value = google_redis_instance.cache.port
}

