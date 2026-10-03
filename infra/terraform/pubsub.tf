resource "google_pubsub_topic" "events" {
  name       = "events"
  depends_on = [google_project_service.apis]
}

# Events a consumer kept failing on; kept 7 days for a look (the pull subscription below).
resource "google_pubsub_topic" "dead_letter" {
  name       = "events-dead-letter"
  depends_on = [google_project_service.apis]
}

resource "google_pubsub_subscription" "dead_letter" {
  name                       = "events-dead-letter"
  topic                      = google_pubsub_topic.dead_letter.id
  message_retention_duration = "604800s"
}

# Each consumer gets every domain event pushed to its /internal/events, signed as the invoker;
# it ignores the types that aren't its own. Funnel events go only to BigQuery (analytics.tf).
resource "google_pubsub_subscription" "push" {
  for_each = toset(["library", "companies", "notifications"])
  name     = "${each.value}-events"
  topic    = google_pubsub_topic.events.id
  filter   = "NOT hasPrefix(attributes.type, \"${local.funnel_prefix}\")"

  ack_deadline_seconds = 60

  push_config {
    push_endpoint = "${local.run_url[each.value]}/internal/events"

    oidc_token {
      service_account_email = google_service_account.invoker.email
      audience              = local.run_url[each.value]
    }
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }

  expiration_policy {
    ttl = ""
  }
}

# Pub/Sub moves dead letters itself: it publishes to the dead-letter topic and acknowledges the
# original.
locals {
  pubsub_agent = "serviceAccount:service-${data.google_project.this.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_pubsub_topic_iam_member" "dead_letter_publisher" {
  topic  = google_pubsub_topic.dead_letter.id
  role   = "roles/pubsub.publisher"
  member = local.pubsub_agent
}

resource "google_pubsub_subscription_iam_member" "dead_letter_subscriber" {
  for_each     = google_pubsub_subscription.push
  subscription = each.value.id
  role         = "roles/pubsub.subscriber"
  member       = local.pubsub_agent
}
