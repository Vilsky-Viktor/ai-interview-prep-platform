resource "google_pubsub_topic" "events" {
  name       = "events"
  depends_on = [google_project_service.apis]
}

# Events a consumer kept failing on; kept 7 days for a look or a replay (the pull subscription
# below; infra/README.md, Notes).
resource "google_pubsub_topic" "dead_letter" {
  name       = "events-dead-letter"
  depends_on = [google_project_service.apis]
}

resource "google_pubsub_subscription" "dead_letter" {
  name                       = "events-dead-letter"
  topic                      = google_pubsub_topic.dead_letter.id
  message_retention_duration = "604800s"
}

# The event types each consumer handles (its app/services/*events*.py and candidate_billing.py).
# A consumer that starts handling a new type needs it added here. Changing a filter replaces the
# subscription, dropping the messages it still holds: apply when its backlog is empty. Funnel
# events go only to BigQuery (analytics.tf).
locals {
  consumes = {
    library       = ["answer.recorded", "session.scored"]
    companies     = ["generation.completed", "generation.cancelled", "interview.finished"]
    notifications = ["notification.requested", "candidate.invited", "candidate.reminded", "report.shared", "contact.sent"]
  }
}

# Each consumer gets its event types pushed to its /internal/events, signed as the invoker.
resource "google_pubsub_subscription" "push" {
  for_each = local.consumes
  name     = "${each.key}-events"
  topic    = google_pubsub_topic.events.id
  filter   = join(" OR ", [for type in each.value : "attributes.type = \"${type}\""])

  ack_deadline_seconds = 60

  push_config {
    push_endpoint = "${local.run_url[each.key]}/internal/events"

    oidc_token {
      service_account_email = google_service_account.invoker.email
      audience              = local.run_url[each.key]
    }
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  # 50 attempts, backing off up to 10 minutes, ride out several hours of downstream trouble
  # before a message is dead-lettered (monitoring.tf alerts on that).
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 50
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
