# GitHub Actions deploys without a stored key: GitHub's signed token for main or a version tag of
# this repository is exchanged for the deploy account's (Workload Identity Federation).
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github"
  display_name              = "GitHub Actions"

  depends_on = [google_project_service.apis]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  display_name                       = "GitHub"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  # Only this repository's main branch (CI pushes images, a manual run rolls back) and its version
  # tags (deploys). Version tags are protected by a ruleset, so only admins can make them.
  attribute_condition = "assertion.repository == '${var.github_repository}' && (assertion.ref == 'refs/heads/main' || assertion.ref.startsWith('refs/tags/v'))"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# What the pipeline acts as: it pushes images, runs migrations and moves services to new images,
# and nothing else; infrastructure changes go through Terraform.
resource "google_service_account" "deploy" {
  account_id   = "prepza-deploy"
  display_name = "GitHub Actions deploys"
}

resource "google_service_account_iam_member" "github_is_deploy" {
  service_account_id = google_service_account.deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
}

resource "google_project_iam_member" "deploy" {
  for_each = toset(["roles/run.developer"])
  project  = var.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.deploy.email}"
}

resource "google_artifact_registry_repository_iam_member" "deploy_pushes" {
  repository = google_artifact_registry_repository.images.name
  location   = var.region
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.deploy.email}"
}

# Each service runs as its own account; deploying one (and running its migrations) means acting
# as it.
resource "google_service_account_iam_member" "deploy_acts_as_service" {
  for_each           = local.services
  service_account_id = google_service_account.service[each.key].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.deploy.email}"
}
