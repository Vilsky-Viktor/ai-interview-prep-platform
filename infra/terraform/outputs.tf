output "site_ip" {
  description = "Add an A record for the domain pointing here (GoDaddy); the certificate follows."
  value       = google_compute_global_address.site.address
}

output "registry" {
  description = "Where the deploy pipeline pushes images."
  value       = local.registry
}

output "service_urls" {
  value = local.run_url
}

output "runtime_service_account" {
  value = google_service_account.runtime.email
}

output "github_variables" {
  description = "Repository variables for the deploy workflow (Settings → Secrets and variables → Actions → Variables)."
  value = {
    GCP_PROJECT_ID                 = var.project_id
    GCP_REGION                     = var.region
    GCP_WORKLOAD_IDENTITY_PROVIDER = google_iam_workload_identity_pool_provider.github.name
    GCP_DEPLOY_SERVICE_ACCOUNT     = google_service_account.deploy.email
    SITE_URL                       = "https://${var.domain}"
  }
}
