# Backlog alerts, by email like the others (monitoring.tf): work that waits too long to be done.

# Events: a consumer's push subscription (pubsub.tf) holding an event unhandled for 15 minutes,
# long before it would be dead-lettered.
resource "google_monitoring_alert_policy" "events_waiting" {
  display_name = "prepza events waiting"
  combiner     = "OR"

  conditions {
    display_name = "An event waits unhandled for over 15 minutes"

    condition_threshold {
      filter          = "metric.type=\"pubsub.googleapis.com/subscription/oldest_unacked_message_age\" AND resource.type=\"pubsub_subscription\" AND resource.label.subscription_id = one_of(${join(", ", [for subscription in google_pubsub_subscription.push : "\"${subscription.name}\""])})"
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = 900

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_MAX"
        cross_series_reducer = "REDUCE_MAX"
        group_by_fields      = ["resource.label.subscription_id"]
      }
    }
  }

  documentation {
    content   = "A consumer hasn't handled an event for over 15 minutes; Pub/Sub keeps retrying it. Check the consumer's Cloud Run logs and Sentry (the subscription is named <service>-events)."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Generation jobs: more than 50 tasks in the Cloud Tasks queue (jobs.tf) for 15 minutes, so the
# worker isn't keeping up or keeps failing them.
resource "google_monitoring_alert_policy" "tasks_waiting" {
  display_name = "prepza generation queue backed up"
  combiner     = "OR"

  conditions {
    display_name = "Over 50 generation tasks queued for 15 minutes"

    condition_threshold {
      filter          = "metric.type=\"cloudtasks.googleapis.com/queue/depth\" AND resource.type=\"cloud_tasks_queue\" AND resource.label.queue_id=\"${google_cloud_tasks_queue.generation.name}\""
      duration        = "900s"
      comparison      = "COMPARISON_GT"
      threshold_value = 50

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  documentation {
    content   = "Generation jobs pile up in the Cloud Tasks queue. Check the generation-worker's Cloud Run logs and Sentry, and its instance limit (locals.tf)."
    mime_type = "text/markdown"
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}
