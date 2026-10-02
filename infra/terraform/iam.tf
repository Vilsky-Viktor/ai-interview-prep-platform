# What every service runs as: it reads its secrets, connects to Cloud SQL, publishes events and
# queues tasks.
resource "google_service_account" "runtime" {
  account_id   = "prepza-runtime"
  display_name = "prepza services"
}

# What Google signs as when it calls our services: Pub/Sub pushes, Cloud Tasks, Cloud Scheduler.
# Services admit only its tokens on /internal/events, /internal/jobs and /internal/schedules.
resource "google_service_account" "invoker" {
  account_id   = "prepza-invoker"
  display_name = "Pub/Sub, Cloud Tasks and Scheduler calling prepza"
}

resource "google_project_iam_member" "runtime" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/cloudtasks.enqueuer",
    "roles/pubsub.publisher",
    "roles/secretmanager.secretAccessor",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

# Creating a Cloud Task that carries the invoker's token requires acting as the invoker.
resource "google_service_account_iam_member" "runtime_acts_as_invoker" {
  service_account_id = google_service_account.invoker.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.runtime.email}"
}

# Pub/Sub signs push requests as the invoker.
resource "google_service_account_iam_member" "pubsub_signs_as_invoker" {
  service_account_id = google_service_account.invoker.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:service-${data.google_project.this.number}@gcp-sa-pubsub.iam.gserviceaccount.com"

  depends_on = [google_project_service.apis]
}
