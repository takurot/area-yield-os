# API Gateway configuration

# Enable required APIs
resource "google_project_service" "api_gateway" {
  service            = "apigateway.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "service_control" {
  service            = "servicecontrol.googleapis.com"
  disable_on_destroy = false
}

# API Gateway API
resource "google_api_gateway_api" "areayield_api" {
  provider     = google
  api_id       = "areayield-api-${var.environment}"
  display_name = "AreaYield API ${var.environment}"
  
  depends_on = [google_project_service.api_gateway]
}

# API Gateway API Config
resource "google_api_gateway_api_config" "areayield_api_config" {
  provider      = google
  api           = google_api_gateway_api.areayield_api.api_id
  api_config_id = "config-${var.environment}"

  openapi_documents {
    document {
      path = "openapi.yaml"
      contents = base64encode(templatefile("${path.module}/openapi.yaml", {
        backend_url = google_cloud_run_service.api.status[0].url
      }))
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Gateway
resource "google_api_gateway_gateway" "areayield_gateway" {
  provider   = google
  gateway_id = "areayield-gateway-${var.environment}"
  api_config = google_api_gateway_api_config.areayield_api_config.id
  region     = var.region

  display_name = "AreaYield API Gateway ${var.environment}"

  depends_on = [google_api_gateway_api_config.areayield_api_config]
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = google_api_gateway_gateway.areayield_gateway.default_hostname
}

