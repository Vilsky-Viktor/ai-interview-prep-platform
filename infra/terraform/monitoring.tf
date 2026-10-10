# Outage, error, database and cost alerts, by email to var.alert_email.
#
# Uptime: Google checks the site and each API's /ready through the load balancer every minute,
# from several regions; an alert fires when a check fails from more than one of them.
locals {
  uptime_paths = merge(
    { site = "/" },
    { for name, service in local.public_services : name => "/api/${service.path}/ready" if service.path != null },
  )
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "prepza alerts"
  type         = "email"
  labels       = { email_address = var.alert_email }

  depends_on = [google_project_service.apis]
}

resource "google_monitoring_uptime_check_config" "check" {
  for_each     = local.uptime_paths
  display_name = "prepza ${each.key}"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = each.value
    port         = 443
    use_ssl      = true
    validate_ssl = true

    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }

  monitored_resource {
    type   = "uptime_url"
    labels = { project_id = var.project_id, host = var.domain }
  }

  depends_on = [google_project_service.apis]
}

resource "google_monitoring_alert_policy" "down" {
  for_each     = google_monitoring_uptime_check_config.check
  display_name = "prepza ${each.key} is down"
  combiner     = "OR"

  conditions {
    display_name = "${each.key} fails its uptime check"

    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND metric.label.check_id=\"${each.value.uptime_check_id}\" AND resource.type=\"uptime_url\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 1

      aggregations {
        alignment_period     = "1200s"
        per_series_aligner   = "ALIGN_NEXT_OLDER"
        cross_series_reducer = "REDUCE_COUNT_FALSE"
        group_by_fields      = ["resource.label.*"]
      }
    }
  }

  documentation {
    content   = "https://${var.domain}${local.uptime_paths[each.key]} stopped answering. Check the service's Cloud Run logs and Sentry."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Cost: a monthly budget on the billing account, scoped to this project. Emails at 50%, 90% and
# 100% of it, and when the month's forecast passes it. It only alerts; nothing is stopped.
resource "google_billing_budget" "monthly" {
  billing_account = var.billing_account
  display_name    = "prepza monthly"

  budget_filter {
    projects = ["projects/${data.google_project.this.number}"]
  }

  amount {
    specified_amount {
      units = tostring(var.monthly_budget)
    }
  }

  threshold_rules {
    threshold_percent = 0.5
  }

  threshold_rules {
    threshold_percent = 0.9
  }

  threshold_rules {
    threshold_percent = 1.0
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "FORECASTED_SPEND"
  }

  all_updates_rule {
    monitoring_notification_channels = [google_monitoring_notification_channel.email.id]
    disable_default_iam_recipients   = false
  }

  depends_on = [google_project_service.apis]
}

# Dead letters: an event a consumer kept failing on for hours (pubsub.tf). Fires while any wait
# in the dead-letter subscription; replay them as infra/README.md (Notes) shows.
resource "google_monitoring_alert_policy" "dead_letters" {
  display_name = "prepza events dead-lettered"
  combiner     = "OR"

  conditions {
    display_name = "events-dead-letter has messages"

    condition_threshold {
      filter          = "metric.type=\"pubsub.googleapis.com/subscription/num_undelivered_messages\" AND resource.type=\"pubsub_subscription\" AND resource.label.subscription_id=\"${google_pubsub_subscription.dead_letter.name}\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  documentation {
    content   = "Events failed 50 deliveries and wait in the events-dead-letter subscription. Fix the consumer (Cloud Run logs, Sentry), then replay them as infra/README.md (Notes) shows."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Scheduler: a periodic job (jobs.tf) whose run failed, from Cloud Scheduler's own error logs.
resource "google_monitoring_alert_policy" "scheduler_failed" {
  display_name = "prepza scheduled job failed"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Scheduler logged a failed run"

    condition_matched_log {
      filter = "resource.type=\"cloud_scheduler_job\" AND severity>=ERROR"

      label_extractors = {
        job = "EXTRACT(resource.labels.job_id)"
      }
    }
  }

  alert_strategy {
    notification_rate_limit {
      period = "3600s"
    }

    auto_close = "86400s"
  }

  documentation {
    content   = "A scheduled job failed. Check the job in Cloud Scheduler and its service's Cloud Run logs."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Web hooks refused: Paddle's or Resend's signature check failed (WEBHOOK_SIGNATURE_REFUSED in
# prepza_common/constants.py). Usually a wrong or unset secret: then every payment and email event
# is refused, as 401s the server-error alert doesn't count.
resource "google_monitoring_alert_policy" "webhook_signature_refused" {
  display_name = "prepza web hook signature refused"
  combiner     = "OR"

  conditions {
    display_name = "A provider's web hook failed its signature check"

    condition_matched_log {
      filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.msg:\"web hook signature refused\""

      label_extractors = {
        service = "EXTRACT(resource.labels.service_name)"
      }
    }
  }

  alert_strategy {
    notification_rate_limit {
      period = "3600s"
    }

    auto_close = "86400s"
  }

  documentation {
    content   = "Paddle's or Resend's web hook was refused for its signature. If it keeps happening, the secret is wrong: compare `paddle-webhook-secret` or `resend-webhook-secret` (Secret Manager) with the provider's dashboard, then resend the failed events from there. Paid top-ups get their credits only once it's fixed."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Server errors: a Cloud Run service answering more than 5% of its requests with a 5xx for ten
# minutes.
resource "google_monitoring_alert_policy" "server_errors" {
  display_name = "prepza server errors"
  combiner     = "OR"

  conditions {
    display_name = "5xx share of requests above 5%"

    condition_threshold {
      filter             = "metric.type=\"run.googleapis.com/request_count\" AND resource.type=\"cloud_run_revision\" AND metric.label.response_code_class=\"5xx\""
      denominator_filter = "metric.type=\"run.googleapis.com/request_count\" AND resource.type=\"cloud_run_revision\""
      duration           = "600s"
      comparison         = "COMPARISON_GT"
      threshold_value    = 0.05

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.label.service_name"]
      }

      denominator_aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.label.service_name"]
      }
    }
  }

  documentation {
    content   = "A service answers many requests with server errors. Check its Cloud Run logs and Sentry."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Database connections: open connections past 80% of max_connections (database.tf), the sign to
# raise db_tier before a deploy at peak runs out of them.
resource "google_monitoring_alert_policy" "database_connections" {
  display_name = "prepza database connections high"
  combiner     = "OR"

  conditions {
    display_name = "Postgres connections above 80% of the limit"

    condition_threshold {
      filter          = "metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\" AND resource.type=\"cloudsql_database\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = floor(local.db_max_connections * 0.8)

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_MAX"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.label.database_id"]
      }
    }
  }

  documentation {
    content   = "The database is near its connection limit. Raise db_tier (and db_max_connections) as infra/README.md describes, or lower services' max instances."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Database CPU: busy above 80% for fifteen minutes.
resource "google_monitoring_alert_policy" "database_cpu" {
  display_name = "prepza database CPU high"
  combiner     = "OR"

  conditions {
    display_name = "Cloud SQL CPU above 80%"

    condition_threshold {
      filter          = "metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\" AND resource.type=\"cloudsql_database\""
      duration        = "900s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  documentation {
    content   = "The database has been busy for a while. Check slow queries in Cloud SQL Query Insights, or raise db_tier."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}
