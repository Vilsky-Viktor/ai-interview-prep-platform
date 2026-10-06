# Outage and cost alerts, by email to var.alert_email.
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
