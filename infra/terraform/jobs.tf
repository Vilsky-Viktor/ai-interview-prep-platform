# Generation jobs: one task runs one generation on the worker. No retries: a failure is saved on
# the generation for the user to retry, so a generation never runs twice.
resource "google_cloud_tasks_queue" "generation" {
  name     = "generation"
  location = var.region

  rate_limits {
    max_concurrent_dispatches = 20
    max_dispatches_per_second = 5
  }

  retry_config {
    max_attempts = 1
  }

  depends_on = [google_project_service.apis]
}

# Periodic work, as scripts/crontab does locally (UTC).
locals {
  schedules = {
    sweep                = { service = "generation-worker", path = "/internal/schedules/sweep", cron = "*/5 * * * *" }
    key-check-batches    = { service = "generation-worker", path = "/internal/schedules/key-check-batches", cron = "*/10 * * * *" }
    generation-retention = { service = "generation-worker", path = "/internal/schedules/retention", cron = "0 3 * * *" }
    candidate-retention  = { service = "companies", path = "/internal/schedules/retention", cron = "15 3 * * *" }
    # Events not published right after their change (the outbox).
    library-outbox    = { service = "library", path = "/internal/schedules/outbox", cron = "* * * * *" }
    companies-outbox  = { service = "companies", path = "/internal/schedules/outbox", cron = "* * * * *" }
    rounds-outbox     = { service = "rounds", path = "/internal/schedules/outbox", cron = "* * * * *" }
    generation-outbox = { service = "generation-worker", path = "/internal/schedules/outbox", cron = "* * * * *" }
  }
}

resource "google_cloud_scheduler_job" "schedule" {
  for_each         = local.schedules
  name             = each.key
  region           = var.region
  schedule         = each.value.cron
  time_zone        = "Etc/UTC"
  attempt_deadline = "600s"

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
