# Alerts counted from the services' own logs (log-based metrics), by email to var.alert_email:
# Redis or OpenAI failing, generation's AI spend running high, generation tasks failing, and
# emails not delivered.

resource "google_logging_metric" "redis_errors" {
  name   = "prepza_redis_errors"
  filter = "resource.type=\"cloud_run_revision\" AND severity>=WARNING AND (jsonPayload.exc:\"redis.exceptions\" OR textPayload:\"redis.exceptions\")"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_logging_metric" "openai_errors" {
  name   = "prepza_openai_errors"
  filter = "resource.type=\"cloud_run_revision\" AND severity>=ERROR AND (jsonPayload.exc:\"openai.\" OR textPayload:\"openai.\")"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

# Each generation run logs what it spent ("Generation <id> (<kind>) spent $1.23; ...").
resource "google_logging_metric" "generation_spend" {
  name            = "prepza_generation_spend"
  filter          = "resource.type=\"cloud_run_revision\" AND jsonPayload.message:\"spent $\""
  value_extractor = "REGEXP_EXTRACT(jsonPayload.message, \"spent \\\\$([0-9.]+)\")"

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "DISTRIBUTION"
    unit        = "USD"
  }

  bucket_options {
    exponential_buckets {
      num_finite_buckets = 20
      growth_factor      = 2
      scale              = 0.01
    }
  }
}

# notifications logs each email Resend reports bounced, suppressed or marked as spam.
resource "google_logging_metric" "emails_undelivered" {
  name   = "prepza_emails_undelivered"
  filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"notifications\" AND jsonPayload.message:\"Email not delivered\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

locals {
  # Each: its metric, the threshold over the window, the window, and what to do.
  log_alerts = {
    redis = {
      name      = "prepza Redis failing"
      condition = "Over 20 Redis errors in 10 minutes"
      filter    = "metric.type=\"logging.googleapis.com/user/${google_logging_metric.redis_errors.name}\" AND resource.type=\"cloud_run_revision\""
      aligner   = "ALIGN_DELTA"
      threshold = 20
      window    = "600s"
      text      = "Services can't reach Redis (Upstash): rate limits, live updates and the pause and maintenance switches fail open or error. Check Upstash's status and the redis-url secret."
    }
    openai = {
      name      = "prepza OpenAI failing"
      condition = "Over 10 OpenAI errors in 15 minutes"
      filter    = "metric.type=\"logging.googleapis.com/user/${google_logging_metric.openai_errors.name}\" AND resource.type=\"cloud_run_revision\""
      aligner   = "ALIGN_DELTA"
      threshold = 10
      window    = "900s"
      text      = "Calls to OpenAI fail: generation, the help chat and the assistant are affected. Check OpenAI's status page, the account's limits and credit, and the openai-api-key secret."
    }
    spend = {
      name      = "prepza AI spend high"
      condition = "Generation spent over var.ai_spend_alert_hourly USD in an hour"
      filter    = "metric.type=\"logging.googleapis.com/user/${google_logging_metric.generation_spend.name}\" AND resource.type=\"cloud_run_revision\""
      # The sum of the logged amounts, a distribution's values.
      aligner   = "ALIGN_SUM"
      threshold = var.ai_spend_alert_hourly
      window    = "3600s"
      text      = "Generation's OpenAI spend in the last hour is above the alert level. Check the generation runs in the logs (each logs what it spent) for a loop or abuse, and the daily caps."
    }
    bounces = {
      name      = "prepza emails bouncing"
      condition = "Over var.email_bounce_alert_hourly emails not delivered in an hour"
      filter    = "metric.type=\"logging.googleapis.com/user/${google_logging_metric.emails_undelivered.name}\" AND resource.type=\"cloud_run_revision\""
      aligner   = "ALIGN_DELTA"
      threshold = var.email_bounce_alert_hourly
      window    = "3600s"
      text      = "Many emails bounce or are marked as spam: Resend may suspend sending. Check Resend's dashboard for the cause (bad addresses from one company, DNS, a spam complaint wave)."
    }
  }
}

resource "google_monitoring_alert_policy" "logs" {
  for_each     = local.log_alerts
  display_name = each.value.name
  combiner     = "OR"

  conditions {
    display_name = each.value.condition

    condition_threshold {
      filter          = each.value.filter
      comparison      = "COMPARISON_GT"
      threshold_value = each.value.threshold
      duration        = "0s"

      aggregations {
        alignment_period     = each.value.window
        per_series_aligner   = each.value.aligner
        cross_series_reducer = "REDUCE_SUM"
      }

      trigger {
        count = 1
      }
    }
  }

  alert_strategy {
    auto_close = "86400s"
  }

  documentation {
    content   = each.value.text
    mime_type = "text/markdown"
  }

  notification_channels = local.alert_channels
}

# Generation tasks: a task's attempt that fails is retried, and dropped after its last; many
# failing attempts mean runs are being lost.
resource "google_monitoring_alert_policy" "tasks_failing" {
  display_name = "prepza generation tasks failing"
  combiner     = "OR"

  conditions {
    display_name = "Over 20% of generation task attempts failed for 30 minutes"

    condition_threshold {
      filter             = "metric.type=\"cloudtasks.googleapis.com/queue/task_attempt_count\" AND resource.type=\"cloud_tasks_queue\" AND metric.label.response_code!=\"OK\""
      denominator_filter = "metric.type=\"cloudtasks.googleapis.com/queue/task_attempt_count\" AND resource.type=\"cloud_tasks_queue\""
      comparison         = "COMPARISON_GT"
      threshold_value    = 0.2
      duration           = "1800s"

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_SUM"
      }

      denominator_aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  alert_strategy {
    auto_close = "86400s"
  }

  documentation {
    content   = "Many generation task attempts fail; after their last attempt Cloud Tasks drops them and the interviews stay ungenerated. Check generation-worker's Cloud Run logs and Sentry, and the generation queue in Cloud Tasks."
    mime_type = "text/markdown"
  }

  notification_channels = local.alert_channels
}
