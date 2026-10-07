# Generation jobs: one task runs one generation on the worker. A delivery that fails before the
# job starts (a worker restarting) is tried again; a started generation is claimed once, so a
# repeated delivery does nothing (services/generation/app/services/jobs.py).
resource "google_cloud_tasks_queue" "generation" {
  name     = "generation"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = 20
    max_dispatches_per_second = 5
  }

  retry_config {
    max_attempts  = 3
    min_backoff   = "10s"
    max_backoff   = "120s"
    max_doublings = 3
  }

  depends_on = [google_project_service.apis]
}

# Periodic work, as scripts/local/crontab does locally (UTC).
locals {
  schedules = {
    sweep                = { service = "generation-worker", path = "/internal/schedules/sweep", cron = "*/5 * * * *" }
    key-check-batches    = { service = "generation-worker", path = "/internal/schedules/key-check-batches", cron = "*/10 * * * *" }
    generation-retention = { service = "generation-worker", path = "/internal/schedules/retention", cron = "0 3 * * *" }
    candidate-retention  = { service = "companies", path = "/internal/schedules/retention", cron = "15 3 * * *" }
    invite-expiry        = { service = "companies", path = "/internal/schedules/invite-expiry", cron = "30 3 * * *" }
    # In the morning (UTC), not the night: a reminder candidates see.
    invite-reminders = { service = "companies", path = "/internal/schedules/invite-reminders", cron = "0 9 * * *" }
    bank-stages      = { service = "library", path = "/internal/schedules/bank", cron = "45 3 * * *" }
    # ATS candidates whose invite stalled, and ones past their retention.
    ats-recover      = { service = "ats", path = "/internal/schedules/recover", cron = "0 4 * * *" }
    # Events not published right after their change (the outbox).
    library-outbox    = { service = "library", path = "/internal/schedules/outbox", cron = "* * * * *" }
    companies-outbox  = { service = "companies", path = "/internal/schedules/outbox", cron = "* * * * *" }
    rounds-outbox     = { service = "rounds", path = "/internal/schedules/outbox", cron = "* * * * *" }
    generation-outbox = { service = "generation-worker", path = "/internal/schedules/outbox", cron = "* * * * *" }
    ats-outbox        = { service = "ats", path = "/internal/schedules/outbox", cron = "* * * * *" }
    # Interviews whose time ran out after the candidate left.
    interview-expiry = { service = "rounds", path = "/internal/schedules/expire-interviews", cron = "* * * * *" }
  }
}

resource "google_cloud_scheduler_job" "schedule" {
  for_each         = local.schedules
  name             = each.key
  region           = var.region
  schedule         = each.value.cron
  time_zone        = "Etc/UTC"
  # As long as the service lets the request run (Scheduler allows 15s to 30 minutes): waiting
  # longer only delays the retry. A retry may still overlap a run Cloud Run cut off, so each job
  # is safe to run twice at once (invite expiry re-checks before holding credits again).
  attempt_deadline = "${max(15, min(local.services[each.value.service].timeout, 1800))}s"

  # The daily jobs retry a failed run; the frequent ones (cron starting with "*") just run again
  # soon.
  dynamic "retry_config" {
    for_each = startswith(each.value.cron, "*") ? [] : [1]

    content {
      retry_count          = 3
      min_backoff_duration = "60s"
      max_backoff_duration = "600s"
    }
  }

  http_target {
    http_method = "POST"
    uri         = "${local.run_url[each.value.service]}${each.value.path}"

    oidc_token {
      service_account_email = google_service_account.invoker.email
      audience              = local.run_url[each.value.service]
    }
  }

  depends_on = [google_project_service.apis]
}
