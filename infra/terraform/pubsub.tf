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

# The event types each consumer handles (its app/services/*events*.py, candidate_billing.py and
# candidate_results.py). A consumer that starts handling a new type needs it added here. Changing
# a filter replaces the subscription, dropping the messages it still holds: apply when its backlog
# is empty. Funnel events go only to BigQuery (analytics.tf).
# Pub/Sub caps a filter at 256 bytes: each type adds 24 bytes plus its name. A type ending in ".*"
# matches every type with that prefix (hasPrefix): notifications takes all "candidate." events
# that way, and ats all "interview." ones (241 bytes; listing them, 277), as listing them one by
# one outgrew the cap; each ignores the ones it doesn't handle. notifications' filter is 236
# bytes, api's 119, the assistant's 35. A new consumer's subscription is created on apply and
# gets only the events published after that.
locals {
  consumes = {
    library       = ["answer.recorded", "session.scored"]
    companies     = ["generation.completed", "generation.failed", "generation.cancelled", "interview.finished", "results.rescored"]
    notifications = ["notification.requested", "candidate.*", "member.invited", "report.shared", "contact.sent", "company.deleted"]
    ats           = ["candidate.finished", "candidate.rescored", "candidate.removed", "interview.*", "company.deleted", "credits.added"]
    api           = ["candidate.finished", "candidate.rescored", "company.deleted"]
    assistant     = ["company.deleted"]
  }
}

# Each consumer gets its event types pushed to its /internal/events, signed as the invoker.
resource "google_pubsub_subscription" "push" {
  for_each = local.consumes
  name     = "${each.key}-events"
  topic    = google_pubsub_topic.events.id
  filter = join(" OR ", [
    for type in each.value : endswith(type, ".*")
    ? "hasPrefix(attributes.type, \"${trimsuffix(type, "*")}\")"
    : "attributes.type = \"${type}\""
  ])

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
