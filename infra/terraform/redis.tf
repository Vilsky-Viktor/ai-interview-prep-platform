# Redis for rate limits, the LLM limiter, the draft cache, live notifications and the pause and
# maintenance switches: Memorystore, in prepza's region and on its private network, so Google
# Cloud is the only provider that holds it. Basic tier: everything here is short-lived; an
# hourly snapshot brings it back after a restart (Google's maintenance), so the switches keep
# their state, and the services treat an empty Redis as limits reset and the switches off. No
# public address; AUTH is required. Traffic stays on Google's private network, encrypted and
# authenticated by Google, so no TLS on this hop.
resource "google_redis_instance" "main" {
  name                    = "prepza"
  region                  = var.region
  tier                    = "BASIC"
  memory_size_gb          = 1
  redis_version           = "REDIS_7_2"
  authorized_network      = google_compute_network.main.id
  connect_mode            = "DIRECT_PEERING"
  auth_enabled            = true
  transit_encryption_mode = "DISABLED"

  persistence_config {
    persistence_mode    = "RDB"
    rdb_snapshot_period = "ONE_HOUR"
  }

  # Updates restart a Basic instance: early on Sunday, when the fewest candidates take tests.
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"

      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# The services' REDIS_URL, made from the instance's address and AUTH string.
resource "google_secret_manager_secret" "redis_url" {
  secret_id = "redis-url"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "redis_url" {
  secret      = google_secret_manager_secret.redis_url.id
  secret_data = "redis://:${google_redis_instance.main.auth_string}@${google_redis_instance.main.host}:${google_redis_instance.main.port}/0"
}
