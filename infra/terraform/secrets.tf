# Secrets you set yourself after the first apply (see README.md); they start as "set-me", and
# Terraform never overwrites what you set.
resource "google_secret_manager_secret" "manual" {
  for_each  = toset(["openai-api-key", "redis-url", "resend-api-key", "resend-webhook-secret", "paddle-webhook-secret", "paddle-api-key"])
  secret_id = each.value

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "manual" {
  for_each    = google_secret_manager_secret.manual
  secret      = each.value.id
  secret_data = "set-me"

  lifecycle {
    ignore_changes = [secret_data]
  }
}

# Secrets Terraform makes: each service's own key. Tokens calling a service are signed with its
# key and addressed to it, so a leaked key lets someone call one service, not all of them.
locals {
  keyed_services = ["library", "generation", "rounds", "companies", "billing"]
}

resource "random_password" "service_secret" {
  for_each = toset(local.keyed_services)
  length   = 48
  special  = false
}

resource "google_secret_manager_secret" "service_secret" {
  for_each  = toset(local.keyed_services)
  secret_id = "service-secret-${each.value}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "service_secret" {
  for_each    = toset(local.keyed_services)
  secret      = google_secret_manager_secret.service_secret[each.value].id
  secret_data = random_password.service_secret[each.value].result
}

locals {
  secret_ids = merge(
    { for name, secret in google_secret_manager_secret.manual : name => secret.secret_id },
    { for name in local.keyed_services : "service-secret-${name}" => google_secret_manager_secret.service_secret[name].secret_id },
    { analytics-salt = google_secret_manager_secret.analytics_salt.secret_id },
  )
}
